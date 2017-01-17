class CategoryInheritanceError(Exception):
    def __init__(self, invalid_category):
        self.invalid_category = invalid_category

    def __repr__(self):
        return "Category '{}' can't be parent because it's endpoint.".format(self.invalid_category)

    def __str__(self):
        return "Category '{}' can't be parent because it's endpoint.".format(self.invalid_category)


class ItemModuleNameNotDefined(Exception):
    def __init__(self, item_class, item_module):
        self.item_class = item_class
        self.item_module = item_module

    def __repr__(self):
        return "Module '{}' of item class '{}' not define ITEM_MODULE_NAME."\
            .format(self.item_module, self.item_class)

    def __str__(self):
        return "Module '{}' of item class '{}' not define ITEM_MODULE_NAME."\
            .format(self.item_module, self.item_class)


class ItemModuleNameDuplicate(Exception):
    def __init__(self, module, module_name, item_module):
        self.module = module
        self.module_name = module_name
        self.duplicated_module = item_module

    def __repr__(self):
        return "Name '{}' in module '{}' already defined in module '{}'"\
            .format(self.module_name, self.module, self.duplicated_module)

    def __str__(self):
        return "Name '{}' in module '{}' already defined in module '{}'"\
            .format(self.module_name, self.module, self.duplicated_module)


class ItemNameDuplicate(Exception):
    def __init__(self, item_name, item_module):
        self.item_name = item_name
        self.item_module = item_module

    def __repr__(self):
        return "Item name '{}' duplicate in module '{}'".format(self.item_name, self.item_module)

    def __str__(self):
        return "Item name '{}' duplicate defined in module '{}'".format(self.item_name, self.item_module)
