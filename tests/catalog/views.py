from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from djcat.path import Path


class Catalog(View):
    def __init__(self):
        super().__init__()

    def get(self, request, *args, **kwargs):
        """
        Route between render category and item
        """
        path = Path(path=kwargs.get('path', None), query=request.GET.get('a'))
        if not path.item:
            return self.render_category(request, path)
        else:
            return self.render_item(request, path)

    def render_category(self, request, path):
        """
        Render catalog category template with post_dict.GET parameters in context
        """
        non_path_query = {x[0]: x[1] for x in request.GET.dict().items() if not x[0] == 'a'}

        if path.category:
            context = {'category': path.category.name}
            context.update(non_path_query)
            for a in path.attrs:
                context.update({a['attribute'].attr_key: a['query_value']})
            return render(request, 'catalog/index.html', context=context)
        else:
            return render(request, 'catalog/index.html', {'category': ''})

    def render_item(self, request, path):
        return render(request, 'catalog/index.html', {'item': path.item.name})

    def post(self, request, *args, **kwargs):
        """
        Emulate catalog search form post. Parse post_dict.POST parameters, build on it url and redirect to get().
        Remember attribute formats! You must prepare your POST values to appropriate attribute format in post_dict.
        """
        post_dict = request.POST.dict()

        path = Path(post_dict=post_dict)
        url = path.url
        if not url:
            url = settings.DJCAT_CATALOG_ROOT_URL
        else:
            url = settings.DJCAT_CATALOG_ROOT_URL + url
        return redirect(url)
