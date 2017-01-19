from django.db import models
from .attrs import AttributeA


class AttrributeAField(models.IntegerField, AttributeA):
    def __init__(self, *args, **kwargs):
        super(AttrributeAField, self).__init__(*args, **kwargs)

