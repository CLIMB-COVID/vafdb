from django_filters import rest_framework as filters
from .models import VAF



BASE_LOOKUPS = ["exact", "contains", "in", "range", "ne", "lt", "gt", "lte", "gte"]
CHAR_LOOKUPS = BASE_LOOKUPS + ["startswith", "endswith", "iexact", "icontains", "istartswith", "iendswith", "regex", "iregex"]
NUMBER_LOOKUPS = BASE_LOOKUPS
DATE_LOOKUPS = BASE_LOOKUPS + [
        "year" + x for x in ["", "__ne", "__lt", "__gt", "__lte", "__gte"]
    ] + [
        "month" + x for x in ["", "__ne", "__lt", "__gt", "__lte", "__gte"]
    ] + [
        "day" + x for x in ["", "__ne", "__lt", "__gt", "__lte", "__gte"]
    ]



class VAFFilter(filters.FilterSet):
    class Meta:
        model = VAF
        fields = {
            "metadata__sample_id" : CHAR_LOOKUPS,
            "metadata__site_code" : CHAR_LOOKUPS,
            "metadata__bam_path" : CHAR_LOOKUPS,
            "metadata__collection_date" : DATE_LOOKUPS,
            "metadata__published_date" : DATE_LOOKUPS,
            "metadata__num_reads" : NUMBER_LOOKUPS,
            "metadata__mean_coverage" : NUMBER_LOOKUPS,
            "metadata__mean_entropy" : NUMBER_LOOKUPS,
            "metadata__references" : CHAR_LOOKUPS,
            "reference" : CHAR_LOOKUPS,
            "position" : NUMBER_LOOKUPS,
            "coverage" : NUMBER_LOOKUPS,
            "num_a" : NUMBER_LOOKUPS,
            "num_c" : NUMBER_LOOKUPS,
            "num_g" : NUMBER_LOOKUPS,
            "num_t" : NUMBER_LOOKUPS,
            "num_ds" : NUMBER_LOOKUPS,
            "pc_a" : NUMBER_LOOKUPS,
            "pc_c" : NUMBER_LOOKUPS,
            "pc_g" : NUMBER_LOOKUPS,
            "pc_t" : NUMBER_LOOKUPS,
            "pc_ds" : NUMBER_LOOKUPS,
            "entropy" : NUMBER_LOOKUPS,
            "secondary_entropy" : NUMBER_LOOKUPS
        }

    @classmethod
    def get_filter_name(cls, field_name, lookup_expr):
        field_name = field_name.removeprefix("metadata__")
        return super().get_filter_name(field_name, lookup_expr)
