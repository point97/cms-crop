from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailadmin.edit_handlers import PageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey


class LinkBlock(models.Model):
  title = models.CharField(max_length=255)
  url = models.URLField(null=True, blank=True)
  text = models.CharField(max_length=255)

  panels = [
    FieldPanel('title'),
    FieldPanel('url'),
    FieldPanel('text'),
  ]

  def __unicode__(self):
    return self.title

register_snippet(LinkBlock)


class LinkBlockPlacement(models.Model):
  page = ParentalKey('demo.EnglishHomePage', related_name='linkblock_placements')
  linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')

  class Meta:
    verbose_name = "Link Block Placement"
    verbose_name_plural = "Link Block Placements"

  panels = [
    PageChooserPanel('page'),
    SnippetChooserPanel('linkBlock', LinkBlock),
  ]

  def __unicode__(self):
    return self.page.title + " -> " + self.linkBlock.text

register_snippet(LinkBlockPlacement)




