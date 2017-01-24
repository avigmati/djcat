from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *
from djcat.register import CatalogItem


def catalog_attribute(name=None, key=None, verbose_name=None):
    """
    Decorator for define attribute class, Example:
     from djcat.attrs import BaseAttribute, catalog_attribute

        @catalog_attribute(name='Area', verbose_name='Area', key='ar')
        class AreaAttribute(SimplyAttribute):
            pass

    :param name: String, attribute name
    :param key: String, unique attribute key
    :param verbose_name: String, attribute verbose name
    :return: Class
    """
    def decorate(cls):
        if key:
            setattr(cls, 'attr_key', key)
        if name:
            setattr(cls, 'attr_name', name)
        if verbose_name:
            setattr(cls, 'attr_verbose_name', verbose_name if verbose_name else name)
        return cls
    return decorate


def djcat_attr():
    """
    Decorator for set attribute class (_attr_class) variable in model field class
    :return: Class
    """
    def decorate(cls):
        for b in cls.__bases__:
            if getattr(b, '_is_djcat_attr', None) and getattr(b, 'attr_key', None):
                setattr(cls, '_attr_class', b)
        return cls
    return decorate


class BaseAttribute:
    """
    Base item attribute class.
     Subclasses must define attributes:
     attr_type - attribute type
     attr_key - unique key, don't repeat anywhere!
     attr_name - attribute name
     attr_verbose_name = attribute verbose name, it shows user
    """
    _is_djcat_attr = True
    attr_key = None
    attr_name = None
    attr_verbose_name = None
    attr_type = None

    def __init__(self, *args, **kwargs):
        if self.__class__.attr_type not in settings.DJCAT_ATTR_TYPES:
            raise ItemAttributeUnknownType(self.__class__, self.__class__.attr_type)

    def get_type(self):
        """
        Return attribute type
        :return: String
        """
        return self.__class__.attr_type

    def get_class(self):
        """
        Return attribute class path
        :return: String
        """
        return '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)

    def get_key(self):
        """
        Return attribute key
        :return: String
        """
        return self.__class__.attr_key

    def get_name(self):
        """
        Return attribute name
        :return: String
        """
        return self.__class__.attr_name

    def get_verbose_name(self):
        """
        Return attribute verbose name
        :return: String
        """
        return self.__class__.attr_verbose_name

    def get_values_for_registry(self, registry):
        """
        Return attribute values dictionary for write to CatalogItem.REGISTRY
        :param registry: CatalogItem.REGISTRY
        :return: Dictionary
        """
        self.validate(registry)
        return {
            'type': self.get_type(),
            'verbose_name': self.get_verbose_name(),
            'key': self.get_key(),
            'class': self.get_class(),
            '_class': self
        }

    def validate(self, registry):
        self.check_attr_key(registry)

    def check_attr_key(self, registry):
        """
        Check attribute key for duplicates in registry
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for a in i[1]['attrs'].items():
                    if a[1]['key'] == self.attr_key:
                        raise ItemAttributeKeyDuplicate(a[1]['class'], self.__class__, self.attr_key)


class SimplyAttribute(BaseAttribute):
    attr_type = 'simply'


class ChoiceAttribute(BaseAttribute):
    """
    Attribute with choices. Choices must be declared in subclass and must contain slugs as third element, example:
        @catalog_attribute(name='building_type', verbose_name='Тип строения', key='rbt')
        class BuildingTypeAttribute(ChoiceAttribute):
            attr_choices = (
                (1, 'Кирпичный', 'kirpichnuy'),
                (2, 'Панельный', 'panelnuy'),
                (3, 'Блочный', 'blochnuy'),
                (4, 'Монолитный', 'monolitnuy'),
                (5, 'Деревянный', 'derevyanuy'),
            )
    """
    attr_type = 'choice'
    attr_choices = None

    def __init__(self):
        super().__init__()
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)

    @classmethod
    def get_choices_for_model_field(cls):
        """
        Return choices for model field
        :return: List
        """
        return [c[0:2] for c in cls.attr_choices]

    def get_choices_slugs(self):
        """
        Return choices slugs
        :return: List
        """
        return [c[-1] for c in self.__class__.attr_choices]

    def get_values_for_registry(self, registry):
        values = super().get_values_for_registry(registry)
        slugs = self.get_choices_slugs()
        self.check_self_choices_slugs(slugs)
        self.check_catalog_item_choices_slugs(slugs, registry)
        self.check_categories_slugs(slugs)
        self.check_items_slugs(slugs, registry)
        values.update({'choices': slugs})
        return values

    def check_self_choices_slugs(self, slugs):
        """
        Check for slug duplicates in attribute class choices
        :param slugs: List - slugs
        :return:
        """
        for s in slugs:
            if settings.DJCAT_ITEM_SLUG_DELIMETER in s:
                raise ItemAttributeChoicesSlugNotValid(self)

        if not len(set(slugs)) == len(slugs):
            raise ItemAttributeChoicesSlugsDuplicate(self)

    def check_catalog_item_choices_slugs(self, slugs, registry):
        """
        Check for slug duplicates in catalog item class all choices
        :param slugs: List - slugs
        :param registry: Dictionary - CatalogItem.REGISTRY
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for a in [a for a in i[1]['attrs'].items() if a[1]['type'] == 'choice']:
                    choices = a[1].get('choices')
                    if len(set(slugs) & set(choices)):
                        raise ItemAttributeChoicesSlugsDuplicateInCatalogItem(self, a[1].get('_class'))

    def check_categories_slugs(self, slugs):
        """
        Check for slug duplicates with categories slugs
        :param slugs: List - slugs
        :return:
        """
        for node in self.CategoryModel.objects.all():
            if node.slug in slugs:
                raise ItemAttributeChoicesSlugsDuplicateWithcCategory(self, node)

    def check_items_slugs(self, slugs, registry):
        """
        Check for slug duplicates with all item instances slugs
        :param slugs: List - slugs
        :param registry: Dictionary - CatalogItem.REGISTRY
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for slug in slugs:
                    try:
                        item = i[1]['_class'].objects.get(slug=slug)
                        raise ItemAttributeChoicesSlugsDuplicateItemInstanceSlug(self, item)
                    except ObjectDoesNotExist:
                        pass
