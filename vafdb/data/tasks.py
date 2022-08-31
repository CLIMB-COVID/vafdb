from celery import shared_task
from django.conf import settings
from django.db import transaction
from .models import Metadata, VAF
import basecount


@shared_task
def create_vafs(metadata_id):
    metadata = Metadata.objects.get(id=metadata_id)
    try:
        with transaction.atomic():
            bc = basecount.BaseCount(
                metadata.bam_path, 
                min_base_quality=10, 
                min_mapping_quality=10
            )
            num_vafs = 0
            for record in bc.records():
                vaf = {
                    "reference" : record["reference"],
                    "position" : record["position"],
                    "coverage" : record["coverage"],
                    "num_a" : record["num_a"],
                    "num_c" : record["num_c"],
                    "num_g" : record["num_g"],
                    "num_t" : record["num_t"],
                    "num_ds" : record["num_ds"],
                    "pc_a" : record["pc_a"],
                    "pc_c" : record["pc_c"],
                    "pc_g" : record["pc_g"],
                    "pc_t" : record["pc_t"],
                    "pc_ds" : record["pc_ds"],
                    "entropy" : round(record["entropy"], settings.FLOATFIELD_DECIMAL_PLACES),
                    "secondary_entropy" : round(record["secondary_entropy"], settings.FLOATFIELD_DECIMAL_PLACES)
                }
                VAF.objects.create(metadata=metadata, **vaf)
                num_vafs += 1
            
            metadata.num_reads = bc.num_reads()
            metadata.mean_coverage = round(bc.mean_coverage(), settings.FLOATFIELD_DECIMAL_PLACES)
            metadata.num_vafs = num_vafs
            metadata.mean_entropy = round(bc.mean_entropy(), settings.FLOATFIELD_DECIMAL_PLACES)
            metadata.references = ",".join(bc.references)
            metadata.save(update_fields = ["num_reads", "mean_coverage", "num_vafs", "mean_entropy", "references"])
            
    except Exception as e:
        sample_id = metadata.sample_id
        metadata.delete()

        raise Exception(sample_id) from e
    
    