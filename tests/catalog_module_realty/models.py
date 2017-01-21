from django.db import models

from djcat.register import CatalogItem

from catalog.models import BaseAd

from .fields import BuildingTypeField


@CatalogItem('Куплю квартиру')
class FlatBuy(BaseAd):
    building_type = BuildingTypeField(choices=BuildingTypeField.get_choices_for_model_field())
