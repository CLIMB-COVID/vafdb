from rest_framework import serializers


class LowerChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        data = str(data).lower()
        return super().to_internal_value(data)


class UpperChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        data = str(data).upper()
        return super().to_internal_value(data)
