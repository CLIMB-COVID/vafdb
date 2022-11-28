from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from django.db.models import Q
from .models import VAF
from .serializers import VAFSerializer
from .tasks import create
from .filters import VAFFilter
from utils.contextmanagers import mutable
import operator
import functools


class QField:
    def __init__(self, key, value):
        self.key = key
        self.value = value


def make_qfields(data):
    key, value = next(iter(data.items()))

    if key in ["&", "|", "^", "~"]:
        for k_v in value:
            make_qfields(k_v)
    else:
        data[key] = QField(key, value)


def get_qfields_flat(data):
    """
    Traverses the provided `data`, that specifies an arbitrarily complex query, and returns a list of all `(key, value)` fields.
    """
    key, value = next(iter(data.items()))

    # AND of multiple key-value pairs
    if key == "&":
        k_v_objects = [get_qfields_flat(k_v) for k_v in value]
        return functools.reduce(operator.add, k_v_objects)

    # OR of multiple key-value pairs
    elif key == "|":
        k_v_objects = [get_qfields_flat(k_v) for k_v in value]
        return functools.reduce(operator.add, k_v_objects)

    # XOR of multiple key-value pairs
    elif key == "^":
        k_v_objects = [get_qfields_flat(k_v) for k_v in value]
        return functools.reduce(operator.add, k_v_objects)

    # NOT of a single key-value pair
    elif key == "~":
        k_v_object = [get_qfields_flat(k_v) for k_v in value][0]
        return k_v_object

    # Base case: a key-value pair we want to filter on
    else:
        return [(key, value)]


def get_query(data):
    """
    Traverses the provided `data`, that specifies an arbitrarily complex query, and forms the corresponding Q object.

    Also returns a flattened list of all `(key, value)` tuples used to form the Q object.
    """
    key, value = next(iter(data.items()))

    # AND of multiple key-value pairs
    if key == "&":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.and_, q_objects)

    # OR of multiple key-value pairs
    elif key == "|":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.or_, q_objects)

    # XOR of multiple key-value pairs
    elif key == "^":
        q_objects = [get_query(k_v) for k_v in value]
        return functools.reduce(operator.xor, q_objects)

    # NOT of a single key-value pair
    elif key == "~":
        q_object = [get_query(k_v) for k_v in value][0]
        return ~q_object

    # Base case: a key-value pair we want to filter on
    else:
        q = Q(
            **{value.key: value.value}
        )  # value is a QField (hopefully with clean data)
        return q


class CreateGetVAFView(APIView):
    def post(self, request):
        task = create.delay(**request.data)
        return Response(
            {
                "sample_id": request.data.get("sample_id"),
                "task_id": task.id,
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        # Prepare paginator
        paginator = CursorPagination()
        paginator.ordering = "created"
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE

        # Take out the pagination cursor param from the request
        with mutable(request.query_params) as query_params:
            cursor = query_params.get(paginator.cursor_query_param)
            if cursor:
                query_params.pop(paginator.cursor_query_param)

        filterset = VAFFilter(
            request.query_params,
            queryset=VAF.objects.select_related("metadata").all(),
        )

        errors = {}

        # Append unknown fields to error dict
        for field in request.query_params:
            if field not in filterset.filters:
                errors[field] = ["Unknown field."]

        if not filterset.is_valid():
            # Append invalid fields to error dict
            for field, msg in filterset.errors.items():
                errors[field] = msg

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Add the pagination cursor param back into the request
        if cursor is not None:
            with mutable(request.query_params) as query_params:
                request.query_params[paginator.cursor_query_param] = cursor

        # Paginate the response
        vafs = filterset.qs.order_by("id")
        result_page = paginator.paginate_queryset(vafs, request)

        # Serialize the results
        serializer = VAFSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class QueryVAFView(APIView):
    def post(self, request):
        # Turn the value of each key-value pair in request.data into a 'QField' object
        make_qfields(request.data)

        # Get flattened list of qfields
        qfields = get_qfields_flat(request.data)

        # Convert the key-value pairs into a structure that resembles the get request's query_params
        request_structured_data = {}
        for field, value in qfields:
            request_structured_data.setdefault(field, []).append(value)

        # Validate this structure using the filterset
        # This ensures the key-value pairs for this nested query go through the same validation as a standard get request
        data = {}
        num_filtersets = 0
        for field, values in request_structured_data.items():
            data[field] = values
            if len(values) > num_filtersets:
                num_filtersets = len(values)

        filterset_datas = [{} for _ in range(num_filtersets)]
        for field, values in data.items():
            for i, value in enumerate(values):
                filterset_datas[i][field] = value

        errors = {}

        for i, filterset_data in enumerate(filterset_datas):
            # Slightly cursed, but it works
            filterset = VAFFilter(
                data={k: v.value for k, v in filterset_data.items()},
                queryset=VAF.objects.none(),
            )

            # On first pass, append any unknown fields to error dict
            if i == 0:
                # Don't need to do more than i == 0, as here we have all the fields
                for field in filterset_data:
                    if field not in filterset.filters:
                        errors[field] = ["Unknown field."]

            if errors or not filterset.is_valid():
                # Append any filterset errors to the errors dict
                for field, msg in filterset.errors.items():
                    errors[field] = msg

            else:
                # Add clean value to the qfields
                for k, qfield in filterset_data.items():
                    qfield.value = filterset.form.cleaned_data[k]

                # Need to swap out filter names for actual field names
                for field in filterset.metadata_fields:
                    for k, v in filterset_data.items():
                        if k.startswith(field):
                            v.key = "metadata__" + v.key

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # The data has been validated (to the best of my knowledge)
        # Form the query (a Q object)
        query = get_query(request.data)

        # Form the queryset, then filter by the Q object
        qs = VAF.objects.select_related("metadata").filter(query)

        # Serialize the results
        serializer = VAFSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
