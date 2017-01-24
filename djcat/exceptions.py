from django.utils.translation import ugettext as _
from django.conf import settings


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
        self.error = "Name '{}' in module '{}' already defined in module '{}'."

    def __repr__(self):
        return self.error.format(self.module_name, self.module, self.duplicated_module)

    def __str__(self):
        return _(self.error).format(self.module_name, self.module, self.duplicated_module)


class ItemNameDuplicate(Exception):
    def __init__(self, item_name, item_module):
        self.item_name = item_name
        self.item_module = item_module
        self.error = "Item class name '{}' duplicate in module '{}'."

    def __repr__(self):
        return self.error.format(self.item_name, self.item_module)

    def __str__(self):
        return _(self.error).format(self.item_name, self.item_module)


class ItemAttributeUnknownType(Exception):
    def __init__(self, attr_class, attr_type):
        self.attr_class = attr_class
        self.attr_type = attr_type
        self.error = "Attribute class '{}' unknown type '{}'."

    def __repr__(self):
        return self.error.format(self.attr_class, self.attr_type)

    def __str__(self):
        return self.error.format(self.attr_class, self.attr_type)


class ItemAttributeKeyNotPresent(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' has no key."

    def __repr__(self):
        return self.error.format(self.attr_class)

    def __str__(self):
        return self.error.format(self.attr_class)


class ItemAttributeKeyDuplicate(Exception):
    def __init__(self, attr_class_dup, attr_class_cur, attr_key):
        self.attr_class_dup = attr_class_dup
        self.attr_class_cur = attr_class_cur
        self.attr_key = attr_key
        self.error = "Attribute key '{}' duplicate in classes: '{}', '{}'."

    def __repr__(self):
        return self.error.format(self.attr_key, self.attr_class_cur, self.attr_class_dup)

    def __str__(self):
        return self.error.format(self.attr_key, self.attr_class_cur, self.attr_class_dup)


class ItemAttributeNameNotPresent(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' has no name."

    def __repr__(self):
        return self.error.format(self.attr_class)

    def __str__(self):
        return self.error.format(self.attr_class)


class ItemAttributeVerboseNameNotPresent(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' has no verbose_name."

    def __repr__(self):
        return self.error.format(self.attr_class)

    def __str__(self):
        return self.error.format(self.attr_class)


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


class ItemAttributeChoicesSlugsDuplicate(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' duplicate choices slugs."

    def __repr__(self):
        return self.error.format(self.attr_class)

    def __str__(self):
        return self.error.format(self.attr_class)


class ItemAttributeChoicesSlugsDuplicateInCatalogItem(Exception):
    def __init__(self, attr_class, another_attr_class):
        self.attr_class = attr_class
        self.another_attr_class = another_attr_class
        self.error = "Attribute class '{}' have choices that duplicates choices in class '{}'."

    def __repr__(self):
        return self.error.format(self.attr_class, self.another_attr_class)

    def __str__(self):
        return self.error.format(self.attr_class, self.another_attr_class)


class ItemAttributeChoicesSlugsDuplicateWithcCategory(Exception):
    def __init__(self, attr_class, category):
        self.attr_class = attr_class
        self.category = category
        self.error = "Attribute class '{}' have choices that clashes with category instance slug, " \
                     "category instance: '{}'."

    def __repr__(self):
        return self.error.format(self.attr_class, self.category)

    def __str__(self):
        return self.error.format(self.attr_class, self.category)


class ItemAttributeChoicesSlugsDuplicateItemInstanceSlug(Exception):
    def __init__(self, attr_class, item):
        self.attr_class = attr_class
        self.item_pk = item.pk
        self.error = "Attribute class '{}' have choices that clashes with item instance slug, item.pk: '{}'."

    def __repr__(self):
        return self.error.format(self.attr_class, self.item_pk)

    def __str__(self):
        return self.error.format(self.attr_class, self.item_pk)


class ItemAttributeChoicesSlugNotValid(Exception):
    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.error = "Attribute class '{}' choices slugs should not contain '{}'."

    def __repr__(self):
        return self.error.format(self.attr_class, settings.DJCAT_ITEM_SLUG_DELIMETER)

    def __str__(self):
        return self.error.format(self.attr_class, settings.DJCAT_ITEM_SLUG_DELIMETER)


class ItemNameNotValid(Exception):
    def __init__(self, item_name):
        self.item_name = item_name
        self.error = "Item name '{}' should not contain '{}'."

    def __repr__(self):
        return self.error.format(self.item_name, settings.DJCAT_ITEM_SLUG_DELIMETER)

    def __str__(self):
        return _(self.error).format(self.item_name, settings.DJCAT_ITEM_SLUG_DELIMETER)
