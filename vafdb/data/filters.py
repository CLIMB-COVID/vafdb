from django_filters import rest_framework as filters
from distutils.util import strtobool
from utils.filters import (
    CharInFilter,
    CharRangeFilter,
    NumberInFilter,
    NumberRangeFilter,
    DateInFilter,
    DateRangeFilter,
)


# Lookups shared by all fields
BASE_LOOKUPS = ["exact", "ne", "lt", "lte", "gt", "gte"]

# Additional lookups for CharField and TextField
CHAR_LOOKUPS = [
    "contains",
    "startswith",
    "endswith",
    "iexact",
    "icontains",
    "istartswith",
    "iendswith",
    "regex",
    "iregex",
]

# Accepted strings for True and False when validating BooleanField
BOOLEAN_CHOICES = (
    ("True", "True"),
    ("true", "true"),
    ("False", "False"),
    ("false", "false"),
)


fields = {
    "metadata__sample_id": "text",
    "metadata__site": "text",
    "metadata__bam_path": "text",
    "metadata__collection_date": "date",
    "metadata__published_date": "date",
    "metadata__num_reads": "number",
    "metadata__mean_coverage": "number",
    "metadata__mean_entropy": "number",
    "metadata__references": "text",
    "reference": "text",
    "position": "number",
    "coverage": "number",
    "num_a": "number",
    "num_c": "number",
    "num_g": "number",
    "num_t": "number",
    "num_ds": "number",
    "pc_a": "number",
    "pc_c": "number",
    "pc_g": "number",
    "pc_t": "number",
    "pc_ds": "number",
    "entropy": "number",
    "secondary_entropy": "number",
}


class VAFFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.metadata_fields = []

        for field, field_type in fields.items():
            filter_name = field.removeprefix("metadata__")

            if field.startswith("metadata__"):
                self.metadata_fields.append(filter_name)

            if not any(x.startswith(filter_name) for x in self.data):
                continue

            if field_type == "text":
                self.filters[filter_name] = filters.CharFilter(field_name=field)
                self.filters[filter_name + "__in"] = CharInFilter(
                    field_name=field, lookup_expr="in"
                )
                self.filters[filter_name + "__range"] = CharRangeFilter(
                    field_name=field, lookup_expr="range"
                )
                self.filters[filter_name + "__isnull"] = filters.TypedChoiceFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="isnull",
                )

                for lookup in BASE_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.CharFilter(
                        field_name=field, lookup_expr=lookup
                    )

                for lookup in CHAR_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.CharFilter(
                        field_name=field, lookup_expr=lookup
                    )

            elif field_type == "number":
                self.filters[filter_name] = filters.NumberFilter(field_name=field)

                self.filters[filter_name + "__in"] = NumberInFilter(
                    field_name=field, lookup_expr="in"
                )
                self.filters[filter_name + "__range"] = NumberRangeFilter(
                    field_name=field, lookup_expr="range"
                )
                self.filters[filter_name + "__isnull"] = filters.TypedChoiceFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="isnull",
                )

                for lookup in BASE_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.NumberFilter(
                        field_name=field, lookup_expr=lookup
                    )

            elif field_type == "date":
                self.filters[filter_name] = filters.DateFilter(
                    field_name=field, input_formats=["%Y-%m-%d"]
                )
                self.filters[filter_name + "__in"] = DateInFilter(
                    field_name=field, input_formats=["%Y-%m-%d"], lookup_expr="in"
                )
                self.filters[filter_name + "__range"] = DateRangeFilter(
                    field_name=field, input_formats=["%Y-%m-%d"], lookup_expr="range"
                )
                self.filters[filter_name + "__isnull"] = filters.TypedChoiceFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="isnull",
                )
                self.filters[filter_name + "__iso_year"] = filters.NumberFilter(
                    field_name=field, lookup_expr="iso_year"
                )
                self.filters[filter_name + "__iso_year__in"] = NumberInFilter(
                    field_name=field,
                    lookup_expr="iso_year__in",
                )
                self.filters[filter_name + "__iso_year__range"] = NumberRangeFilter(
                    field_name=field,
                    lookup_expr="iso_year__range",
                )
                self.filters[filter_name + "__week"] = filters.NumberFilter(
                    field_name=field, lookup_expr="week"
                )
                self.filters[filter_name + "__week__in"] = NumberInFilter(
                    field_name=field,
                    lookup_expr="week__in",
                )
                self.filters[filter_name + "__week__range"] = NumberRangeFilter(
                    field_name=field,
                    lookup_expr="week__range",
                )

                for lookup in BASE_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.DateFilter(
                        field_name=field, input_formats=["%Y-%m-%d"], lookup_expr=lookup
                    )
