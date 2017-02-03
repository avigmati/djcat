# from djcat.attrs import catalog_attribute, NumericAttribute, NumericQuery
from djcat.attrs import catalog_attribute, NumericAttribute


@catalog_attribute(name='price', verbose_name='Цена', key='pr')
class PriceAttribute(NumericAttribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
