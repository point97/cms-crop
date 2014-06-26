from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey


class LinkBlock(models.Model):
  title = models.CharField(max_length=255)
  url = models.URLField(null=True, blank=True)
  text = models.CharField(max_length=255)
  image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

  panels = [
    FieldPanel('title'),
    FieldPanel('url'),
    FieldPanel('text'),
    ImageChooserPanel('image'),
  ]

  class Meta:
    verbose_name = "Link"
    verbose_name_plural = "Links"

  def __unicode__(self):
    return self.title

register_snippet(LinkBlock)




class EnglishLinkBlockPlacement(models.Model):
  page = ParentalKey('demo.EnglishHomePage', related_name='linkblock_placements')
  linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')

  class Meta:
    verbose_name = "English Home Page link"
    verbose_name_plural = "English Home Page links"

  panels = [
    #PageChooserPanel('page', 'demo.EnglishHomePage'),
    SnippetChooserPanel('linkBlock', LinkBlock),
  ]

  def __unicode__(self):
    return self.page.title + " -> " + self.linkBlock.text

register_snippet(EnglishLinkBlockPlacement)

class SpanishLinkBlockPlacement(models.Model):
  page = ParentalKey('demo.SpanishHomePage', related_name='linkblock_placements')
  linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')

  class Meta:
    verbose_name = "Spanish Home Page link"
    verbose_name_plural = "Spanish Home Page links"

  panels = [
    PageChooserPanel('page', 'demo.SpanishHomePage'),
    SnippetChooserPanel('linkBlock', LinkBlock),
  ]

  def __unicode__(self):
    return self.page.title + " -> " + self.linkBlock.text

register_snippet(SpanishLinkBlockPlacement)

