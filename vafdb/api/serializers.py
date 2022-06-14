from rest_framework import serializers
from base.models import MetadataRecord


class MetadataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataRecord
        fields = "__all__"