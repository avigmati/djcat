from django.db import models

from djcat.attrs import djcat_attr

from .attrs import BuildingTypeAttribute


@djcat_attr()
class BuildingTypeField(models.IntegerField, BuildingTypeAttribute):
    pass

