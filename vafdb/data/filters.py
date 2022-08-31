from django_filters import rest_framework as filters
from .models import VAF


CHAR_LOOKUPS = ["exact", "contains", "isnull"]
NUMBER_LOOKUPS = ["exact", "lt", "gt", "lte", "gte", "isnull"]
DATE_LOOKUPS = ["exact", "lt", "gt", "lte", "gte", "isnull"]


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
            "entropy" : NUMBER_LOOKUPS,
            "secondary_entropy" : NUMBER_LOOKUPS
        }

    @classmethod
    def get_filter_name(cls, field_name, lookup_expr):
        field_name = field_name.removeprefix("metadata__")
        return super().get_filter_name(field_name, lookup_expr)
