from django.db import models
from django.db.models.lookups import BuiltinLookup
from django.db.models.fields.related_lookups import RelatedLookupMixin
from utils.functions import choices
from utils.fields import UpperCharField, LowerCharField


class NotEqual(models.Lookup):
    lookup_name = "ne"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <> %s" % (lhs, rhs), params


class NotEqualRelated(RelatedLookupMixin, NotEqual):
    pass


class IsNull(BuiltinLookup):
    lookup_name = "isnull"
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        if str(self.rhs).lower() in ["0", "false"]:
            self.rhs = False

        elif str(self.rhs).lower() in ["1", "true"]:
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


class IsNullRelated(RelatedLookupMixin, IsNull):
    pass


class Project(models.Model):
    code = LowerCharField(max_length=50, unique=True)
    description = models.TextField(null=True)
    region = models.TextField(null=True)
    base_quality = models.IntegerField(default=0)
    mapping_quality = models.IntegerField(default=0)
    min_coverage = models.IntegerField(default=0)
    min_entropy = models.FloatField(default=0)
    min_secondary_entropy = models.FloatField(default=0)
    insertions = models.BooleanField(default=False)
    diff_confidence = models.IntegerField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]


class Reference(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
    sequence = models.TextField()

    class Meta:
        unique_together = [
            "project",
            "name",
        ]


class Metadata(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sample_id = models.TextField()
    bam_path = models.TextField()
    published_date = models.DateField(auto_now_add=True)
    collection_date = models.DateField(null=True)
    site = models.TextField(null=True)
    num_reads = models.IntegerField(null=True)
    num_vafs = models.IntegerField(null=True)
    mean_coverage = models.FloatField(null=True)
    mean_entropy = models.FloatField(null=True)
    references = models.TextField(null=True)

    class Meta:
        unique_together = [
            "project",
            "sample_id",
        ]
        indexes = [
            models.Index(fields=["project", "sample_id"]),
            models.Index(fields=["project"]),
            models.Index(fields=["sample_id"]),
            models.Index(fields=["published_date"]),
        ]


class VAF(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, related_name="vaf")
    reference = models.TextField()
    position = models.IntegerField()
    insertion = models.IntegerField()
    ptype = UpperCharField(max_length=3, choices=choices(["REF", "INS"]))
    coverage = models.IntegerField()
    ref_base = UpperCharField(max_length=2, choices=choices(["A", "C", "T", "G", "DS"]))
    base = UpperCharField(
        max_length=2, choices=choices(["A", "C", "T", "G", "DS"]), null=True
    )
    confidence = models.FloatField()
    diff = models.BooleanField()
    a = models.IntegerField()
    c = models.IntegerField()
    g = models.IntegerField()
    t = models.IntegerField()
    ds = models.IntegerField()
    pc_a = models.FloatField()
    pc_c = models.FloatField()
    pc_g = models.FloatField()
    pc_t = models.FloatField()
    pc_ds = models.FloatField()
    entropy = models.FloatField()
    secondary_entropy = models.FloatField()

    class Meta:
        unique_together = [
            "metadata",
            "reference",
            "position",
            "insertion",
        ]
        indexes = [
            models.Index(fields=["metadata"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["position"]),
            models.Index(fields=["insertion"]),
        ]
