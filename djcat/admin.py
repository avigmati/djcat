from django import forms
from django.utils.html import format_html

from mptt.admin import MPTTModelAdmin


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

    class Meta:
        exclude = ['is_root', 'is_endpoint']

    def clean(self):
        cleaned_data = super(CategoryForm, self).clean()
        return cleaned_data


class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm

    list_display = ('title', 'is_active', 'is_unique_in_path', 'is_endpoint')
    list_display_links = ('title', 'is_active', 'is_unique_in_path', 'is_endpoint')

    def title(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            instance.title,  # Or whatever you want to put here
        )
