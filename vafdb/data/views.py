from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from django.db.models import Prefetch
from .models import Metadata, VAF
from .serializers import MetadataSerializer



class CreateGetVAFView(APIView):
    def post(self, request):
        serializer = MetadataSerializer(data=request.data)        

        if serializer.is_valid():
            serializer.save()
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
        # Remove query params from the request that we do not wish to filter on
        _mutable = request.query_params._mutable
        request.query_params._mutable = True
        # The cursor param is for paginating the request, not for filtering
        cursor = request.query_params.get("cursor")
        if cursor:
            request.query_params.pop("cursor")
        request.query_params._mutable = _mutable

        # Get vaf query parameters
        vaf_query_params = {}
        for field in request.query_params:
            if field == "vaf":
                # Just filtering on 'vafs' in metadata filters by VAF id
                # So we want to keep the same behaviour when filtering the vafs separately
                vaf_query_params["id"] = request.query_params.getlist(field)
            elif field.startswith("vaf__"):
                field_split = field.split("__")
                vaf_field = "__".join(field_split[1:])
                vaf_query_params[vaf_field] = request.query_params.getlist(field)

        # By default, create queryset of all VAF objects
        vafs = VAF.objects.all()

        # Filter VAF queryset by each provided vaf field
        for field, values in vaf_query_params.items():
            for value in values:
                try:
                    if value == settings.FIELD_NULL_TOKEN:
                        value = None                

                    vafs = vafs.filter(**{field : value})

                except Exception as e:
                    return Response(
                        e.args, 
                        status=status.HTTP_400_BAD_REQUEST
                    )             
        
        # By default, create queryset of all Metadata objects
        metadata = Metadata.objects.all()
        
        # Filter Metadata by each provided field
        for field in request.query_params:
            values = request.query_params.getlist(field)
            for value in values:
                try:
                    if value == settings.FIELD_NULL_TOKEN:
                        value = None

                    metadata = metadata.filter(**{field : value})
                
                except Exception as e:
                    return Response(
                        e.args, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # TODO: Moving this down here fixed something regarding duplication of metadata instances. Why is that?
        # Combine filtered VAF results with metadata
        metadata = metadata.prefetch_related(Prefetch("vaf", vafs))

        # Add the cursor back in to the query params, because its needed for pagination
        if cursor is not None:
            _mutable = request.query_params._mutable
            request.query_params._mutable = True
            request.query_params["cursor"] = cursor       
            request.query_params._mutable = _mutable

        # Paginate the response
        metadata = metadata.order_by("id")
        paginator = CursorPagination()
        paginator.ordering = "modified_date" # TODO: Must be created, not modified
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE        
        result_page = paginator.paginate_queryset(metadata, request)

        # TODO: Hide vafs option

        serializer = MetadataSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
