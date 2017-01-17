from django import forms
from django.utils.html import escape
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.translation import ugettext as _

from djcat.models import CatalogItem
from djcat.exceptions import CategoryRootCheckError


class ItemClassWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes_in_use = []

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        selected_html = (option_value in selected_choices) and 'selected="selected"' or ''
        disabled_html = (option_value in self.classes_in_use) and 'disabled' or ''
        if option_value in selected_choices:
            if not option_value == '':
                option_label = '{} {}'.format(option_label, _('(selected)'))
        else:
            option_label = (option_value in self.classes_in_use) and '{} {}'.format(option_label, _('(in use)')) \
                           or option_label
        return '<option value="{}" {} {}>{}</option>'.format(escape(option_value), disabled_html, selected_html,
                                                             conditional_escape(force_text(option_label)))


class ItemClassField(forms.ChoiceField):

    widget = ItemClassWidget

    def __init__(self, choices=(), *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(choices=self.get_choices(), *args, **kwargs)
        self.widget.classes_in_use = [x.item_class for x in self.model.objects.filter(is_active=True)]

    def get_choices(self):
        choices = [('', '')]
        for module, mdict in CatalogItem.REGISTRY.items():
            items = [(x[1]['class'], x[1]['name']) for x in mdict['items'].items()]
            items = sorted(items, key=lambda x: x[1])
            choices.append((mdict['human_name'], tuple(items)))
        return sorted(choices, key=lambda x: x[0])


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = self.Meta.model.objects.filter(is_endpoint=False)
        self.fields['item_class'] = ItemClassField(required=False, model=self.Meta.model)

    class Meta:
        exclude = ['is_root', 'is_endpoint']

    def clean(self):
        cleaned_data = super(CategoryForm, self).clean()

        if not cleaned_data['parent']:
            try:
                self.Meta.model.check_root(cleaned_data['title'], self.Meta.model)
            except CategoryRootCheckError as e:
                self.add_error('title', '')
                self.add_error('parent', '')
                raise forms.ValidationError(e)

        return cleaned_data
