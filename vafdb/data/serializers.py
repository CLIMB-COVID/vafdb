from rest_framework import serializers
from data.models import Metadata, VAF



class VAFSerializer(serializers.ModelSerializer):
    class Meta:
        model = VAF
        exclude = ("id", "metadata")



class MetadataSerializer(serializers.ModelSerializer):
    vaf = VAFSerializer(many=True)


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
