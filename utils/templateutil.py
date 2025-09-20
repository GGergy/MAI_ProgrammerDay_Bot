from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils.config import settings


env = Environment(
    loader=FileSystemLoader(settings.template_dir),
    autoescape=select_autoescape()
)


@lru_cache
def get_template(template_name):
    return env.get_template(template_name)


def render(template_name, **kwargs):
    template = get_template(template_name)
    return template.render(**kwargs)
