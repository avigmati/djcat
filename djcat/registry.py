import importlib

from .exceptions import ItemModuleNameNotDefined


ITEM_REGISTRY = {}


def get_module_name(cls):
    """
    Return given class item module name (ITEM_MODULE_NAME)
    :param cls: Class object
    :return: String
    """
    try:
        name = cls.__module__.ITEM_MODULE_NAME
    except AttributeError:
        mnames = cls.__module__.split('.')
        if len(mnames) > 1:
            root_module = importlib.import_module(mnames[0])
            try:
                name = root_module.ITEM_MODULE_NAME
            except AttributeError:
                raise ItemModuleNameNotDefined(cls, root_module)
        else:
            raise ItemModuleNameNotDefined(cls, mnames[0])
    return name


def item_register(cls):
    """
    Decorator register item modules and its item classes.
    :param cls: Class object
    :return: Class object
    """
    name = get_module_name(cls)
    if ITEM_REGISTRY.get(name):
        ITEM_REGISTRY[get_module_name(cls)].append(cls)
    else:
        ITEM_REGISTRY[get_module_name(cls)] = [cls]
    return cls
