from rest_framework import serializers
from data.models import Metadata, VAF
from django.db import models



class MetadataSerializer(serializers.ModelSerializer):
    # vaf = VAFSerializer(many=True)


    class Meta:
        model = Metadata
        exclude = ("id", )


    def create(self, validated_data):
        vafs = validated_data.pop("vaf")

        # Create Metadata object from validated data, and save to database
        metadata = Metadata.objects.create(**validated_data)
        
        # Create each VAF object with their validated data, and save to database
        for vaf in vafs:
            VAF.objects.create(metadata=metadata, **vaf)
        
        return metadata



class VAFListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = super().to_representation(data)
        metadata = {}
        for record in data:
            pair = (
                record["metadata"]["central_sample_id"], 
                record["metadata"]["run_name"]
            )
            record = dict(record)
            md = record.pop("metadata")
            if not pair in metadata:
                metadata[pair] = md
                metadata[pair]["vaf"] = [record]
            else:
                metadata[pair]["vaf"].append(record)
        return metadata.values()



class VAFSerializer(serializers.ModelSerializer):
    metadata = MetadataSerializer()


    class Meta:
        model = VAF
        exclude = ("id", )
        list_serializer_class = VAFListSerializer
