import importlib

from .exceptions import *


# def load_catalog():
#     return CatalogItem.REGISTRY


class CatalogItem:
    """
    Decorator class, register all catalog modules and his item classes and store in REGISTRY
    """

    REGISTRY = {}

    def __init__(self, name):
        self.verbose_name = name

    def __call__(self, cls):
        self.register(cls)
        return cls

    def register(self, cls):
        """
        Register item modules and its item classes.
        :param cls: Class object
        :return: Class object
        """
        module_name, module = self.register_module(cls)
        self.__class__.REGISTRY[module_name] = self.register_item(module, cls)
        self.load_items_attributes()


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
                    raise ItemModuleNameNotDefined(cls, module)
                else:
                    verbose_name = getattr(module, 'ITEM_MODULE_VERBOSE_NAME', name)
            else:
                raise ItemModuleNameNotDefined(cls, mnames[0])

        # check duplicates
        for mname, mprops in self.__class__.REGISTRY.items():
            if not cls.__module__ == mprops['module']:
                if mname == name:
                    raise ItemModuleNameDuplicate(cls.__module__, name, mprops['module'])
                if mprops['verbose_name'] == verbose_name:
                    raise ItemModuleNameDuplicate(cls.__module__, verbose_name, mprops['module'])

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
        # check duplicates
        if self.verbose_name in [x[1]['verbose_name'] for x in module['items'].items()]:
            raise ItemNameDuplicate(self.verbose_name, module['module'])
        return {'verbose_name': self.verbose_name, 'class_name': cls.__name__,
                'class': '{}.{}'.format(module['module'], cls.__name__), '_class': cls, 'attrs': {}}

    def load_items_attributes(self):
        """
        Load attributes of catalog items
        :return:
        """
        for m in self.__class__.REGISTRY.items():
            for i in m[1]['items'].items():
                for f in i[1]['_class']._meta.fields:
                    if getattr(f, '_is_djcat_attr', False):
                        a = f._attr_class()
                        if not a.attr_key:
                            raise ItemAttributeKeyNotPresent(a.__class__)
                        if not a.attr_name:
                            raise ItemAttributeNameNotPresent(a.__class__)
                        if not a.attr_verbose_name:
                            raise ItemAttributeVerboseNameNotPresent(a.__class__)
                        i[1]['attrs'].update({
                            f.get_name(): a.get_values_for_registry(self.__class__.REGISTRY)
                        })


    # def get_items_attributes(self):
    #     for m in self.__class__.REGISTRY.items():
    #         for i in m[1]['items'].items():
    #             for f in i[1]['_class']._meta.fields:
    #                 if getattr(f, '_attr_class', None):
    #                     a = f._attr_class()
    #                     i[1]['attrs'].update({
    #                         f.get_name(): a.get_values_for_registry(self.__class__.REGISTRY)
    #                     })
    #
    # def get_attr(self, attr_class):
    #     attr = attr_class
    #     attr.validate(self.__class__.REGISTRY)
    #     return {
    #         'type': attr.get_type(),
    #         'verbose_name': attr.get_verbose_name(),
    #         'key': attr.get_key(),
    #         'class': attr.get_class(),
    #         '_class': attr_class
    #     }

