from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

import six


class BaseEnumerate(object):
    """
    Abstract class for enumerates
    """
    values = {}

    @classmethod
    def get_choices(cls):
        """
        mostly for applying in orm.field.choices
        """
        return cls.values.items()

    get_items = get_choices

    @classmethod
    def get_keys(cls):
        return cls.values.keys()

    @classmethod
    def get_constant_value_by_name(cls, name):
        if not isinstance(name, six.string_types):
            raise TypeError(_('Field "name" must be string'))

        if not name:
            raise ValueError(_('Field "name" must not be empty'))

        return cls.__dict__[name]


class StatusEnum(BaseEnumerate):
    """
    Object publicity status enumerate
    """
    DRAFT = 0
    PUBLIC = 1
    HIDDEN = 2

    values = OrderedDict((
        (DRAFT, _('Draft')),
        (PUBLIC, _('Public')),
        (HIDDEN, _('Hidden')),
    ))
