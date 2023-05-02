def check_kwargs(kwargs):
    if len(kwargs) != 1:
        raise Exception("Exactly one field and its value must be provided")


def check_field(field):
    if not isinstance(field, F):
        raise Exception("Can only combine field with other fields")


class F:
    def __init__(self, **kwargs):
        check_kwargs(kwargs)

        field, value = next(iter(kwargs.items()))

        if (field not in ["&", "|", "^", "~"]) and (type(value) in [list, tuple, set]):
            value = ",".join(map(str, value))

        self.query = {field: value}

    def __and__(self, field):
        check_field(field)
        return F(**{"&": [self.query, field.query]})

    def __or__(self, field):
        check_field(field)
        return F(**{"|": [self.query, field.query]})

    def __xor__(self, field):
        check_field(field)
        return F(**{"^": [self.query, field.query]})

    def __invert__(self):
        return F(**{"~": [self.query]})
