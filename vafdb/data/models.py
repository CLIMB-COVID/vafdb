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
    entropy = models.FloatField()
    secondary_entropy = models.FloatField()

    class Meta:
        unique_together = [
            "metadata", 
            "reference", 
            "position"
        ]



from django.db.models import Field
from django.db.models.lookups import BuiltinLookup

@Field.register_lookup
class IsNull(BuiltinLookup):
    lookup_name = "isnull"
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        if self.rhs in ["true", "True"]:
            self.rhs = True
        elif self.rhs in ["false", "False"]:
            self.rhs = False

        if not isinstance(self.rhs, bool):
            raise ValueError(
                "The QuerySet value for an isnull lookup must be True or False."
            )
        sql, params = compiler.compile(self.lhs)
        if self.rhs:
            return "%s IS NULL" % sql, params
        else:
            return "%s IS NOT NULL" % sql, params
