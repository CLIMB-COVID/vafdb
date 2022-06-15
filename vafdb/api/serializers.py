from rest_framework import serializers
from base.models import MetadataRecord, VAFRecord


class VAFRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VAFRecord
        fields = (
            "reference", 
            "position", 
            "coverage", 
            "num_a",
            "num_c",
            "num_g",
            "num_t",
            "num_ds"
        )
        

class MetadataRecordSerializer(serializers.ModelSerializer):
    vafs = VAFRecordSerializer(many=True) # TODO read up on serialisers and how this works

    class Meta:
        model = MetadataRecord
        fields = [
            "pathogen",
            "central_sample_id",
            "run_name",
            "published_name",
            "collection_date",
            "published_date",
            "modified_date",
            "num_vafs",
            "fasta_path",
            "bam_path",
            "lineage",
            "primer_scheme",
            "vafs"
        ]
    
    def create(self, validated_data):
        vafs_data = validated_data.pop("vafs")
        metadata = MetadataRecord.objects.create(**validated_data)
        for vaf_data in vafs_data:
            VAFRecord.objects.create(metadata_record=metadata, **vaf_data)
        return metadata
