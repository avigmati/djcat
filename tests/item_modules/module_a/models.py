from django.db import models

from djcat.models import DjcatItem, CatalogItem

from .fields import AttrributeAField


@CatalogItem('Item A')
class ItemA(DjcatItem):
    attribute_a_field = AttrributeAField(verbose_name='Attribute A', null=True)
