from pprint import pprint
from django.shortcuts import render, HttpResponse


def test_v(request):
    from djcat.models import CatalogItem
    pprint(CatalogItem.REGISTRY)

    # from catalog.attrs import PriceAttribute
    # from catalog_item_realty.models import FlatBuy
    # pa = PriceAttribute()
    #
    # from catalog.models import Category
    # c = Category.objects.get(pk=1)
    # # aa = FlatBuy.objects.create(name='test', slug='test', price=100, category=c)
    # aa = FlatBuy.objects.get(pk=1)

    return HttpResponse('ok')
