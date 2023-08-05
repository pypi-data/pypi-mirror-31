import os
from datetime import datetime

import attr
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bottery.conf import settings


@attr.s
class Message:
    id = attr.ib()
    platform = attr.ib()
    user = attr.ib()
    chat = attr.ib()
    text = attr.ib()
    timestamp = attr.ib()
    raw = attr.ib()
    edited = attr.ib(default=False)
    _request_payload = attr.ib(default=attr.Factory(dict))
    _response_handler = attr.ib(default=None)

    @property
    def datetime(self):
        return datetime.utcfromtimestamp(self.timestamp)


@attr.s
class Response:
    source = attr.ib()
    text = attr.ib()


def render(message, template_name, context=None):
    context = context or {}
    base_dir = os.path.join(os.getcwd(), 'templates')
    paths = [base_dir]
    paths.extend(settings.TEMPLATES)

    env = Environment(
        loader=FileSystemLoader(paths),
        autoescape=select_autoescape(['html']))

    template = env.get_template(template_name)

    default_context = {
        'user': message.user,
        'platform': message.platform,
    }
    default_context.update(context)
    return template.render(**default_context)
