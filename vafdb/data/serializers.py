from rest_framework import serializers
from data.models import Metadata, VAF


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        exclude = ("created", )


class VAFListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = super().to_representation(data)
        
        transformed_data = {}
        for record in data:
            record = dict(record)
            id = record["metadata"]["id"]
            md = record.pop("metadata")
            md.pop("id")

            if not id in transformed_data:
                transformed_data[id] = md
                transformed_data[id]["vaf"] = [record]
            else:
                transformed_data[id]["vaf"].append(record)
        
        return transformed_data.values()


class VAFSerializer(serializers.ModelSerializer):
    metadata = MetadataSerializer()

    class Meta:
        model = VAF
        exclude = ("id", "created")
        list_serializer_class = VAFListSerializer
