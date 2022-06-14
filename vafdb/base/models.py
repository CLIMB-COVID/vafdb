from django.db import models

# Create your models here.

class MetadataRecord(models.Model):
    central_sample_id = models.CharField(max_length=100)
    num_vafs = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)