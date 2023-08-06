from collections import OrderedDict

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse

from markupsafe import escape

from prometheus.apps.general.db_config import db_vars


def get_admin_emails(force_system=False, language=settings.DEFAULT_LANGUAGE):
    if force_system:
        return [x[1] for x in settings.ADMINS]

    admins = db_vars.get('ADMINS', language, '')
    return admins.split(',') if admins else [x[1] for x in settings.ADMINS]


def get_default_from_email(force_system=False):
    if force_system:
        return settings.DEFAULT_FROM_EMAIL

    email = db_vars.get('DEFAULT_FROM_EMAIL', None)
    return email if email else settings.DEFAULT_FROM_EMAIL


def send_email(template, emails, subject, params=None, extra_headers=None, from_email=None):
    if from_email is None:
        from_email = get_default_from_email()

    message_html = render_to_string(
        'emails/%s/%s.html' % (template, template), params, using='jinja2'
    )
    message_txt = render_to_string(
        'emails/%s/%s.txt' % (template, template), params, using='jinja2'
    )

    msg = EmailMultiAlternatives(subject, message_txt, from_email, emails, headers=extra_headers)
    msg.attach_alternative(message_html, 'text/html')

    msg.send()


def send_trigger_email(event, obj=None, fields=None, emails=None, from_email=None,
                       extra_data=None, extra_headers=None, language=settings.DEFAULT_LANGUAGE):
    if emails is None:
        emails = get_admin_emails(language=language)

    if from_email is None:
        from_email = get_default_from_email()

    if event is None:
        if obj:
            event = 'новый объект %s' % obj._meta.verbose_name
        else:
            event = 'новое событие'

    if extra_data is not None:
        assert isinstance(extra_data, dict)

    subject = 'На сайте %s %s' % (settings.SITE_NAME, event)

    admin_url = None
    if obj:
        meta = obj._meta
        model = meta.model
        app = model.__module__.split('.')[0]
        model_name = meta.object_name.lower()

        if fields is None:
            fields = {'ID': obj.pk}
        else:
            field_names = fields[:]
            fields = OrderedDict()
            for field in field_names:
                for f in meta.fields:
                    value = getattr(obj, field)
                    if f.name == field:
                        if isinstance(f, models.ForeignKey):
                            if value:
                                orig_value = value
                                value = 'ID=%s: %s' % (value.id, escape(str(value)))

                                if hasattr(orig_value, 'get_absolute_url'):
                                    value = '<a href="%s%s">%s</a>' % (
                                        settings.SITE_URL,
                                        orig_value.get_absolute_url(),
                                        value
                                    )
                            else:
                                value = '-'
                        else:
                            value = escape(value)
                        fields[f.verbose_name] = value
                        break

        admin_url = reverse('admin:%s_%s_change', (app, model_name), args=(obj.pk,))

    params = {
        'admin_url': admin_url,
        'extra_data': extra_data,
        'fields': fields,
        'site_url': settings.SITE_URL,
        'subject': subject
    }

    message_txt = render_to_string(
        'emails/admin/new_object_trigger.html',
        params,
        using='jinja2'
    )

    msg = EmailMessage(subject, message_txt, from_email, emails, headers=extra_headers)
    return msg.send()
