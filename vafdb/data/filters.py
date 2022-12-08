from django_filters import rest_framework as filters
from distutils.util import strtobool
from utils.filters import (
    ChoiceInFilter,
    ChoiceRangeFilter,
    CharInFilter,
    CharRangeFilter,
    NumberInFilter,
    NumberRangeFilter,
    DateInFilter,
    DateRangeFilter,
    TypedChoiceInFilter,
    TypedChoiceRangeFilter,
)
from .models import VAF


# Lookups shared by all fields
BASE_LOOKUPS = [
    "exact",
    "ne",
    "lt",
    "lte",
    "gt",
    "gte",
]

# Additional lookups for text fields
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

# Accepted strings for True and False when validating bool fields
BOOLEAN_CHOICES = (
    ("True", "True"),
    ("true", "true"),
    ("False", "False"),
    ("false", "false"),
)


# All filterable fields and their field type
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
    "position_type": "choice",
    "insert_position": "number",
    "coverage": "number",
    "ref_base": "choice",
    "base": "choice",
    "confidence": "number",
    "diff": "bool",
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

        # List of metadata fields (not including the prefix required for VAF filter)
        self.metadata_fields = []

        # List of all choice filters
        # This is needed for finding and setting any user input choice values to uppercase
        # Want choice fields to be case-insensitive, so this needs doing before the filterset form validates the user data
        self.choice_filters = []

        for field, field_type in fields.items():
            # Filter name is the user-facing name for the field
            # Don't want metadata fields to require this prefix so its removed in the filter name
            filter_name = field.removeprefix("metadata__")

            # If none of the user supplied fields even start with the filter name, it can be assumed we dont need to build this filter
            if not any(x.startswith(filter_name) for x in self.data):
                continue

            # If field is a metadata field, add it to the list of metadata fields
            if field.startswith("metadata__"):
                self.metadata_fields.append(filter_name)

            # If field is a choice type, construct choice filters for it
            if field_type == "choice":
                choices = VAF._meta.get_field(field).choices

                self.filters[filter_name] = filters.ChoiceFilter(
                    field_name=field, choices=choices
                )
                self.choice_filters.append(filter_name)

                self.filters[filter_name + "__in"] = ChoiceInFilter(
                    field_name=field, choices=choices, lookup_expr="in"
                )
                self.choice_filters.append(filter_name + "__in")

                self.filters[filter_name + "__range"] = ChoiceRangeFilter(
                    field_name=field, choices=choices, lookup_expr="range"
                )
                self.choice_filters.append(filter_name + "__range")

                self.filters[filter_name + "__isnull"] = filters.TypedChoiceFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="isnull",
                )

                for lookup in BASE_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.ChoiceFilter(
                        field_name=field, choices=choices, lookup_expr=lookup
                    )
                    self.choice_filters.append(filter_name + "__" + lookup)

                for lookup in CHAR_LOOKUPS:
                    self.filters[filter_name + "__" + lookup] = filters.CharFilter(
                        field_name=field, lookup_expr=lookup
                    )
                    self.choice_filters.append(filter_name + "__" + lookup)

            # If field is text, construct text filters for it
            elif field_type == "text":
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

            # If field is a number, construct number filters for it
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

            # If field is a date, construct date filters for it
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

            # If field is a bool, construct bool filters for it
            elif field_type == "bool":
                self.filters[filter_name] = filters.TypedChoiceFilter(
                    field_name=field, choices=BOOLEAN_CHOICES, coerce=strtobool
                )
                self.filters[filter_name + "__in"] = TypedChoiceInFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="in",
                )
                self.filters[filter_name + "__range"] = TypedChoiceRangeFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="range",
                )
                self.filters[filter_name + "__isnull"] = filters.TypedChoiceFilter(
                    field_name=field,
                    choices=BOOLEAN_CHOICES,
                    coerce=strtobool,
                    lookup_expr="isnull",
                )

                for lookup in BASE_LOOKUPS:
                    self.filters[
                        filter_name + "__" + lookup
                    ] = filters.TypedChoiceFilter(
                        field_name=field,
                        choices=BOOLEAN_CHOICES,
                        coerce=strtobool,
                        lookup_expr=lookup,
                    )

        # Check user data for any choice fields, and set their values to uppercase
        for field, value in self.data.items():
            if field in self.choice_filters and isinstance(value, str):
                self.data[field] = value.upper()
