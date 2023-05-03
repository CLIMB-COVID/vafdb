from celery import shared_task
from django.conf import settings
from django.db import transaction
from .models import Project, Reference, VAF
from .serializers import MetadataSerializer
import maptide
import time
import math


def entropy(probabilities, normalised=False):
    ent = sum([-(x * math.log2(x)) if x != 0 else 0 for x in probabilities])

    if normalised:
        return ent / math.log2(len(probabilities))
    else:
        return ent


def get_stats(counts, decimals=3):
    coverage = sum(counts)
    probabilities = [count / coverage if coverage > 0 else 0.0 for count in counts]
    percentages = [100 * probability for probability in probabilities]
    ent = entropy(probabilities, normalised=True)
    secondary_count = list(counts)
    secondary_count.pop(counts.index(max(counts)))
    secondary_coverage = sum(secondary_count)
    secondary_probabilities = [
        count / secondary_coverage if secondary_coverage > 0 else 0.0
        for count in secondary_count
    ]
    secondary_ent = entropy(secondary_probabilities, normalised=True)
    return (
        [coverage]
        + counts
        + [round(x, decimals) for x in percentages + [ent, secondary_ent]]
    )


def iterate(data, region=None, stats=False, decimals=3):
    if region:
        chrom, start, end = maptide.parse_region(region)
        for (pos, ins_pos), row in sorted(data[chrom].items()):
            if (not start or pos >= start) and (not end or pos <= end):
                if stats:
                    yield [chrom, pos, ins_pos] + get_stats(row, decimals=decimals)
                else:
                    yield [chrom, pos, ins_pos, sum(row)] + row
    else:
        for chrom, chrom_data in data.items():
            for (pos, ins_pos), row in sorted(chrom_data.items()):
                if stats:
                    yield [chrom, pos, ins_pos] + get_stats(row, decimals=decimals)
                else:
                    yield [chrom, pos, ins_pos, sum(row)] + row


@shared_task
def generate(code, metadata):
    start = time.time()

    # Get the project
    project = Project.objects.get(code=code)

    # Run maptide
    mp = maptide.query(
        metadata["bam_path"],
        region=project.region,
        bai=metadata.get("bai_path"),
        mapping_quality=project.mapping_quality,
        base_quality=project.base_quality,
        indexed=True if metadata.get("bai_path") else False,
    )

    # Maptide output columns
    columns = [
        "reference",
        "position",
        "insertion",
        "coverage",
        "a",
        "c",
        "g",
        "t",
        "ds",
        "n",
        "pc_a",
        "pc_c",
        "pc_g",
        "pc_t",
        "pc_ds",
        "pc_n",
        "entropy",
        "secondary_entropy",
    ]

    references = {}
    vafs = []
    num_vafs = 0

    # Create VAF instances
    for record in iterate(mp, region=project.region, stats=True):
        record = dict(zip(columns, record))

        if (not project.insertions) and record["insertion"] != 0:
            continue

        if (
            record["coverage"] < project.min_coverage
            or record["entropy"] < project.min_entropy
            or record["secondary_entropy"] < project.min_secondary_entropy
        ):
            continue

        base_counts = {
            "A": record["a"],
            "C": record["c"],
            "G": record["g"],
            "T": record["t"],
            "DS": record["ds"],
        }
        if record["coverage"] > 0:
            record["base"] = max(
                base_counts,
                key=base_counts.get,  # type: ignore
            )
            record["confidence"] = (
                100 * base_counts[record["base"]] / sum(base_counts.values())
            )
        else:
            record["base"] = None
            record["confidence"] = 0

        if record["reference"] not in references:
            references[record["reference"]] = Reference.objects.get(
                project=project, name=record["reference"]
            )

        ref_base = references[record["reference"]].sequence[record["position"] - 1]
        diff = record["base"] and record["base"] != ref_base

        if (project.diff_confidence is not None) and not (
            diff and record["confidence"] >= project.diff_confidence
        ):
            continue

        vafs.append(
            {
                "reference": record["reference"],
                "position": record["position"],
                "insertion": record["insertion"],
                "ptype": "REF" if record["insertion"] == 0 else "INS",
                "coverage": record["coverage"],
                "ref_base": ref_base,
                "base": record["base"],
                "confidence": round(
                    record["confidence"], settings.FLOATFIELD_DECIMAL_PLACES
                ),
                "diff": diff,
                "a": record["a"],
                "c": record["c"],
                "g": record["g"],
                "t": record["t"],
                "ds": record["ds"],
                "pc_a": round(record["pc_a"], settings.FLOATFIELD_DECIMAL_PLACES),
                "pc_c": round(record["pc_c"], settings.FLOATFIELD_DECIMAL_PLACES),
                "pc_g": round(record["pc_g"], settings.FLOATFIELD_DECIMAL_PLACES),
                "pc_t": round(record["pc_t"], settings.FLOATFIELD_DECIMAL_PLACES),
                "pc_ds": round(record["pc_ds"], settings.FLOATFIELD_DECIMAL_PLACES),
                "entropy": round(record["entropy"], settings.FLOATFIELD_DECIMAL_PLACES),
                "secondary_entropy": round(
                    record["secondary_entropy"], settings.FLOATFIELD_DECIMAL_PLACES
                ),
            }
        )
        num_vafs += 1

    end = time.time()

    print(
        f"[GENERATE] [SAMPLE_ID] {metadata['sample_id']} [SUCCESS] time: {round(end - start, settings.FLOATFIELD_DECIMAL_PLACES)} s"
    )
    return metadata, vafs, num_vafs, None, None, None, None


@shared_task
def store(args):
    metadata, vafs, num_vafs, num_reads, mean_coverage, mean_entropy, references = args
    start = time.time()

    # Validate the metadata (again because we cant pass the object to the task) before doing anything else
    serializer = MetadataSerializer(data=metadata)  # type: ignore
    serializer.is_valid(raise_exception=True)

    # All changes to the db for this task are wrapped in a single transaction
    # So if anything goes wrong, any changes made are rolled back
    with transaction.atomic():
        # Create Metadata instance
        instance = serializer.save()

        # Create VAF instances
        for vaf in vafs:
            VAF.objects.create(metadata=instance, **vaf)

        # Update Metadata instance with VAF summary statistics
        # instance.num_reads = sum(bc.read_counts.values())
        # instance.mean_coverage = bc.mean_coverage()
        instance.num_vafs = num_vafs
        # instance.mean_entropy = bc.mean_entropy()
        # instance.references = ",".join(bc.references)
        instance.save(
            update_fields=[
                "num_reads",
                "mean_coverage",
                "num_vafs",
                "mean_entropy",
                "references",
            ]
        )
    end = time.time()

    print(
        f"[STORE] [SAMPLE_ID] {metadata['sample_id']} [SUCCESS] time: {round(end - start, settings.FLOATFIELD_DECIMAL_PLACES)} s"
    )
