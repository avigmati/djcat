import json

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from . import settings
from .exceptions import *
from .register import CatalogItem


class AttributeRegistry(type):

    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2:
            if cls.is_attr():
                if not cls.is_field():
                    cls.check_attr()
                    CatalogItem.ATTRS.update({cls.attr_key: cls})
                else:
                    cls.mark_filed_as_attr()
        super(AttributeRegistry, cls).__init__(name, bases, clsdict)

    def is_attr(cls, klass=None):
        obj = klass if klass else cls
        key = getattr(obj, 'attr_key', None)
        name = getattr(obj, 'attr_name', None)
        type = getattr(obj, 'attr_type', None)
        verb_name = getattr(obj, 'attr_verbose_name', None)
        return key and name and type and verb_name

    def is_field(cls):
        for b in cls.__bases__:
            if b.__module__.startswith('django.db.models'):
                return True
        return False

    def check_attr(cls):
        # check key duplicates
        if CatalogItem.ATTRS.get(cls.attr_key):
            raise BadAttribute("Attribute key '{}' duplicate in classes: '{}', '{}'."
                               .format(cls.attr_key, cls, CatalogItem.ATTRS.get(cls.attr_key)))
        # self.check
        cls.check()

    def mark_filed_as_attr(cls):
        for b in cls.__bases__:
            if cls.is_attr(klass=b):
                setattr(cls, '_attr_class', b)
                return


class BaseAttribute(metaclass=AttributeRegistry):
    """
    Base item attribute class.
     Subclasses must define attributes:
     attr_type - attribute type
     attr_key - unique key, don't repeat anywhere!
     attr_name - attribute name
     attr_verbose_name = attribute verbose name, it shows user
    """
    attr_key = None
    attr_name = None
    attr_verbose_name = None
    attr_type = None

    def __init__(self, *args, **kwargs):
        self.value = kwargs.get('value', None)
        if self.value:
            self.validate_value()
        self.query = kwargs.get('query', None)

    def validate_value(self):
        """Validate value, value must have format defined in subclass"""
        raise NotImplementedError('validate_value() must implement in subclass.')

    def parse_query(self):
        """
        Parse query string
        :return: Parsed value
        """
        raise Exception('parse_query() must implement in subclasses')

    def build_query(self, *args, **kwargs):
        """
        Build query string
        :return: Parsed value
        """
        raise Exception('build_query() must implement in subclasses')

    @classmethod
    def check(cls):
        """
        Perform class attributes check
        """
        NotImplementedError('check() must implement in subclass.')

    @classmethod
    def get_class(cls):
        """
        Return attribute class path
        :return: String
        """
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @classmethod
    def values_for_registry(cls, registry, registry_item):
        """
        Return attribute values dictionary for write to CatalogItem.REGISTRY
        :param registry: CatalogItem.REGISTRY
        :return: Dictionary
        """
        return {
            'type': cls.attr_type,
            'verbose_name': cls.attr_verbose_name,
            'key': cls.attr_key,
            'class': cls.get_class(),
            '_class': cls
        }


