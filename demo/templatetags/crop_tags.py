from django import template
from demo.models import *
from django.utils import translation

register = template.Library()


@register.simple_tag()
def home_url():
    # provide root url for the current language
    return '/' + translation.get_language()
