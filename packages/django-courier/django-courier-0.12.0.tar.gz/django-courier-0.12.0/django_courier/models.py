import collections
from typing import Any, List, Mapping, TypeVar, cast

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from . import templates
from .backends import get_backends, get_backends_from_settings
from .base import AbstractContactable, Contact

_COURIER_CONTENTTYPE_IDS = None


def get_model_variables(label, value, cls, ancestors=set()):
    if cls is None:
        return {'label': label, 'value': value}
    assert issubclass(cls, models.Model)
    sub_ancestors = ancestors.copy()
    sub_ancestors.add(cls)
    attrs = []
    skip_relations = len(ancestors) > 2
    children = []
    for field in cls._meta.fields:
        sub_label = field.verbose_name.title(),
        sub_value = '{}.{}'.format(value, field.name)
        if field.is_relation:
            if skip_relations or field.related_model in ancestors:
                continue
            children.append(get_model_variables(
                sub_label, sub_value, field.related_model,
                ancestors=sub_ancestors))
        else:
            attrs.append({'label': sub_label, 'value': sub_value})
    return {'label': label, 'value': value, 'attrs': attrs,
            'rels': children}


def _courier_contenttype_ids():
    for all_models in apps.all_models.values():
        for model in all_models.values():
            if issubclass(model, CourierModel):
                if model._courier_meta.has_channels():
                    ct = ContentType.objects.get_for_model(model)
                    yield ct.id


def content_type_limit():
    global _COURIER_CONTENTTYPE_IDS
    if _COURIER_CONTENTTYPE_IDS is None:
        _COURIER_CONTENTTYPE_IDS = tuple(_courier_contenttype_ids())
    return {'id__in': _COURIER_CONTENTTYPE_IDS}


class Channel(collections.namedtuple('ChannelBase',
                                     ('name', 'cls', 'func', 'obj'))):
    def contactables(self):
        return (self.obj,) if self.func is None else self.func(self.obj)


class CourierOptions(object):
    """
    Options for Courier extensions
    """

    PREFIX_NAMES = {
        'si': _('Site Contacts'),
        'c': 'Content',
        'se': _('Source'),
        're': _('Target'),
    }
    PREFIX_FORMATS = {
        'c': '{}',
        'se': _('Source\'s {}'),
        're': _('Target\'s {}'),
    }
    ALL_OPTIONS = ('notifications', 'channels')
    # list of notification code names
    notifications = []

    def __init__(self, meta):
        """
        Set any options provided, replacing the default values
        """
        self.__channel_items = None
        self._channels = {}
        self.notifications = []
        if meta is not None:
            for key, value in meta.__dict__.items():
                if key in self.ALL_OPTIONS:
                    setattr(self, key, value)
                elif not key.startswith('_'):  # ignore private parts
                    raise ValueError(
                        'CourierMeta has invalid attribute: {}'.format(key))

    def get_channels(self, prefix: str, obj) -> dict:
        if self.__channel_items is None:
            self.__channel_items = {}
            for key, (name, cls, func) in self._channels.items():
                channel_key = prefix if key == '' else prefix + ':' + key
                if name == '':
                    name = self.PREFIX_NAMES[prefix]
                    if name == 'Content':
                        name = cls._meta.verbose_name.title()
                else:
                    name = self.PREFIX_FORMATS[prefix].format(name)
                self.__channel_items[channel_key] = (name, cls, func)
        return dict((key, Channel(name, cls, func, obj))
                    for key, (name, cls, func) in self.__channel_items.items())

    def add_channel(self, key, name, target_type, func=None):
        self.__channel_items = None
        self._channels[key] = name, target_type, func

    def has_channels(self):
        return bool(self._channels)


class CourierModelBase(models.base.ModelBase):
    """
    Metaclass for Courier extensions.

    Deals with notifications on CourierOptions
    """
    def __new__(mcs, name, bases, attributes):
        new = super(CourierModelBase, mcs).__new__(
            mcs, name, bases, attributes)
        meta = attributes.pop('CourierMeta', None)
        setattr(new, '_courier_meta', CourierOptions(meta))
        return new


