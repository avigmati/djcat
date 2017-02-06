from django.db import models

from .attrs import BuildingTypeAttribute, RoomsAttribute


class BuildingTypeField(models.IntegerField, BuildingTypeAttribute):
    pass


class RoomsField(models.IntegerField, RoomsAttribute):
    pass
