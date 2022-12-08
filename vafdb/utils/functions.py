from django.db.models import Q
from .classes import KeyValue
import operator
import functools


def choices(cs):
    return [(c, c) for c in cs]


def make_keyvalues(data):
    """
    Traverses the provided `data` and replaces request values with `KeyValue` objects.

    Returns a list of these `KeyValue` objects.
    """
    key, value = next(iter(data.items()))

    if key in {"&", "|", "^", "~"}:
        keyvalues = [make_keyvalues(k_v) for k_v in value]
        return functools.reduce(operator.add, keyvalues)
    else:
        # Initialise KeyValue object
        keyvalue = KeyValue(key, value)

        # Replace the request.data value with the KeyValue object
        data[key] = keyvalue

        # Now return the Keyvalue object
        # All this is being done so that its easy to modify the key/value in the request.data structure
        # To modify the key/values, we will be able to change them in the returned list
        # And because they are the same objects as in request.data, that will be altered as well
        return [keyvalue]


def get_query(data):
    """
    Traverses the provided `data` and forms the corresponding Q object.
    """
    key, value = next(iter(data.items()))

    # AND of multiple keyvalues
    if key == "&":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.and_, q_objects)

    # OR of multiple keyvalues
    elif key == "|":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.or_, q_objects)

    # XOR of multiple keyvalues
    elif key == "^":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.xor, q_objects)

    # NOT of a single keyvalue
    elif key == "~":
        q_object = [get_query(k_v) for k_v in value][0]
        return ~q_object

    # Base case: a keyvalue to filter on
    else:
        # 'value' here is a KeyValue object
        # That by this point, should have been cleaned and corrected to work in a query
        q = Q(**{value.key: value.value})
        return q
