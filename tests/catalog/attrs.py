from djcat.attrs import SimplyAttribute, catalog_attribute


# @catalog_attribute(name='price', verbose_name='Цена', key='pr')
# @catalog_attribute(name='price', verbose_name='Цена')
# @catalog_attribute()
class PriceAttribute(SimplyAttribute):
    attr_key = 'pr'
    attr_name = 'price'
    attr_verbose_name = 'Цена'

