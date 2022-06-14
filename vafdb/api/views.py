from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import MetadataRecord
from .serializers import MetadataRecordSerializer


@api_view(["GET"])
def get_metadata(request):
    metadata_records = MetadataRecord.objects.all()
    serializer = MetadataRecordSerializer(metadata_records, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def add_metadata(request):
    serializer = MetadataRecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

    