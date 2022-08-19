from rest_framework import serializers
from data.models import MetadataRecord, VAFRecord


class VAFRecordSerializer(serializers.ModelSerializer):
    # Fields required for both creation and update of records
    required_fields = [
        "reference", 
        "position"
    ]

    class Meta:
        model = VAFRecord
        exclude = ("id", "metadata_record", )

    # Additional custom validation
    def validate(self, data):
        # Check required_fields are provided
        for required_field in self.required_fields:
            if not data.get(required_field):
                raise serializers.ValidationError(f"{required_field} must always be provided")
        return data
    

class MetadataRecordSerializer(serializers.ModelSerializer):
    # Serializer that will handle a list of VAFRecords
    vafs = VAFRecordSerializer(many=True)
    # Fields required for both creation and update of records
    required_fields = [
        "central_sample_id", 
        "run_name", 
        "published_name"
    ]

    class Meta:
        model = MetadataRecord
        exclude = ("id", )

    # Additional custom validation
    def validate(self, data):
        # Check required_fields are provided
        for required_field in self.required_fields:
            if not data.get(required_field):
                raise serializers.ValidationError(f"{required_field} must always be provided")
        # Formatting constraint on the published_name
        if  data["published_name"] != f"{data['central_sample_id']}.{data['run_name']}":
            raise serializers.ValidationError("The published_name field must be central_sample_id.run_name")
        return data

    def create(self, validated_data):
        vafs = validated_data.pop("vafs")
        # Create MetadataRecord object from validated data, and save to database
        metadata = MetadataRecord.objects.create(**validated_data)
        # Create each VAFRecord object with their validated data, and save to database
        for vaf in vafs:
            VAFRecord.objects.create(metadata_record=metadata, **vaf)
        return metadata

    def update(self, instance, validated_data):
        # TODO: vafs
        vafs = validated_data.pop("vafs", None)
        # Update MetadataRecord object with the validated data
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
