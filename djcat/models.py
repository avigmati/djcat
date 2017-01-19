import abc
import importlib
import json

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel, TreeForeignKey

from .utils import create_slug, unique_slug
from .exceptions import CategoryInheritanceError, ItemModuleNameNotDefined, ItemModuleNameDuplicate, ItemNameDuplicate, \
    CategoryRootCheckError, ItemAttributeKeyNotPresent, ItemAttributeKeyDuplicate


class BaseDjcat:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __str__(self):
        """Return descriptive instance name"""
        return

    @abc.abstractmethod
    def __unicode__(self):
        """Return descriptive instance name"""
        return

    @abc.abstractmethod
    def get_url(self):
        """Return item url"""
        return

    @abc.abstractmethod
    def create_slug(self, *args, **kwargs):
        """Create item slug"""


class BaseCategoryManager(models.Manager):

    def update_active(self, instance, instance_before):
        """
        Updates children active flag
        :param instance: Model instance
        :param instance_before: Model instance before save()
        :return:
        """
        if instance_before and not instance_before.is_active == instance.is_active:
            instance.get_descendants().update(is_active=instance.is_active)

    def update_paths(self, instance, instance_before):
        """
        Updates tree url paths
        :param instance: Model instance
        :param instance_before: Model instance before save()
        :return:
        """
        # update actual tree branch where instance
        for node in instance.get_family():
            node.available_paths = json.dumps(self.make_url_paths(node))
            node.save(update_process=True)

        # update tree branch where instance was before move
        if instance_before and not instance_before.get_root() == instance.get_root():
            for node in instance_before.get_family():
                node.available_paths = json.dumps(self.make_url_paths(node))
                node.save(update_process=True)

    def update_tree(self, instance, instance_before):
        """
        Update tree branch where instance present, if instance was moved to another branch then update old branch
        :param instance: Model instance
        :param instance_before: Model instance before save()
        :return:
        """
        self.update_active(instance, instance_before)
        self.update_paths(instance, instance_before)

    def make_url_paths(self, node):
        """
        Return category instance (node) paths: full and unique
        :param node: Model instance
        :return: Dictionary paths
        """
        paths = {'full': [], 'unique': []}

        if node.parent:
            paths = node.parent.get_url_paths()
            paths['full'].append(node.slug)
            if node.is_unique_in_path:
                paths['unique'].append(node.slug)
        else:
            paths['full'] = [node.slug]
            if node.is_unique_in_path:
                paths['unique'] = [node.slug]

        return paths


class DjcatCategory(MPTTModel, BaseDjcat):
    title = models.CharField(max_length=400, verbose_name=_('Title'))
    slug = models.SlugField(max_length=420, verbose_name='Slug', blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name=_('Children'), db_index=True,
                            verbose_name=_('Parent category'))
    item_class = models.CharField(max_length=200, verbose_name=_('Item class'), null=True, blank=True)
    available_paths = models.CharField(max_length=10000, verbose_name=_('Available url paths'), editable=False,
                                       blank=True, null=True)
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))
    is_root = models.BooleanField(default=False, verbose_name=_('Root'), blank=True)
    is_unique_in_path = models.BooleanField(default=False, verbose_name=_('Unique'), blank=True)
    is_endpoint = models.BooleanField(default=False, verbose_name=_('Endpoint'), blank=True)

    objects = BaseCategoryManager()

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        abstract = True
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_url(self):
        return 'url'

    def get_url_paths(self):
        """
        Return available category paths
        :return: Dictionary
        """
        return json.loads(self.available_paths)

    def create_slug(self, instance_before):
        """
        Create and make unique slug.
        If passed instance before save(), checks if new slug (in admin edit for example) unique and make unique if not.
        :param instance_before: Category instance before save()
        """
        if not instance_before:
            self.slug = unique_slug(self.__class__, create_slug(self.title))
        else:
            if not instance_before.slug == self.slug:
                self.slug = unique_slug(self.__class__, self.slug, instance=self)

    @classmethod
    def check_root(cls, title, model, instance_before=None):
        """
        Check for root with same name not present
        :return:
        """
        if instance_before:
            find = model.objects.filter(title=title).exclude(pk=instance_before.pk).count()
        else:
            find = model.objects.filter(title=title).count()
        if find:
            raise CategoryRootCheckError(title=title)

    def check_inheritance(self):
        """
        Check for parent category is not endpoint
        :return:
        """
        if self.parent and self.parent.is_endpoint:
            raise CategoryInheritanceError(invalid_category=self.parent)

    def save(self, *args, **kwargs):
        """
        Saves instance and update tree
        :param args:
        :param kwargs:
        :return:
        """
        update_process = kwargs.pop('update_process', False)
        if not update_process:
            instance_before = self.__class__.objects.get(pk=self.pk) if self.id else None
            if not self.parent:
                self.__class__.check_root(self.title, self.__class__, instance_before=instance_before)
                self.is_root = True
            self.is_endpoint = True if self.item_class else False
            self.check_inheritance()
            if self.is_endpoint and not self.is_unique_in_path:
                self.is_unique_in_path = True
            self.create_slug(instance_before)

            super(DjcatCategory, self).save(*args, **kwargs)
            self.__class__.objects.update_tree(self, instance_before)
        else:
            super(DjcatCategory, self).save(*args, **kwargs)


