import requests
import pkg_resources
from django.conf import settings

distribution = pkg_resources.get_distribution('warapidpro')


def session_for_warapidpro():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'warapidpro/%s (%s, %s)' % (
            distribution.version, "[Auth Setup]", settings.HOSTNAME)
    })
    return session


def session_for_channel(channel):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'warapidpro/%s (%s, %s, %s)' % (
            distribution.version,
            (channel.org.name
             if channel.org
             else 'Unknown Org'),
            '%s/%s' % (channel.channel_type, channel.pk),
            settings.HOSTNAME)
    })
    return session