CourierModelN = TypeVar('CourierModelN', 'CourierModel', None)


class CourierModel(models.Model, metaclass=CourierModelBase):
    """
    Base class for models that implement notifications
    """

    class Meta:
        abstract = True

    def issue_notification(self, codename: str,
                           target: CourierModelN = None,
                           source: CourierModelN = None):
        ct = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(
            codename=codename, content_type=ct)
        notification.issue(self, target, source)

    @classmethod
    def add_channel(cls, key, verbose_name='', target_type=None, func=None):
        if target_type is None:
            target_type = cls
        elif func is None and target_type != cls:
            raise ValueError('Must specify function when using '
                             'different models')
        cls._courier_meta.add_channel(key, verbose_name, target_type, func)

    def get_channels(self, prefix: str):
        return self.__class__._courier_meta.get_channels(prefix, self)


class NotificationManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, app_label, model, codename):
        return self.get(
            codename=codename,
            content_type=ContentType.objects.db_manager(
                self.db).get_by_natural_key(app_label, model),
        )


class CourierParam:
    REQUIRED_PARAMS = {'codename', 'description'}
    OPTIONAL_PARAMS = {'source_model': '', 'target_model': '',
                       'required': False}

    def __init__(self, codename, description, **kwargs):
        self.params = {
            'codename': codename,
            'description': description,
            'from_code': True,
        }
        for key, default in self.OPTIONAL_PARAMS.items():
            if key in kwargs:
                self.params[key] = kwargs.pop(key)
            else:
                self.params[key] = default
        if kwargs:
            raise ValueError('Unrecognized parameters {}'.format(
                ', '.join(kwargs.keys())))

    def params_equal(self, notification):
        for key in self.params:
            if getattr(notification, key) != self.params[key]:
                return False
        return True

    def param_value(self, key):
        value = self.params[key]
        if key in ('source_model', 'target_model'):
            if value == '':
                return None
            model = apps.get_model(value)
            return ContentType.objects.get_for_model(model)
        return value

    def set_params(self, notification):
        for key in self.params:
            setattr(notification, key, self.param_value(key))

    def create(self, content_type):
        new = Notification(content_type=content_type)
        self.set_params(new)
        return new

    @property
    def codename(self):
        return self.params['codename']