class DjcatItem(models.Model, BaseDjcat):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, verbose_name='Slug', blank=True)
    active = models.BooleanField(verbose_name=_('Active'), default=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    category = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_url(self):
        return 'url'

    def create_slug(self, instance_before):
        """
        Create and make unique slug.
        If passed instance before save(), checks if new slug (in admin edit for example) unique and make unique if not.
        :param instance_before: Category instance before save()
        """
        if not instance_before:
            self.slug = unique_slug(self.__class__, create_slug(self.title))
        else:
            if not instance_before.slug == self.slug:
                self.slug = unique_slug(self.__class__, self.slug, instance=self)


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
        self.check_attr_values()

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

    def register_module(self, cls):
        """
        Populate REGISTRY with module of given class
        :param cls: Class object
        :return: name: String - module name, module: Dictionary, module data
        """
        name, verbose_name = self.get_module_name(cls)
        if self.__class__.REGISTRY.get(name):
            module = self.__class__.REGISTRY[name]
        else:
            module = {'module': cls.__module__, 'verbose_name': verbose_name, 'items': {}}
        return name, module

    def get_module_name(self, cls):
        """
        Return given class item module name (ITEM_MODULE_NAME)
        :param cls: Class object
        :return: String
        """
        try:
            m = importlib.import_module(cls.__module__)
            name = m.ITEM_MODULE_NAME
            verbose_name = getattr(m, 'ITEM_MODULE_VERBOSE_NAME', name)
        except AttributeError:
            mnames = cls.__module__.split('.')
            if len(mnames) > 1:
                root_module = importlib.import_module(mnames[0])
                try:
                    name = root_module.ITEM_MODULE_NAME
                except AttributeError:
                    raise ItemModuleNameNotDefined(cls, root_module)
                else:
                    verbose_name = getattr(root_module, 'ITEM_MODULE_VERBOSE_NAME', name)
            else:
                raise ItemModuleNameNotDefined(cls, mnames[0])

        # check duplicates
        for mname, mprops in self.__class__.REGISTRY.items():
            if not cls.__module__ == mprops['module']:
                if mname == name:
                    raise ItemModuleNameDuplicate(cls.__module__, name, mprops['module'])
                if mprops['verbose_name'] == verbose_name:
                    raise ItemModuleNameDuplicate(cls.__module__, verbose_name, mprops['module'])

        return name, verbose_name

    def get_item_class_props(self, module, cls):
        """
        Return given class properties
        :param cls: Class object
        :return: Dictionary
        """
        # check duplicates
        if self.verbose_name in [x[1]['verbose_name'] for x in module['items'].items()]:
            raise ItemNameDuplicate(self.verbose_name, module['module'])
        return {'verbose_name': self.verbose_name, 'class_name': cls.__name__, 'class': '{}.{}'.format(module['module'], cls.__name__),
                'attributes': self.get_class_attributes(cls)}

    def get_class_attributes(self, cls):
        """
        Return given class attributes
        :param cls: Class object
        :return: Dictionary
        """
        attrs = {}
        for f in cls._meta.fields:
            if getattr(f, 'DJCAT_ATTRIBUTE_NAME', None):
                attrs[f.DJCAT_ATTRIBUTE_NAME] = {'verbose_name': f.DJCAT_ATTRIBUTE_VERBOSE_NAME,
                                                 'key': f.DJCAT_ATTRIBUTE_KEY,
                                                 'class': '{}.{}'.format(f.DJCAT_ATTRIBUTE_CLASS.__module__,
                                                                         f.DJCAT_ATTRIBUTE_CLASS.__name__)}
        return attrs

    def check_attr_values(self):
        """
        Validate items attributes values
        :return:
        """
        akeys = []
        for m in self.__class__.REGISTRY.items():
            for i in m[1]['items'].items():
                for a in i[1]['attributes'].items():
                    if not a[1].get('key', None):
                        raise ItemAttributeKeyNotPresent(a[1]['class'])
                    if not a[1]['key'] in akeys:
                        akeys.append(a[1]['key'])
                    else:
                        raise ItemAttributeKeyDuplicate(a[1]['class'], a[1]['key'])
