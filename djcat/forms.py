from django import forms

from djcat.models import CatalogItem



class ItemClassField(forms.ChoiceField):
    def __init__(self, choices=(), *args, **kwargs):
        choices = [(k, k) for k in CatalogItem.REGISTRY.keys()]
        # choice_pairs = [(c[0], c[1]) for c in choices]
        super().__init__(choices=choices, *args, **kwargs)
        # self.widget.uniques = dict([(c[1], c[2]) for c in choices])
    # def clean(self, value):
    #     try:
    #         return value
    #     except:
    #         raise ValidationError


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = self.Meta.model.objects.filter(is_endpoint=False)
        self.fields['item_class'] = ItemClassField()

    class Meta:
        exclude = ['is_root', 'is_endpoint']

    def clean(self):
        cleaned_data = super(CategoryForm, self).clean()
        return cleaned_data