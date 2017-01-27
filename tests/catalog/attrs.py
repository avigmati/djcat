from djcat.attrs import SimplyAttribute, NumQuery


class PriceAttribute(SimplyAttribute, NumQuery):
    attr_key = 'pr'
    attr_name = 'price'
    attr_verbose_name = 'Цена'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

