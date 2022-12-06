from django.db import models
from django.db.models import Field
from django.db.models.lookups import BuiltinLookup


@Field.register_lookup
class NotEqual(models.Lookup):
    lookup_name = "ne"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <> %s" % (lhs, rhs), params


@Field.register_lookup
class IsNull(BuiltinLookup):
    lookup_name = "isnull"
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        if str(self.rhs) in ["0", "false", "False"]:
            self.rhs = False

        elif str(self.rhs) in ["1", "false", "False"]:
            self.rhs = True

        if not isinstance(self.rhs, bool):
            raise ValueError(
                "The QuerySet value for an isnull lookup must be True or False."
            )

        sql, params = compiler.compile(self.lhs)
        if self.rhs:
            return "%s IS NULL" % sql, params
        else:
            return "%s IS NOT NULL" % sql, params


class Reference(models.Model):
    name = models.TextField(unique=True)
    sequence = models.TextField()


class Metadata(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    sample_id = models.TextField(unique=True)
    site = models.TextField(db_index=True)
    bam_path = models.TextField()
    collection_date = models.DateField(db_index=True)
    published_date = models.DateField(auto_now_add=True, db_index=True)
    num_reads = models.IntegerField(null=True)
    num_vafs = models.IntegerField(null=True)
    mean_coverage = models.FloatField(null=True)
    mean_entropy = models.FloatField(null=True)
    references = models.TextField(null=True)


class VAF(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, related_name="vaf")
    reference = models.TextField(db_index=True)
    position = models.IntegerField(db_index=True)
    coverage = models.IntegerField()
    ref_base = models.CharField(max_length=2)
    base = models.CharField(max_length=2)
    confidence = models.FloatField()
    diff = models.BooleanField()
    num_a = models.IntegerField()
    num_c = models.IntegerField()
    num_g = models.IntegerField()
    num_t = models.IntegerField()
    num_ds = models.IntegerField()
    pc_a = models.FloatField()
    pc_c = models.FloatField()
    pc_g = models.FloatField()
    pc_t = models.FloatField()
    pc_ds = models.FloatField()
    entropy = models.FloatField()
    secondary_entropy = models.FloatField()

    class Meta:
        unique_together = ["metadata", "reference", "position"]
