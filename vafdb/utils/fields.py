from django.db import models


class UpperCharField(models.CharField):
    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, str):
            return value.upper()

        return str(value).upper()
