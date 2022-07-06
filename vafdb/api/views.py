from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from data.models import MetadataRecord, VAFRecord
from .serializers import MetadataRecordSerializer, VAFRecordSerializer


@api_view(["POST"])
def create(request):
    # Serializer validates input data
    serializer = MetadataRecordSerializer(data=request.data)
    
    # If data is valid, save to the database. If invalid, return errors
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update(request):
    # TODO: use filter or use get?
    # TODO: check if published_date included
    instance = MetadataRecord.objects.filter(published_name=request.data["published_name"]).first()
    
    if not instance:
        return Response(
            {"detail" : f"MetadataRecord with published_name {request.data['published_name']} does not exist"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Serializer validates input data
    serializer = MetadataRecordSerializer(instance=instance, data=request.data, partial=True)
    
    if serializer.is_valid():
        # Calling .save() in this case will use the update method of the serializer class
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_central_sample_id(request, central_sample_id):
    instance = MetadataRecord.objects.filter(central_sample_id=central_sample_id)
    serializer = MetadataRecordSerializer(instance, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_run_name(request, run_name):
    instance = MetadataRecord.objects.filter(run_name=run_name)
    serializer = MetadataRecordSerializer(instance, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_published_name(request, published_name):
    instance = MetadataRecord.objects.filter(published_name=published_name)
    serializer = MetadataRecordSerializer(instance, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_position(request, position):
    vaf_records = VAFRecord.objects.select_related('metadata_record').filter(position=position)
    serializer = VAFRecordSerializer(vaf_records, many=True)
    # metadata_records = MetadataRecord.objects.prefetch_related('vafs').filter(vafs__position=position)
    # serializer = MetadataRecordSerializer(metadata_records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete(request, published_name):
    delete_response = MetadataRecord.objects.filter(published_name=published_name).delete()
    return Response(
        {"detail" : delete_response},
        status=status.HTTP_200_OK
    )