class Notification(models.Model):
    """
    Base class for all notifications
    """

    codename = models.CharField(_('codename'), max_length=100)
    content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE,
        limit_choices_to=content_type_limit,
        verbose_name=_('content type'))
    description = models.TextField(_('description'))
    source_model = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE, related_name='+',
        limit_choices_to=content_type_limit,
        verbose_name=_('source model'), null=True, blank=True)
    target_model = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE, related_name='+',
        limit_choices_to=content_type_limit,
        verbose_name=_('target model'), null=True, blank=True)
    required = models.BooleanField(
        _('required'), default=False,
        help_text=_('If true, triggering the notification will throw an '
                    'error if there is no available template/contact'))
    from_code = models.BooleanField(
        _('from code'), default=False,
        help_text=_('True if the notification is defined in the code and '
                    'automatically managed'))

    objects = NotificationManager()

    def __str__(self):
        return "{} | {} | {}".format(
            self.content_type.app_label, self.content_type, self.codename)

    def natural_key(self):
        return self.content_type.natural_key() + (self.codename,)

    natural_key.dependencies = ['contenttypes.contenttype']

    def get_recipient_models(self):
        source_model = self.get_source_model()
        target_model = self.get_target_model()
        content_model = (None if self.content_type_id is None
                         else self.content_type.model_class())
        recipient_spec = {
            'si': SiteContact,
            're': target_model,
            'se': source_model,
            'c': content_model,
        }
        return dict((key, value) for (key, value)
                    in recipient_spec.items() if value is not None)

    def get_recipient_instances(self, content, target, source):
        choices = {
            'si': SiteContact(),
            'c': content,
        }
        if self.target_model and (target is not None):
            choices['re'] = target
        elif self.target_model:
            raise RuntimeError(
                'Model specified "target_model" for notification but '
                'target missing on issue_notification ')
        elif target is not None:
            raise RuntimeError('Recipient added to issue_notification, '
                               'but is not specified in CourierMeta')
        if self.source_model and (source is not None):
            choices['se'] + source
        elif self.source_model:
            raise RuntimeError(
                'Model specified "source_model" for notification but source '
                'missing on issue_notification ')
        elif source is not None:
            raise RuntimeError('Sender added to issue_notification, but is '
                               'not specified in CourierMeta')

        return dict((key, model) for (key, model)
                    in choices.items() if model is not None)

    def get_recipient_channels(self, content, target, source):
        instances = self.get_recipient_instances(content, target, source)
        return dict((key, channel)
                    for recip_key, model in instances.items()
                    for key, channel in model.get_channels(recip_key).items())

    def issue(self, content,
              target: CourierModelN=None,
              source: CourierModelN=None):
        """
        To send a notification to a user, get all the user's active methods.
        Then get the backend for each method and find the relevant template
        to send (and has the said notification). Send that template with
        the parameters with the backend.

        :param content: model object that the notification is about
        :param target: either a user, or None if no logical target
        :param source: user who initiated the notification
        :return: None
        """
        # check
        parameters = {'content': content}
        if target is not None:
            parameters['target'] = target
        if source is not None:
            parameters['source'] = source

        channels = self.get_recipient_channels(content, target, source)
        contactable_list = dict((key, channel.contactables())
                                for (key, channel) in channels.items())

        contact_set = collections.defaultdict(dict)
        for key, contactables in contactable_list.items():
            for c_able in contactables:
                for contact in c_able.get_contacts_for_notification(self):
                    contact_set[key][contact] = c_able

        sent = False
        for key, contact_dict in contact_set.items():
            if self.send_messages(contact_dict, parameters,
                                  Template.objects.filter(recipient=key)):
                sent = True
        if not sent and self.required:
            raise RuntimeError('Notification required, but no message sent')

    def send_messages(
            self, contacts: Mapping[Contact, AbstractContactable],
            generic_params: Mapping[str, Any], template_queryset):

        def _get_backend_message(protocol):
            backends = get_backends_from_settings(protocol)
            # now get all the templates for these backends
            for be in backends:
                tpl = template_queryset.filter(
                    backend=be.ID, notification=self, is_active=True).first()
                if tpl is not None:
                    return be, tpl
            return None

        # per-protocol message cache
        cache = {}
        sent = False
        for contact, contactable in contacts.items():
            params = generic_params.copy()
            params['contact'] = contact
            params['recipient'] = contactable
            proto = contact.protocol
            if proto not in cache:
                cache[proto] = _get_backend_message(proto)
            if cache[proto] is not None:
                backend, template = cache[proto]
                message = backend.build_message(
                    template.subject, template.content, params)
                # We're catching all exceptions here because some people
                # are bad people and can't subclass properly
                try:
                    backend.send_message(contact, message)
                    sent = True
                except Exception as e:
                    FailedMessage.objects.create(
                        backend=backend.ID,
                        name=contact.name,
                        address=contact.address,
                        message=str(message),
                        error=str(e),
                    )
        return sent

    def can_issue_custom(self):
        return not (self.source_model or self.target_model)

    def preview(self, backend_id, message):
        backend = [b for b in get_backends() if b.ID == backend_id][0]
        content_model = self.content_type.model_class()
        params = templates.PreviewParameters(
            content_model, self.get_source_model(), self.get_target_model())
        return backend.preview_message('', message, params)

    def get_source_model(self):
        if self.source_model:
            return self.source_model.model_class()
        return None

    def get_target_model(self):
        if self.target_model:
            return apps.get_model(self.target_model)
        return None

    def get_recipient_variables(self):
        recipient_spec = self.get_recipient_models()
        source_model = self.get_source_model()
        target_model = self.get_target_model()
        content_model = self.content_type.model_class()
        mapping = {}
        for target_key, model in recipient_spec.items():
            if model is not None:
                channel_items = model._courier_meta.get_channels(
                    target_key, None).items()
                for key, (name, cls, _func, _obj) in channel_items:
                    mapping[key] = get_model_variables(
                        'Recipient', 'recipient', cls)
        content_name = content_model._meta.verbose_name.title()
        mapping['_static'] = [
            get_model_variables(content_name, 'content', content_model),
        ]
        if source_model:
            mapping['_static'].append(
                get_model_variables('Source', 'source', source_model))
        if target_model:
            mapping['_static'].append(
                get_model_variables('Target', 'target', target_model))
        return mapping


