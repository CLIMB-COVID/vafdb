from django_filters import rest_framework as filters


class ChoiceInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    pass


class ChoiceRangeFilter(filters.BaseRangeFilter, filters.ChoiceFilter):
    pass


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class NumberRangeFilter(filters.BaseRangeFilter, filters.NumberFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class CharRangeFilter(filters.BaseRangeFilter, filters.CharFilter):
    pass


class DateInFilter(filters.BaseInFilter, filters.DateFilter):
    pass


class DateRangeFilter(filters.BaseRangeFilter, filters.DateFilter):
    pass


class TypedChoiceInFilter(filters.BaseInFilter, filters.TypedChoiceFilter):
    pass


class TypedChoiceRangeFilter(filters.BaseInFilter, filters.TypedChoiceFilter):
    pass
