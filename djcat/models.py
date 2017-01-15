import abc
import json

from django.db import models
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel, TreeForeignKey

from .utils import create_slug, unique_slug


class BaseCatalogItem:
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


class BaseCategory(MPTTModel, BaseCatalogItem):
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
            self.is_root = self.is_root_node()
            self.is_endpoint = True if self.item_class else False
            if self.is_endpoint and not self.is_unique_in_path:
                self.is_unique_in_path = True
            self.create_slug(instance_before)
            super(BaseCategory, self).save(*args, **kwargs)
            self.__class__.objects.update_tree(self, instance_before)
        else:
            super(BaseCategory, self).save(*args, **kwargs)


