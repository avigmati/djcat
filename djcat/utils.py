import random
import string
import itertools

from unidecode import unidecode

from django.db import connection
from django.utils.text import slugify

from . import settings


def create_slug(val):
    """
    Create slug from val.
    :param val: String
    :return: String
    """
    slug = slugify(unidecode(val))
    for s in settings.DJCAT_SLUG_RESERVED:
        slug = slug.replace(s, '')
    return slug


def create_uid(model, size):
    gen_uid = lambda: ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))
    uid = gen_uid()
    while model.objects.filter(uid=uid).exists():
        uid = gen_uid()
    return uid


def split_slug_on_appendix(slug):
    if len(slug[::-1].split(settings.DJCAT_SLUG_UNIQNUMBER_DELIMITER)) > 1:
        appendix, slug = slug[::-1].split(settings.DJCAT_SLUG_UNIQNUMBER_DELIMITER)
        slug = slug[::-1]
    else:
        appendix = None
    return slug, appendix


def unique_slug(model, slug, instance=None, reserved_slugs=[]):
    """
    Return unique slug for passed django model class.
    :param model: Django model class
    :param slug: String. Slug for make unique
    :param instance: Django model instance
    :return: String
    """
    orig, apdx = split_slug_on_appendix(slug)
    for x in itertools.count(1):
        if instance:
            if not model.objects.filter(slug=slug).exclude(pk=instance.pk).exists() and slug not in reserved_slugs:
                break
        else:
            if not model.objects.filter(slug=slug).exists() and slug not in reserved_slugs:
                break
        slug = '{}{}{}'.format(orig, settings.DJCAT_SLUG_UNIQNUMBER_DELIMITER, x)
    return slug


def db_table_exists(table_name):
    """
    Check table exist
    :param table_name:
    :return:
    """
    return table_name in connection.introspection.table_names()
