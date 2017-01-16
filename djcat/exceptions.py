class CategoryInheritanceError(Exception):
    def __init__(self, invalid_category):
        self.invalid_category = invalid_category

    def __repr__(self):
        return "Category {} can't be parent because it's endpoint.".format(self.invalid_category)

    def __str__(self):
        return "Category {} can't be parent because it's endpoint.".format(self.invalid_category)


class ItemModuleNameNotDefined(Exception):
    def __init__(self, item_class, item_module):
        self.item_class = item_class
        self.item_module = item_module

    def __repr__(self):
        return "Module {} of item class {} not define ITEM_MODULE_NAME."\
            .format(self.item_module, self.item_class)

    def __str__(self):
        return "Module {} of item class {} not define ITEM_MODULE_NAME."\
            .format(self.item_module, self.item_class)
