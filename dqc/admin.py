from django.contrib import admin
from . import models

admin.site.register(models.DataType)
admin.site.register(models.DataQualityDimension)
admin.site.register(models.DataValidationConstraint)
