from djcat.attrs import catalog_attribute, SimplyAttribute, NumericQuery


@catalog_attribute(name='price', verbose_name='Цена', key='pr')
class PriceAttribute(SimplyAttribute, NumericQuery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
