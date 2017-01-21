from django.db import models

from djcat.attrs import djcat_attr

from .attrs import PriceAttribute


@djcat_attr()
class PriceField(models.IntegerField, PriceAttribute):
    pass