class NumericAttribute(BaseAttribute):
    attr_type = 'numeric'

    @classmethod
    def check(cls):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_value(self):
        """
        Validate value, value format:
        {'from': numeric value, 'to': numeric value} or {'from': numeric value} or {'to': numeric value}
        """
        if isinstance(self.value, str):
            try:
                self.value = json.loads(self.value)
            except Exception:
                raise Exception('Bad value')

        if not isinstance(self.value, dict):
            raise Exception('Bad value')
        if not 'from' in self.value and not 'to' in self.value:
            raise Exception('Bad value')

    def build_query(self, value=None):
        if not value:
            value = self.value
        f = 'f{}'.format(value.get('from')) if value.get('from') else None
        t = 't{}'.format(value.get('to')) if value.get('to') else None
        s = '{}-{}'.format(f, t) if f and t else '{}'.format(f or t)
        return '{}_{}'.format(self.attr_key, s)

    def parse_query(self):
        """
        Parse numeric query string, string must have format: f100-t10000000 or f255 or t4534
        where f - from, t - to range tokens
        :return: Dict contain parsed string
        """
        if not self.query:
            return None

        val_type = 'range' if '-' in self.query else 'single'

        if val_type == 'single':
            return self._get_val(self.query)
        else:
            vals = self.query.split('-')
            if not len(vals) == 2:
                return None

            _values = [self._get_val(v) for v in vals]
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

    def _get_val(self, val):
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

    def validate_value(self):
        """
        Validate value, value format:
        [1, 2, 3] or [4]
        :return: Query string
        """
        if isinstance(self.value, str):
            try:
                self.value = json.loads(self.value)
            except Exception:
                raise Exception('Bad value')
        if not isinstance(self.value, list):
            raise Exception('Bad value')

    def build_query(self, value=None):
        if not value:
            value = self.value

        if not isinstance(value, list):
            raise Exception('Bad value')

        if not len(value):
            return None

        return '{}_{}'.format(self.attr_key, ','.join([str(x) for x in value]))

    def parse_query(self):
        """
        Parse numeric query string, string must have format: "1,2,3" or "4"
        :return: List of choices values
        """
        if not self.query:
            return None

        val_type = 'enum' if ',' in self.query else 'single'

        choices_values = self.get_choices_values()

        if val_type == 'single':
            try:
                if int(self.query) in choices_values:
                    return int(self.query)
            except Exception:
                return None
            return None
        else:
            vals = [int(x) for x in self.query.split(',')]
            if len([x for x in vals if x not in choices_values]):
                return None
            return vals

    def get_choices_values(self):
        return [x[0] for x in self.__class__.attr_choices]

    @classmethod
    def check(cls):
        if not type(cls.attr_choices) == tuple:
            raise BadAttribute("Attribute '{}' must be tuple.".format(cls))
        cls.check_cls_choices_slugs()

    @classmethod
    def check_cls_choices_slugs(cls):
        """
        Check for slug duplicates in attribute class choices
        """
        slugs = [c[-1] for c in cls.attr_choices]
        for s in slugs:
            if settings.DJCAT_ITEM_SLUG_DELIMITER in s:
                raise BadAttribute("Attribute class '{}' choices slugs should not contain '{}'."
                                   .format(cls, settings.DJCAT_ITEM_SLUG_DELIMITER))
        if not len(set(slugs)) == len(slugs):
            raise BadAttribute("Attribute class '{}' duplicate choices slugs.".format(cls))

    @classmethod
    def get_choices_for_model_field(cls):
        """
        Return choices for model field
        :return: List
        """
        return [c[0:2] for c in cls.attr_choices]

    @classmethod
    def values_for_registry(cls, registry, registry_item):
        values = super(ChoiceAttribute, cls).values_for_registry(registry, registry_item)
        slugs = cls.choices_slugs_for_registry(registry, registry_item)
        values.update({'choices': slugs})
        return values

    @classmethod
    def choices_slugs_for_registry(cls, registry, registry_item):
        """
        Return choices slugs
        :return: List
        """
        slugs = [c[-1] for c in cls.attr_choices]
        cls.check_item_choices_slugs(slugs, registry_item)
        cls.check_categories_slugs(slugs)
        cls.check_item_instances_slugs(slugs, registry)
        return slugs

    @classmethod
    def check_item_choices_slugs(cls, slugs, registry_item):
        """
        Check for slug clashes in catalog item class all attributes choices
        :param slugs: List - slugs
        :param registry_item Registry Item class dict
        """
        for a in [a for a in registry_item['attrs'].items() if a[1]['type'] == 'choice']:
            choices = a[1].get('choices')
            if len(set(slugs) & set(choices)):
                raise BadAttribute("Attribute class '{}' have choices that clashes with choices in same "
                                   "Item attribute class '{}'.".format(cls, a[1].get('_class')))

    @classmethod
    def check_categories_slugs(cls, slugs):
        """
        Check for slug clashes with categories slugs
        :param slugs: List - slugs
        """
        CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        for node in CategoryModel.objects.all():
            if node.slug in slugs:
                raise BadAttribute("Attribute class '{}' have choices that clashes with category instance slug, "
                                   "category instance: '{}'.".format(cls, node))

    @classmethod
    def check_item_instances_slugs(cls, slugs, registry):
        """
        Check for slug clashes with all item instances slugs
        :param slugs: List - slugs
        :param registry: Dictionary - CatalogItem.REGISTRY
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for slug in slugs:
                    try:
                        item = i[1]['_class'].objects.get(slug=slug)
                        raise BadAttribute("Attribute class '{}' have choices that clashes with item instance slug, "
                                           "item.pk: '{}'.".format(cls, item.pk))
                    except ObjectDoesNotExist:
                        pass
