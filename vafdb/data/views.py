from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from .models import VAF
from .serializers import MetadataSerializer, VAFSerializer
from .tasks import create_vafs
from .filters import VAFFilter
from utils.contextmanagers import mutable


class CreateGetVAFView(APIView):
    def post(self, request):
        serializer = MetadataSerializer(data=request.data)

        if serializer.is_valid():
            metadata = serializer.save()
            create_vafs.delay(metadata.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"detail": "hello there"})
