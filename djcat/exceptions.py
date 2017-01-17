from django.utils.translation import ugettext as _


class CategoryInheritanceError(Exception):
    def __init__(self, invalid_category):
        self.invalid_category = invalid_category
        self.error = "Category '{}' can't be parent because it's endpoint."

    def __repr__(self):
        return self.error.format(self.invalid_category)

    def __str__(self):
        return _(self.error).format(self.invalid_category)


class CategoryRootCheckError(Exception):
    def __init__(self, title):
        self.title = title
        self.error = "Category '{}' can't be root because root category with same name present."

    def __repr__(self):
        return self.error.format(self.title)

    def __str__(self):
        return _(self.error).format(self.title)


class ItemModuleNameNotDefined(Exception):
    def __init__(self, item_class, item_module):
        self.item_class = item_class
        self.item_module = item_module
        self.error = "Module '{}' of item class '{}' not define ITEM_MODULE_NAME."

    def __repr__(self):
        return self.error.format(self.item_module, self.item_class)

    def __str__(self):
        return _(self.error).format(self.item_module, self.item_class)


class ItemModuleNameDuplicate(Exception):
    def __init__(self, module, module_name, item_module):
        self.module = module
        self.module_name = module_name
        self.duplicated_module = item_module
        self.error = "Name '{}' in module '{}' already defined in module '{}'"

    def __repr__(self):
        return self.error.format(self.module_name, self.module, self.duplicated_module)

    def __str__(self):
        return _(self.error).format(self.module_name, self.module, self.duplicated_module)


class ItemNameDuplicate(Exception):
    def __init__(self, item_name, item_module):
        self.item_name = item_name
        self.item_module = item_module
        self.error = "Item name '{}' duplicate in module '{}'"

    def __repr__(self):
        return self.error.format(self.item_name, self.item_module)

    def __str__(self):
        return _(self.error).format(self.item_name, self.item_module)
