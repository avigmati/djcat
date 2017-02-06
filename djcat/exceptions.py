from django.utils.translation import ugettext as _

from . import settings


class BadModule(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class BadItem(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class BadAttribute(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class CategoryInheritanceError(Exception):
    def __init__(self, invalid_category):
        self.invalid_category = invalid_category
        self.error = "Category '{}' can't be parent because it's endpoint."

    def __repr__(self):
        return self.error.format(self.invalid_category)

    def __str__(self):
        return _(self.error).format(self.invalid_category)


class CategoryRootCheckError(Exception):
    def __init__(self, name):
        self.name = name
        self.error = "Category '{}' can't be root because root category with same name present."

    def __repr__(self):
        return self.error.format(self.name)

    def __str__(self):
        return _(self.error).format(self.name)


class CategorySlugClashWithAttr(Exception):
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug
        self.error = "Category with name '{}' and slug '{}' clashes with attr slug."

    def __repr__(self):
        return self.error.format(self.name, self.slug)

    def __str__(self):
        return _(self.error).format(self.name, self.slug)


class PathNotValid(Exception):
    def __init__(self, path):
        self.path = path
        self.error = "Path '{}' not valid."

    def __repr__(self):
        return self.error.format(self.path)

    def __str__(self):
        return self.error.format(self.path)


class PathNotFound(Exception):
    def __init__(self, path):
        self.path = path
        self.error = "Path '{}' not found."

    def __repr__(self):
        return self.error.format(self.path)

    def __str__(self):
        return self.error.format(self.path)

class ItemNameNotValid(Exception):
    def __init__(self, item_name):
        self.item_name = item_name
        self.error = "Item name '{}' should not contain '{}'."

    def __repr__(self):
        return self.error.format(self.item_name, settings.DJCAT_ITEM_SLUG_DELIMITER)

    def __str__(self):
        return _(self.error).format(self.item_name, settings.DJCAT_ITEM_SLUG_DELIMITER)
