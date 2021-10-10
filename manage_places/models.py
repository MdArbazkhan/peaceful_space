from django.db import models

# Create your models here.
class PlacesData(models.Model):
    place_id = models.CharField(max_length=10,default=None)
    city_name = models.CharField(max_length=30,default=None)
    place_name = models.CharField(max_length=50,default=None)
    place_type = models.CharField(max_length=20,default=None)
    place_upvote = models.IntegerField(default=None)
    approval_status = models.BooleanField(default=False)
    image_url = models.TextField(default=None)
    map_url = models.TextField(default=None)

class FileModel(models.Model):
    file = models.FileField(upload_to='uploaded_files/', default='')
    file_id = models.CharField(max_length=10,default=None)