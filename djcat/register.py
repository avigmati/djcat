import importlib

from .exceptions import *


class Item:
    """
    Contain item class REGISTRY entry
    """
    def __init__(self, name, klass, class_obj, verbose_name, attrs):
        self.name = name
        self.klass = klass
        self.class_obj = class_obj
        self.verbose_name = verbose_name
        self.attrs = attrs

    def get_attr_by_key(self, key):
        for a in self.attrs:
            if a.key == key:
                return a


class ItemAttribute:
    """
    Contain item class attribute REGISTRY entry
    """
    def __init__(self, name, klass, class_obj, verbose_name, type, key, choices):
        self.name = name
        self.klass = klass
        self.class_obj = class_obj
        self.verbose_name = verbose_name
        self.type = type
        self.key = key
        self.choices = choices


class CatalogItem:
    """
    Decorator class, collect all catalog modules and his item classes in cls.REGISTRY
    """

    REGISTRY = {}
    ATTRS = {}

    def __init__(self, name):
        self.verbose_name = name

    def __call__(self, cls):
        self.register(cls)
        return cls

    def register(self, cls):
        """
        Register item modules and its item classes.
        :param cls: Class object
        :return:
        """
        module_name, module = self.register_module(cls)
        self.__class__.REGISTRY[module_name] = self.register_item(module, cls)

    def register_module(self, cls):
        """
        Populate REGISTRY with module of given class
        :param cls: Class object
        :return: name: String - module name, module: Dictionary, module data
        """
        name, verbose_name, _module = self.get_module(cls)
        if self.__class__.REGISTRY.get(name):
            module = self.__class__.REGISTRY[name]
        else:
            module = {'module': cls.__module__, 'verbose_name': verbose_name, 'items': {}, '_module': _module}
        return name, module

    def get_module(self, cls):
        """
        Return given class item module name (ITEM_MODULE_NAME)
        :param cls: Class object
        :return: String
        """
        try:
            module = importlib.import_module(cls.__module__)
            name = module.ITEM_MODULE_NAME
            verbose_name = getattr(module, 'ITEM_MODULE_VERBOSE_NAME', name)
        except AttributeError:
            mnames = cls.__module__.split('.')
            if len(mnames) > 1:
                module = importlib.import_module(mnames[0])
                try:
                    name = module.ITEM_MODULE_NAME
                except AttributeError:
                    raise BadModule("Module '{}' of item class '{}' is not define ITEM_MODULE_NAME."
                                    .format(module, cls))
                else:
                    verbose_name = getattr(module, 'ITEM_MODULE_VERBOSE_NAME', name)
            else:
                raise BadModule("Module '{}' of item class '{}' is not define ITEM_MODULE_NAME.".format(module, cls))

        # check duplicates
        for mname, mprops in self.__class__.REGISTRY.items():
            if not cls.__module__ == mprops['module']:
                if mname == name:
                    raise BadModule("Name '{}' of module '{}' already defined in module '{}'."
                                    .format(name, cls.__module__, mprops['module']))
                if mprops['verbose_name'] == verbose_name:
                    raise BadModule("Verbose name '{}' of module '{}' already defined in module '{}'."
                                    .format(name, cls.__module__, mprops['module']))

        return name, verbose_name, module

    def register_item(self, module, cls):
        """
        Populate module items with given class
        :param module: Dictionary. Module data
        :param cls: Class object
        :return: Dictionary. Module data
        """
        item_props = self.get_item_class_props(module, cls)
        class_name = item_props.pop('class_name')
        module['items'].update({class_name: item_props})
        return module

    def get_item_class_props(self, module, cls):
        """
        Return given class properties
        :param cls: Class object
        :return: Dictionary
        """
        # check duplicate verbose name
        if self.verbose_name in [x[1]['verbose_name'] for x in module['items'].items()]:
            raise BadItem("Item class verbose name '{}' duplicate in module '{}'."
                          .format(self.verbose_name, module['module']))
        return {'verbose_name': self.verbose_name, 'class_name': cls.__name__,
                'class': '{}.{}'.format(module['module'], cls.__name__), '_class': cls, 'attrs': {}}

    @classmethod
    def load_items_attributes(cls):
        """
        Load attributes of catalog items
        :return:
        """
        for m in cls.REGISTRY.items():
            for i in m[1]['items'].items():
                for f in i[1]['_class']._meta.fields:
                    attr = getattr(f, '_attr_class', None)
                    if attr:
                        i[1]['attrs'].update({
                            attr.attr_name: attr.values_for_registry(cls.REGISTRY, i[1])
                        })

    @classmethod
    def get_item_by_class(cls, klass):
        """
        Return item by 'class' attr
        :param klass: String - item class path
        :return: Item
        """
        for m in cls.REGISTRY.items():
            for i in m[1]['items'].items():
                if i[1].get('class') == klass:
                    item = Item(name=i[0], klass=klass, class_obj=i[1]['_class'], verbose_name=i[1]['verbose_name'],
                                attrs=cls.get_item_attrs(i[1]['attrs']))
                    return item
        return None

    @classmethod
    def get_item_attrs(cls, registry_dict):
        """
        Reeturn list of item attributes
        :param registry_dict: Dict - item attrs from REGISTRY
        :return: list
        """
        attrs = []
        for a in registry_dict.items():
            attrs.append(ItemAttribute(name=a[0], klass=a[1]['class'], class_obj=a[1]['_class'],
                                       verbose_name=a[1]['verbose_name'], type=a[1]['type'], key=a[1]['key'],
                                       choices=a[1]['choices'] if a[1].get('choices') else None))
        return attrs


