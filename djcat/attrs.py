from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *


class BaseAttrPath:
    """
    Base for attribute and query classes. Need for proper multiple inheritance.
    http://stackoverflow.com/questions/8688114/python-multi-inheritance-init
    """
    def __init__(self, *args, **kwargs):
        pass


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


class BaseAttribute(BaseAttrPath):
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
        super().__init__(*args, **kwargs)

    @classmethod
    def check(cls):
        if cls.attr_type not in settings.DJCAT_ATTR_TYPES:
            raise ItemAttributeUnknownType(cls, cls.attr_type)
        if not cls.attr_key:
            raise ItemAttributeKeyNotPresent(cls)
        if not cls.attr_name:
            raise ItemAttributeNameNotPresent(cls)
        if not cls.attr_verbose_name:
            raise ItemAttributeVerboseNameNotPresent(cls)

    @classmethod
    def get_class(cls):
        """
        Return attribute class path
        :return: String
        """
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @classmethod
    def values_for_registry(cls, registry):
        """
        Return attribute values dictionary for write to CatalogItem.REGISTRY
        :param registry: CatalogItem.REGISTRY
        :return: Dictionary
        """
        cls.validate(registry)
        return {
            'type': cls.attr_type,
            'verbose_name': cls.attr_verbose_name,
            'key': cls.attr_key,
            'class': cls.get_class(),
            '_class': cls
        }

    @classmethod
    def validate(cls, registry):
        cls.check_attr_key(registry)

    @classmethod
    def check_attr_key(cls, registry):
        """
        Check attribute key for duplicates in registry
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for a in i[1]['attrs'].items():
                    if a[1]['key'] == cls.attr_key:
                        raise ItemAttributeKeyDuplicate(a[1]['class'], cls, cls.attr_key)


class SimplyAttribute(BaseAttribute):
    attr_type = 'simply'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def check(cls):
        super(ChoiceAttribute, cls).check()
        if not type(cls.attr_choices) == tuple:
            raise Exception('attr_choices must be tuple type')

    @classmethod
    def get_choices_for_model_field(cls):
        """
        Return choices for model field
        :return: List
        """
        return [c[0:2] for c in cls.attr_choices]

    @classmethod
    def choices_slugs_for_registry(cls, registry):
        """
        Return choices slugs
        :return: List
        """
        slugs = [c[-1] for c in cls.attr_choices]
        cls.check_cls_choices_slugs(slugs)
        cls.check_catalog_item_choices_slugs(slugs, registry)
        cls.check_categories_slugs(slugs)
        cls.check_items_slugs(slugs, registry)
        return slugs

    @classmethod
    def values_for_registry(cls, registry):
        values = super(ChoiceAttribute, cls).values_for_registry(registry)
        slugs = cls.choices_slugs_for_registry(registry)
        values.update({'choices': slugs})
        return values

    @classmethod
    def check_cls_choices_slugs(cls, slugs):
        """
        Check for slug duplicates in attribute class choices
        :param slugs: List - slugs
        :return:
        """
        for s in slugs:
            if settings.DJCAT_ITEM_SLUG_DELIMETER in s:
                raise ItemAttributeChoicesSlugNotValid(cls)

        if not len(set(slugs)) == len(slugs):
            raise ItemAttributeChoicesSlugsDuplicate(cls)

    @classmethod
    def check_catalog_item_choices_slugs(cls, slugs, registry):
        """
        Check for slug clashes in catalog item class all choices
        :param slugs: List - slugs
        :param registry: Dictionary - CatalogItem.REGISTRY
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for a in [a for a in i[1]['attrs'].items() if a[1]['type'] == 'choice']:
                    choices = a[1].get('choices')
                    if len(set(slugs) & set(choices)):
                        raise ItemAttributeChoicesSlugsDuplicateInCatalogItem(cls, a[1].get('_class'))

    @classmethod
    def check_categories_slugs(cls, slugs):
        """
        Check for slug clashes with categories slugs
        :param slugs: List - slugs
        :return:
        """
        CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        for node in CategoryModel.objects.all():
            if node.slug in slugs:
                raise ItemAttributeChoicesSlugsDuplicateWithcCategory(cls, node)

    @classmethod
    def check_items_slugs(cls, slugs, registry):
        """
        Check for slug clashes with all item instances slugs
        :param slugs: List - slugs
        :param registry: Dictionary - CatalogItem.REGISTRY
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for slug in slugs:
                    try:
                        item = i[1]['_class'].objects.get(slug=slug)
                        raise ItemAttributeChoicesSlugsDuplicateItemInstanceSlug(cls, item)
                    except ObjectDoesNotExist:
                        pass


class QueryBase(BaseAttrPath):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = kwargs.get('query')

    def parse_query(self):
        """
        Parse query string
        :return: Parsed value
        """
        raise Exception('parse_query() must implement in subclasses')


class NumQuery(QueryBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_query(self):
        if not self.query:
            return None

        val_type = 'range' if '-' in self.query else 'single'

        if val_type == 'single':
            return self.parse_val(self.query)
        else:
            vals = self.query.split('-')
            if not len(vals) == 2:
                return None

            _values = [self.parse_val(v) for v in vals]
            if None in _values:
                return None

            _from, _to = None, None
            for v in _values:
                if 'from' in v:
                    _from = v.get('from')
                if 'to' in v:
                    _to = v.get('to')
            if _from > _to or _from == _to:
                return None

            value = {}
            for v in _values:
                value.update(v)

            return value

    def parse_val(self, val):
        value = {}
        if 'f' not in val and 't' not in val:
            return None
        if 'f' in val:
            try:
                value['from'] = int(val.replace('f', ''))
                return value
            except ValueError:
                return None
        else:
            try:
                value['to'] = int(val.replace('t', ''))
                return value
            except ValueError:
                return None

#
# class ChoiceQuery(QueryBase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def parse_query(self):
#         if not self.query:
#             raise Exception('bad query')
#         t = self.get_query_type()
#         return self.query
#
#     def get_query_type(self):
#         # for x in self.attr.attr_choices:
#         #     if query == x[0] or query == x[2]:
#         #         return cls.__name__
#         return False