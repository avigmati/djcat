from djcat.attrs import BaseAttribute, catalog_attribute


@catalog_attribute(name='AttributeA', verbose_name='Attribute A', key='aa')
class AttributeA(BaseAttribute):
    pass