class Template(models.Model):

    class Meta:
        verbose_name = _('template')

    notification = models.ForeignKey(
        to=Notification, on_delete=models.PROTECT,
        verbose_name=_('notification'))
    backend = models.CharField(_('backend'), max_length=100)
    subject = models.CharField(_('subject'), max_length=500, blank=True)
    content = models.TextField(_('content'))
    recipient = models.CharField(
        verbose_name=_('recipient'), max_length=103, default='re',
        help_text=_('Who this message actually gets sent to.'))
    is_active = models.BooleanField(
        _('is active'), default=True,
        help_text=_('When not active, the template will be ignored'))

    objects = models.Manager()

    def render(self, parameters: dict, autoescape=True):
        content = cast(str, self.content)
        template = templates.from_string(content)
        context = Context(parameters, autoescape=autoescape)
        return template.render(context)


class SiteContactManager(models.Manager, AbstractContactable):
    use_in_migrations = True

    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[Contact]:
        wlq = Q(enable_filter='whitelist',
                sitecontactpreference__notification=notification,
                sitecontactpreference__is_active=False)
        blq = Q(enable_filter='blacklist') & ~Q(
                sitecontactpreference__notification=notification,
                sitecontactpreference__is_active=False)
        for sc in SiteContact.objects.filter(blq | wlq):
            yield Contact(sc.name, sc.protocol, sc.address)


# can't make this subclass AbstractContact or fields become unset-able
class SiteContact(CourierModel):

    ENABLE_CHOICES = (
        ('blacklist', _('Blacklist')),
        ('whitelist', _('Whitelist')),
    )

    class Meta:
        verbose_name = _('site contact')
        unique_together = (('address', 'protocol'),)

    name = models.CharField(_('name'), blank=True, max_length=500)
    protocol = models.CharField(_('protocol'), max_length=100)
    address = models.CharField(_('address'), max_length=500)
    enable_filter = models.CharField(choices=ENABLE_CHOICES, max_length=10,
                                     default='blacklist')

    objects = SiteContactManager()

    def __str__(self):
        return self.name

    @staticmethod
    def all_contacts(_obj):
        yield SiteContact.objects


SiteContact.add_channel('', func=SiteContact.all_contacts)


class SiteContactPreference(models.Model):

    site_contact = models.ForeignKey(SiteContact, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('is active'))

    objects = models.Manager()


class FailedMessage(models.Model):

    class Meta:
        verbose_name = _('failed message')

    backend = models.CharField(_('backend'), max_length=100)
    contact_name = models.CharField(_('contact name'), max_length=500)
    address = models.CharField(_('address'), max_length=500)
    message = models.TextField(_('message'))
    error = models.TextField(_('error'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return '{}:{} @ {}'.format(self.backend.PROTOCOL,
                                   self.address, self.created_at)


def get_recipient_choices(notification):
    for recipient_key, model in notification.get_recipient_models().items():
        channel_data = model._courier_meta.get_channels(recipient_key, None)
        for key, (name, _cls, _func, _obj) in channel_data.items():
            yield key, name
