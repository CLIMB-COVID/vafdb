from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from .models import Metadata, VAF
from .serializers import VAFSerializer
from .tasks import create
from .filters import VAFFilter
from utils.contextmanagers import mutable
from utils.functions import make_keyvalues, get_query


class CreateGetView(APIView):
    def post(self, request):
        """
        Start the celery task for creating a `Metadata` instance and its `VAF` instances.
        """
        # Kick off celery task
        task = create.delay(**request.data)

        # Return response with sample id and task id
        return Response(
            {
                "sample_id": request.data.get("sample_id"),
                "task_id": task.id,
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        """
        Use the provided `VAF` and `Metadata` fields to filter data.
        """
        # Prepare paginator
        paginator = CursorPagination()
        paginator.ordering = "created"
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE

        # Take out the pagination cursor param from the request
        with mutable(request.query_params) as query_params:
            cursor = query_params.get(paginator.cursor_query_param)
            if cursor:
                query_params.pop(paginator.cursor_query_param)

        # Turn the request query params into a series of dictionaries, each that will be passed to a filterset
        filterset_datas = []
        for field in request.query_params:
            values = list(set(request.query_params.getlist(field)))

            for i, value in enumerate(values):
                if len(filterset_datas) == i:
                    filterset_datas.append({})

                filterset_datas[i][field] = value

        # Dictionary of filterset errors
        errors = {}

        # Initial queryset
        qs = VAF.objects.select_related("metadata").all()

        # A filterset can only take a a query with one of each field at a time
        # So given that the get view only AND's fields together, we can represent this
        # as a series of filtersets ANDed together
        for i, filterset_data in enumerate(filterset_datas):
            # Generate filterset of current queryset
            filterset = VAFFilter(
                data=filterset_data,
                queryset=qs,
            )

            # Retrieve the resulting filtered queryset
            qs = filterset.qs

            # On first pass, append any unknown fields to error dict
            # Don't need to do more than i == 0, as here we have all the fields
            if i == 0:
                for field in filterset_data:
                    if field not in filterset.filters:
                        errors[field] = ["Unknown field."]

            # Append any filterset errors to the errors dict
            if not filterset.is_valid():
                for field, msg in filterset.errors.items():
                    errors[field] = msg

        # Return any errors that cropped up during filtering
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Add the pagination cursor param back into the request
        if cursor is not None:
            with mutable(request.query_params) as query_params:
                request.query_params[paginator.cursor_query_param] = cursor

        # Paginate the response
        vafs = qs.order_by("id")
        result_page = paginator.paginate_queryset(vafs, request)

        # Serialize the results
        serialized = VAFSerializer(result_page, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serialized.data)


class QueryView(APIView):
    def post(self, request):
        """
        Use the provided `VAF` and `Metadata` fields to filter data.
        """
        # Prepare paginator
        paginator = CursorPagination()
        paginator.ordering = "created"
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE

        # Take out the pagination cursor param from the request
        with mutable(request.query_params) as query_params:
            cursor = query_params.get(paginator.cursor_query_param)
            if cursor:
                query_params.pop(paginator.cursor_query_param)

        # Turn the value of each key-value pair in request.data into a 'KeyValue' object
        # Returns a list of the keyvalues
        keyvalues = make_keyvalues(request.data)

        # Construct a list of dictionaries from the keyvalues
        # Each of these dictionaries will be passed to a filterset
        # The filterset is being used just to clean and validate the input filters
        # Until we construct the query, it doesn't matter how fields are related in the query (i.e. AND, OR, etc)
        # All that matters is if the individual filters and their values are valid
        filterset_datas = [{}]
        for keyvalue in keyvalues:
            # Place the keyvalue in the first dictionary where the key is not present
            # If we reach the end with no placement, create a new dictionary and add it in there
            for filterset_data in filterset_datas:
                if keyvalue.key not in filterset_data:
                    filterset_data[keyvalue.key] = keyvalue
                    break
            else:
                filterset_datas.append({keyvalue.key: keyvalue})

        # Dictionary of filterset errors
        errors = {}

        # Use a filterset, applied to each dict in filterset_datas, to validate the data
        for i, filterset_data in enumerate(filterset_datas):
            # Slightly cursed, but it works
            filterset = VAFFilter(
                data={k: v.value for k, v in filterset_data.items()},
                queryset=VAF.objects.none(),
            )

            # On first pass, append any unknown fields to error dict
            # Don't need to do more than i == 0, as here we have all the fields
            if i == 0:
                for field in filterset_data:
                    if field not in filterset.filters:
                        errors[field] = ["Unknown field."]

            # Append any filterset errors to the errors dict
            if not filterset.is_valid():
                for field, msg in filterset.errors.items():
                    errors[field] = msg

            if not errors:
                # Add the cleaned values to the KeyValue objects
                for k, keyvalue in filterset_data.items():
                    keyvalue.value = filterset.form.cleaned_data[k]

                # Add the metadata prefix to the metadata field KeyValues, due to them being accessed via a query on the VAF table
                for k, v in filterset_data.items():
                    if k.split("__")[0] in filterset.metadata_fields:
                        v.key = "metadata__" + v.key

        # Return any errors that cropped up during validation
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # The data has been validated so we form the query (a Q object)
        query = get_query(request.data)

        # Then filter using the Q object
        qs = VAF.objects.select_related("metadata").filter(query)

        # Add the pagination cursor param back into the request
        if cursor is not None:
            with mutable(request.query_params) as query_params:
                request.query_params[paginator.cursor_query_param] = cursor

        # Paginate the response
        vafs = qs.order_by("id")
        result_page = paginator.paginate_queryset(vafs, request)

        # Serialize the results
        serialized = VAFSerializer(result_page, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serialized.data)


class DeleteView(APIView):
    def delete(self, request, sample_id):
        """
        Use the provided `sample_id` to permanently delete a `Metadata` instance and its `VAF` instances.
        """
        try:
            # Attempt to delete object with the provided sample_id
            Metadata.objects.get(sample_id=sample_id).delete()
        except Metadata.DoesNotExist:
            # If the sample_id did not exist, return error
            return Response(
                {sample_id: "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check for the deletion
        deleted = not Metadata.objects.filter(sample_id=sample_id).exists()

        # Return response indicating successful deletion
        return Response(
            {
                "sample_id": sample_id,
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )
