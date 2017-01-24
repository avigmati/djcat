from django.utils.html import format_html

from mptt.admin import MPTTModelAdmin

from .forms import CategoryForm


class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm

    list_display = ('name', 'is_active', 'is_unique_in_path', 'is_endpoint')
    list_display_links = ('name', 'is_active', 'is_unique_in_path', 'is_endpoint')

    def name(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            instance.name,  # Or whatever you want to put here
        )
