from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import MetadataRecord
from .serializers import MetadataRecordSerializer


# @api_view(["GET"])
# def get_central_sample_id(request):
#     params = dict(request.GET)
#     if params["action"][0] == "is":
#         metadata_records = MetadataRecord.objects.filter(central_sample_id=params["central_sample_id"][0])
#     else:
#         metadata_records = MetadataRecord.objects.filter(central_sample_id__contains=params["central_sample_id"][0])
#     serializer = MetadataRecordSerializer(metadata_records, many=True)
#     return Response(serializer.data)


@api_view(["POST"])
def create(request):
    serializer = MetadataRecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
