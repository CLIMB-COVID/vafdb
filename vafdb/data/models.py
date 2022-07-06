from django.db import models

# Create your models here.

class MetadataRecord(models.Model):
    pathogen = models.CharField(max_length=100)
    central_sample_id = models.CharField(max_length=100)
    run_name = models.CharField(max_length=100)
    published_name = models.CharField(max_length=100, unique=True)
    collection_date = models.DateField()
    published_date = models.DateField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    num_vafs = models.IntegerField()
    fasta_path = models.CharField(max_length=500)
    bam_path = models.TextField(max_length=500)
    lineage = models.CharField(max_length=100)
    primer_scheme = models.CharField(max_length=100)

    class Meta:
        unique_together = ["central_sample_id", "run_name"]


class VAFRecord(models.Model):
    metadata_record = models.ForeignKey(
        MetadataRecord, 
        on_delete=models.CASCADE, 
        related_name="vafs"
    )
    reference = models.CharField(max_length=100)
    position = models.IntegerField()
    coverage = models.IntegerField()
    num_a = models.IntegerField()
    num_c = models.IntegerField()
    num_g = models.IntegerField()
    num_t = models.IntegerField()
    num_ds = models.IntegerField()
    # consensus_base = models.CharField(
    #     max_length=1,
    #     choices=(
    #         ("A", "A"),
    #         ("C", "C"),
    #         ("G", "G"),
    #         ("T", "T"),
    #         ("N", "N")
    #     )
    # )

    class Meta:
        unique_together = ["metadata_record", "reference", "position"]
