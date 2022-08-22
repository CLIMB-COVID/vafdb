from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.conf import settings
from django.db.models import Prefetch
from .models import Metadata, VAF
from .serializers import MetadataSerializer, VAFSerializer



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


    def get_scary(self, request):
        # Separate Metadata and VAF query parameters
        query_params = {
            "metadata" : {},
            "vaf" : {}
        }
        for field in request.query_params:
            if field == "cursor":
                # Ignore the cursor param, its for pagination not filtering
                continue

            values = request.query_params.getlist(field)
            if field == "vaf":
                # Just filtering on 'vafs' in metadata filters by VAF id
                # So we want to keep the same behaviour when filtering the vafs separately
                query_params["vaf"]["id"] = values
            elif field.startswith("vaf__"):
                query_params["vaf"][field.removeprefix("vaf__")] = values
            else:
                query_params["metadata"][field] = values

        # By default, create queryset of all VAF objects and all Metadata objects
        vafs = VAF.objects.all()
        # NOTE: Using id list instead of distinct() is an alternative
        # ids = vafs.values_list("metadata", flat=True).distinct()
        # metadata = Metadata.objects.filter(id__in=list(ids))
        metadata = Metadata.objects.all()

        # Filter each queryset by their provided fields
        for query_param_group in query_params:
            for field, values in query_params[query_param_group].items():
                for value in values:
                    try:
                        if value == settings.FIELD_NULL_TOKEN:
                            value = None
                        
                        if query_param_group == "metadata":
                            metadata = metadata.filter(**{field : value})
                        else:
                            vafs = vafs.filter(**{field : value})
                            metadata = metadata.filter(**{"vaf__" + field : value}).distinct()

                    except Exception as e:
                        return Response(
                            e.args, 
                            status=status.HTTP_400_BAD_REQUEST
                        )

        # TODO: Moving this down here fixed something regarding duplication of metadata instances. Why is that?
        # Combine filtered VAF results with metadata
        metadata = metadata.prefetch_related(Prefetch("vaf", queryset=vafs))

        # Paginate the response
        metadata = metadata.order_by("id")
        paginator = CursorPagination()
        paginator.ordering = "created"
        paginator.page_size = settings.CURSOR_PAGINATION_PAGE_SIZE        
        result_page = paginator.paginate_queryset(metadata, request)

        # TODO: Serializer which hides the vafs (and a request param for this)
        serializer = MetadataSerializer(result_page, many=True)

        # NOTE: Not filtering metadata for vaf fields, but removing them after is also an option
        # data = []
        # for val in serializer.data:
        #     if val["vaf"]:
        #         data.append(val)

        return paginator.get_paginated_response(serializer.data)


    def get(self, request):
        vafs = VAF.objects.select_related("metadata").all()

        for field in request.query_params:
            values = request.query_params.getlist(field)
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
        
        serializer = VAFSerializer(
            vafs, 
            many=True
        )

        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )
