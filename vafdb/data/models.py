from django.db import models



# TODO: All max_lengths are pretty arbitrary at the moment
# TODO: Lineage
class Metadata(models.Model):
    pathogen = models.CharField(max_length=50)
    central_sample_id = models.CharField(max_length=50)
    run_name = models.CharField(max_length=100)
    published_name = models.CharField(max_length=100, unique=True)
    collection_date = models.DateField()
    published_date = models.DateField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    num_vafs = models.IntegerField()
    fasta_path = models.CharField(max_length=500)
    bam_path = models.TextField(max_length=500)
    primer_scheme = models.CharField(max_length=10)
    created = models.DateTimeField(null=True) # TODO: De-null

    class Meta:
        unique_together = ["central_sample_id", "run_name"]



class VAF(models.Model):
    metadata = models.ForeignKey(
        Metadata, 
        on_delete=models.CASCADE, 
        related_name="vaf"
    )
    reference = models.CharField(max_length=50)
    position = models.IntegerField()
    coverage = models.IntegerField()
    num_a = models.IntegerField()
    num_c = models.IntegerField()
    num_g = models.IntegerField()
    num_t = models.IntegerField()
    num_ds = models.IntegerField()
    entropy = models.FloatField(null=True) # TODO: De-null

    class Meta:
        unique_together = ["metadata", "reference", "position"]



# TODO: Could have reference in its own table?
# class Reference(models.Model):
#     metadata = models.ForeignKey(
#         Metadata, 
#         on_delete=models.CASCADE, 
#         related_name="vafs"
#     )
#     reference = models.CharField(max_length=50)
