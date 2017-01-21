from django.contrib import admin

from djcat.admin import CategoryAdmin as DjcatCategoryAdmin

from .models import Category


class CategoryAdmin(DjcatCategoryAdmin):
    def __init__(self, *args, **kwargs):
        super(CategoryAdmin, self).__init__(*args, **kwargs)


admin.site.register(Category, CategoryAdmin)