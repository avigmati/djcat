from django.db import models

from djcat.models import DjcatCategory, DjcatItem

from .fields import PriceField


class Category(DjcatCategory):
    pass


class BaseAd(DjcatItem):
    price = PriceField(verbose_name="Price")

    def create_name(self):
        return self.name
