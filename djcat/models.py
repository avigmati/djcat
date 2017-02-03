import abc
import json

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from djcat.register import CatalogItem
from .utils import create_slug, unique_slug, create_uid
from .exceptions import *


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
    def get_url(self, *args, **kwargs):
        """Return item url"""
        return

    @abc.abstractmethod
    def create_slug(self, *args, **kwargs):
        """Create item slug"""

    def check_name(self, name):
        """
        Check name contains not allowed symbols
        :param name:
        :return:
        """
        if settings.DJCAT_ITEM_SLUG_DELIMETER in name:
            raise ItemNameNotValid(item_name=name)


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
    name = models.CharField(max_length=400, verbose_name=_('Category name'))
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
        order_insertion_by = ['name']

    class Meta:
        abstract = True
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self, *args, **kwargs):
        paths = [v for k, v in self.get_url_paths().items() if len(v)]
        shortest = min(paths, key=len)
        return '/'.join(shortest) + '/'

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
        reserved_slugs = self.get_reserved_slugs()
        if not instance_before:
            self.slug = unique_slug(self.__class__, create_slug(self.name), reserved_slugs=reserved_slugs)
        else:
            if not instance_before.slug == self.slug:
                self.slug = unique_slug(self.__class__, self.slug, instance=self)

    @classmethod
    def check_root(cls, name, model, instance_before=None):
        """
        Check for root with same name not present
        :return:
        """
        if instance_before:
            find = model.objects.filter(name=name).exclude(pk=instance_before.pk).count()
        else:
            find = model.objects.filter(name=name).count()
        if find:
            raise CategoryRootCheckError(name=name)

    def check_inheritance(self):
        """
        Check for parent category is not endpoint
        :return:
        """
        if self.parent and self.parent.is_endpoint:
            raise CategoryInheritanceError(invalid_category=self.parent)

    def get_reserved_slugs(self):
        slugs = []
        if self.item_class:
            item_class = CatalogItem.get_item_by_class(self.item_class)
            if item_class:
                for a in item_class.attrs:
                    if a.type == 'choice':
                        slugs.extend(a.choices)
        return slugs

    def save(self, *args, **kwargs):
        """
        Saves instance and update tree
        :param args:
        :param kwargs:
        :return:
        """
        update_process = kwargs.pop('update_process', False)
        if not update_process:
            self.check_name(self.name)
            instance_before = self.__class__.objects.get(pk=self.pk) if self.id else None
            if not self.parent:
                self.__class__.check_root(self.name, self.__class__, instance_before=instance_before)
                self.is_root = True
            self.is_endpoint = True if self.item_class else False
            self.check_inheritance()
            if self.is_endpoint and not self.is_unique_in_path:
                self.is_unique_in_path = True
            self.create_slug(instance_before=instance_before)

            super(DjcatCategory, self).save(*args, **kwargs)
            self.__class__.objects.update_tree(self, instance_before)
        else:
            super(DjcatCategory, self).save(*args, **kwargs)


class DjcatItem(models.Model, BaseDjcat):
    name = models.CharField(max_length=200, verbose_name=_('Item name'))
    slug = models.SlugField(max_length=200, verbose_name='Slug', blank=True)
    uid = models.CharField(max_length=200)
    active = models.BooleanField(verbose_name=_('Active'), default=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    category = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return 'url'

    def create_name(self):
        """
        Create name for item
        :return:
        """
        raise NotImplementedError('create_name() must implement in subclasses.')

    def create_uid(self, size=settings.DJCAT_ITEM_UID_LENGTH):
        """
        Return unique string
        :param size: Integer, string length
        :return: String
        """
        return create_uid(self.__class__, size)

    def get_name_for_slug(self):
        """
        Return normalized name for slug creation
        :return: String, normalized name
        """
        name = ' '.join([x for x in self.name.split(' ') if len(x)])
        self.check_name(name)
        return name

    def get_reserved_slugs(self):
        """
        Return item class attributes slugs
        :return: List, attributes slugs
        """
        slugs = []
        item_class = CatalogItem.get_item_by_class(self.__class__.__module__+'.'+self.__class__.__name__)
        for a in item_class.attrs:
            if a.type == 'choice':
                slugs.extend(a.choices)
        return slugs

    def save(self, *args, **kwargs):
        self.create_name()
        self.create_slug()
        super(DjcatItem, self).save(*args, **kwargs)

    def create_slug(self):
        """
        Create and make unique slug with uid.
        """
        if not self.id:
            self.uid = self.create_uid()
        # hehe shit happens
        self.slug = create_slug(self.get_name_for_slug()) + settings.DJCAT_ITEM_SLUG_DELIMETER + self.uid
        while self.slug in self.get_reserved_slugs():
            self.slug = create_slug(self.get_name_for_slug()) + settings.DJCAT_ITEM_SLUG_DELIMETER + self.uid



