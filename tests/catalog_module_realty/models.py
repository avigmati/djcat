from django.db import models

from djcat.register import CatalogItem

from catalog.models import BaseAd

from .fields import BuildingTypeField, RoomField


@CatalogItem('Куплю квартиру')
class FlatBuy(BaseAd):
    building_type = BuildingTypeField(choices=BuildingTypeField.get_choices_for_model_field())
    room = RoomField(choices=RoomField.get_choices_for_model_field())
