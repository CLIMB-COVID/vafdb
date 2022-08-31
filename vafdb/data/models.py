from django.db import models



class Metadata(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    sample_id = models.TextField(unique=True)
    site_code = models.TextField()
    bam_path = models.TextField()
    collection_date = models.DateField()

    published_date = models.DateField(auto_now_add=True)
    num_reads = models.IntegerField(null=True)
    num_vafs = models.IntegerField(null=True)
    mean_coverage = models.FloatField(null=True)
    mean_entropy = models.FloatField(null=True)
    references = models.TextField(null=True)



class VAF(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    metadata = models.ForeignKey(
        Metadata,
        on_delete=models.CASCADE, 
        related_name="vaf",
        db_index=True
    )
    reference = models.CharField(max_length=50, db_index=True)
    position = models.IntegerField(db_index=True)
    coverage = models.IntegerField()
    num_a = models.IntegerField()
    num_c = models.IntegerField()
    num_g = models.IntegerField()
    num_t = models.IntegerField()
    num_ds = models.IntegerField()
    pc_a = models.IntegerField()
    pc_c = models.IntegerField()
    pc_g = models.IntegerField()
    pc_t = models.IntegerField()
    pc_ds = models.IntegerField()
    entropy = models.FloatField()
    secondary_entropy = models.FloatField()

    class Meta:
        unique_together = [
            "metadata", 
            "reference", 
            "position"
        ]



@models.Field.register_lookup
class NotEqual(models.Lookup):
    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params
