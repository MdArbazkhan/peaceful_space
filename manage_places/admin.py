from django.contrib import admin
from .models import PlacesData, FileModel

# Register your models here.
admin.site.register(PlacesData)
admin.site.register(FileModel)