from celery import shared_task
from django.conf import settings
from django.db import transaction
from .models import VAF
from .serializers import MetadataSerializer
import basecount
import time


@shared_task
def create(**metadata):
    try:
        # Validate the metadata before doing anything else
        serializer = MetadataSerializer(data=metadata)  # type: ignore
        serializer.is_valid(raise_exception=True)

        # Run basecount
        b_start = time.time()
        bc = basecount.BaseCount(
            metadata["bam_path"],
            min_base_quality=settings.MIN_BASE_QUALITY,
            min_mapping_quality=settings.MIN_MAPPING_QUALITY,
        )
        b_end = time.time()

        # All changes to the db for this task are wrapped in a single transaction
        # So if anything goes wrong, any changes made are rolled back
        t_start = time.time()
        with transaction.atomic():
            # Create Metadata instance
            instance = serializer.save()

            # Create VAF instances
            num_vafs = 0
            for record in bc.records():
                vaf = {
                    "reference": record["reference"],
                    "position": record["position"],
                    "coverage": record["coverage"],
                    "num_a": record["num_a"],
                    "num_c": record["num_c"],
                    "num_g": record["num_g"],
                    "num_t": record["num_t"],
                    "num_ds": record["num_ds"],
                    "pc_a": round(record["pc_a"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "pc_c": round(record["pc_c"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "pc_g": round(record["pc_g"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "pc_t": round(record["pc_t"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "pc_ds": round(record["pc_ds"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "entropy": round(
                        record["entropy"], settings.FLOATFIELD_DECIMAL_PLACES
                    ),
                    "secondary_entropy": round(
                        record["secondary_entropy"], settings.FLOATFIELD_DECIMAL_PLACES
                    ),
                }
                VAF.objects.create(metadata=instance, **vaf)
                num_vafs += 1

            # Update Metadata instance with VAF summary statistics
            instance.num_reads = bc.num_reads()
            instance.mean_coverage = round(
                bc.mean_coverage(), settings.FLOATFIELD_DECIMAL_PLACES
            )
            instance.num_vafs = num_vafs
            instance.mean_entropy = round(
                bc.mean_entropy(), settings.FLOATFIELD_DECIMAL_PLACES
            )
            instance.references = ",".join(bc.references)
            instance.save(
                update_fields=[
                    "num_reads",
                    "mean_coverage",
                    "num_vafs",
                    "mean_entropy",
                    "references",
                ]
            )
        t_end = time.time()

        print(
            f"[SAMPLE_ID] {metadata['sample_id']} [TIME] basecount: {round(b_end - b_start, settings.FLOATFIELD_DECIMAL_PLACES)} s"
        )
        print(
            f"[SAMPLE_ID] {metadata['sample_id']} [TIME] transaction: {round(t_end - t_start, settings.FLOATFIELD_DECIMAL_PLACES)} s"
        )

    except Exception as e:
        # Print the sample_id (if there is one) alongside the exception
        msg = f"sample_id: {metadata.get('sample_id')}"
        raise Exception(msg) from e
