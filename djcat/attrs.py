from django.conf import settings

from djcat.exceptions import ItemAttributeUnknownType, ItemAttributeKeyNotPresent, ItemAttributeKeyDuplicate


def catalog_attribute(name=None, key=None, verbose_name=None):
    def decorate(cls):
        setattr(cls, '_attr_class', cls)
        if not key:
            raise ItemAttributeKeyNotPresent(cls)
        setattr(cls, 'attr_key', key)  # must be unique
        setattr(cls, 'attr_name', name)
        setattr(cls, 'attr_verbose_name', verbose_name if verbose_name else name)
        return cls
    return decorate


def slug_attribute(cls):
    cls._slug_methods = {}
    cls._is_slug = True
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_slug'):
            try:
                getattr(cls, method._slug_validator_func)
            except AttributeError as e:
                raise Exception('slug validator func not exist')
            cls._slug_methods.update({methodname: {'validator_func': method._slug_validator_func}})
    return cls


def slug(*args, **kwargs):
    try:
        validator_func = kwargs.pop('validator')
    except KeyError:
        raise Exception('slug validator not specified')

    def wrapper(func):
        func._slug = True
        func._slug_validator_func = validator_func
        return func
    return wrapper


class BaseAttribute:
    """
    Base item attribute class.
     Subclasses must define attributes:
     DJCAT_ATTRIBUTE_TYPE - unique key, don't repeat anywhere!
     DJCAT_ATTRIBUTE_KEY - unique key, don't repeat anywhere!
     DJCAT_ATTRIBUTE_NAME - attribute name
     DJCAT_ATTRIBUTE_VERBOSE_NAME = attribute verbose name, it shows user

     These attributes can be specified through catalog_attribute decorator, example:

     from djcat.attrs import BaseAttribute, catalog_attribute

        @catalog_attribute(name='Area', verbose_name='Area', key='ar')
        class AreaAttribute(BaseAttribute):
            pass
    """
    attr_key = None
    attr_name = None
    attr_verbose_name = None
    attr_type = None
    _attr_class = None

    def __init__(self, *args, **kwargs):
        if self.__class__.attr_type not in settings.DJCAT_ATTR_TYPES:
            raise ItemAttributeUnknownType(self.__class__._attr_class, self.__class__.attr_type)

    @classmethod
    def get_type(cls):
        """
        Return attribute type
        :return: String
        """
        return cls.attr_type

    @classmethod
    def get_class(cls):
        """
        Return attribute class path
        :return: String
        """
        return '{}.{}'.format(cls._attr_class.__module__, cls._attr_class.__name__)

    @classmethod
    def get_key(cls):
        """
        Return attribute key
        :return: String
        """
        return cls.attr_key

    @classmethod
    def get_name(cls):
        """
        Return attribute name
        :return: String
        """
        return cls.attr_name

    @classmethod
    def get_verbose_name(cls):
        """
        Return attribute verbose name
        :return: String
        """
        return cls.attr_verbose_name

    def get_values_for_registry(self, registry):
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
        if getattr(self, '_is_slug', False):
            self.validate_specials(registry)

    def check_attr_key(self, registry):
        """
        Check attribute key for duplicates in registry
        :return:
        """
        for m in registry.items():
            for i in m[1]['items'].items():
                for a in i[1]['attrs'].items():
                    if a[1]['key'] == self.attr_key:
                        raise ItemAttributeKeyDuplicate(a[1]['class'], self._attr_class, self.attr_key)

    def validate_specials(self, registry):
        """
        Validate special methods of attribute class
        :param registry: Dictionary CatalogItem.REGISTRY
        :return:
        """
        for _, spec_d in self.__class__._specials.items():
            validator = getattr(self.__class__, spec_d['validator_func'])
            validator(self, registry)


class SimplyAttribute(BaseAttribute):
    attr_type = 'simply'

    # def __init__(self, *args, **kwargs):
    #     print(self.__class__.attr_type)


class ItemAttributeChoicesSlugsDuplicate(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' duplicate choices slugs"

    def __repr__(self):
        return self.error.format(self.attr_class)

    def __str__(self):
        return self.error.format(self.attr_class)


@slug_attribute
class ChoiceAttribute(BaseAttribute):
    attr_type = 'choice'
    attr_choices = None

    @classmethod
    def get_choices_for_model_field(cls):
        return [c[0:2] for c in cls.attr_choices]

    def get_choices_slugs(self):
        return [c[-1] for c in self.__class__.attr_choices]

    @slug(validator='choices_slugs_validator')
    def get_choices_slugs_for_registry(self):
        return {'choices': self.get_choices_slugs()}

    def choices_slugs_validator(self, registry):
        self.check_choices_slugs()
        self.check_catalog_item_choices_slugs(registry)
        # check for duplicates in catalog item all choices

        # print()

    def check_choices_slugs(self):
        """
        Check for slug duplicates in attribute class choices
        :return:
        """
        slugs = self.get_choices_slugs()
        if not len(set(slugs)) == len(slugs):
            raise ItemAttributeChoicesSlugsDuplicate(self)

    def check_catalog_item_choices_slugs(self, registry):
        """
        Check for slug duplicates in catalog item class all choices
        :param registry: Dictionary - CatalogItem.REGISTRY
        :return:
        """
        slugs = self.get_choices_slugs()

        for m in registry.items():
            for i in m[1]['items'].items():
                # for a in [a for a in i[1]['attrs'].items() ]:
                for a in [a for a in i[1]['attrs'].items() if a[1]['type'] == 'choice']:
                    print()
                    if a[1]['key'] == self.attr_key:
                        raise ItemAttributeKeyDuplicate(a[1]['class'], self._attr_class, self.attr_key)


    def check_categories(self):
        pass