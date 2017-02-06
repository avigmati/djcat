from django.db import models

from djcat.register import CatalogItem

from catalog.models import BaseAd

from .fields import BuildingTypeField, RoomsField


@CatalogItem('Flat buy')
class FlatBuy(BaseAd):
    building_type = BuildingTypeField(choices=BuildingTypeField.get_choices_for_model_field())
    room = RoomsField(choices=RoomsField.get_choices_for_model_field())

    def create_name(self):
        if self.room == 1:
            name = 'Studio, '
        else:
            c = [c for c in RoomsField.get_choices_for_model_field() if c[0] == self.room][0]
            r = c[1].split(' ')[0]
            name = '{}-roomed flat, '.format(r)
        self.name = name

