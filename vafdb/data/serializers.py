from rest_framework import serializers
from data.models import Metadata, VAF


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        exclude = ("id", )


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
        exclude = ("id", "created")
        list_serializer_class = VAFListSerializer
