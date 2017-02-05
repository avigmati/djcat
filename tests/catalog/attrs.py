from djcat.attrs import catalog_attribute, NumericAttribute


@catalog_attribute(name='price', verbose_name='Price', key='pr')
class PriceAttribute(NumericAttribute):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
