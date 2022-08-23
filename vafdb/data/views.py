from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from .models import VAF
from .serializers import MetadataSerializer, VAFSerializer
from .tasks import create_vafs



class CreateGetVAFView(APIView):
    def post(self, request):
        serializer = MetadataSerializer(data=request.data)        

        if serializer.is_valid():
            metadata = serializer.save()
            create_vafs.delay(metadata.id)

            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )        


    def get(self, request):
        # Get all VAFs, with their related Metadata
        vafs = VAF.objects.select_related("metadata").all()

        for field in request.query_params:
            if field == "cursor":
                # Ignore this param as its used for pagination
                continue

            values = request.query_params.getlist(field)
            for value in values:
                try:
                    if value == settings.FIELD_NULL_TOKEN:
                        # Filter for rows with a NULL value
                        value = None

                    vafs = vafs.filter(**{field : value})

                except Exception as e:
                    return Response(
                        e.args, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Paginate the response
        vafs = vafs.order_by("id")
        paginator = CursorPagination()
        paginator.ordering = "created"
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE      
        result_page = paginator.paginate_queryset(vafs, request)

        # Serialize the results
        serializer = VAFSerializer(
            result_page, 
            many=True
        )
        return paginator.get_paginated_response(serializer.data)
