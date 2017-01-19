def catalog_attribute(name=None, key=None, verbose_name=None):
    def decorate(cls):
        setattr(cls, 'DJCAT_ATTRIBUTE_CLASS', cls)
        setattr(cls, 'DJCAT_ATTRIBUTE_KEY', key)
        setattr(cls, 'DJCAT_ATTRIBUTE_NAME', name)
        setattr(cls, 'DJCAT_ATTRIBUTE_VERBOSE_NAME', verbose_name if verbose_name else name)
        return cls
    return decorate


class BaseAttribute:
    DJCAT_ATTRIBUTE_CLASS = None
    DJCAT_ATTRIBUTE_KEY = None
    DJCAT_ATTRIBUTE_NAME = None
    DJCAT_ATTRIBUTE_VERBOSE_NAME = None

    @classmethod
    def get_name(cls):
        """
        Return attribute name
        :return: String
        """
        return cls.DJCAT_ATTRIBUTE_NAME
