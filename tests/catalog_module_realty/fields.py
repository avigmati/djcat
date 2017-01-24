from django.db import models

from djcat.attrs import djcat_attr

from .attrs import BuildingTypeAttribute, RoomAttribute


@djcat_attr()
class BuildingTypeField(models.IntegerField, BuildingTypeAttribute):
    pass


@djcat_attr()
class RoomField(models.IntegerField, RoomAttribute):
    pass

