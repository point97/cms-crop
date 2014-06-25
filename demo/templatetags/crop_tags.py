from django import template
from demo.models import *
from demo.snippets import LinkBLock

register = template.Library()


# LinkBlock snippets
@register.inclusion_tag('crop/tags/link_block.html', takes_context=True)
def linkBlocks(context):
  return {
    'linkBlocks': LinkBlock.objects.all(),
    'request': context['request'],
  }