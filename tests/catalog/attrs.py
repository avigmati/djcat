from djcat.attrs import NumericAttribute


class PriceAttribute(NumericAttribute):
    attr_key = 'pr'
    attr_name = 'price'
    attr_verbose_name = 'Price'
