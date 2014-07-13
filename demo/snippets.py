from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey

POSITION_CHOICES = (
    ('content-bottom', 'Below main content'),
    ('carousel-bottom', 'Below carousel'),
    ('sidebar-bottom', 'Bottom of sidebar')
)


class LinkBlock(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255, blank=True)
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
        verbose_name = "LINK BLOCK- A link with an image."
        verbose_name_plural = "LINK BLOCKS - put your links here first. Then you can add them to pages or sections."

    def __unicode__(self):
        return self.title

register_snippet(LinkBlock)



class EnglishLinkBlockPlacement(models.Model):
    page = ParentalKey('demo.EnglishHomePage', related_name='linkblock_placements')
    linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')
    position = models.CharField(max_length=45, default="content-bottom", 
        choices=POSITION_CHOICES, help_text="""Determines the postion of the link on the page or section.""")


    class Meta:
        verbose_name = "English Home Page link"
        verbose_name_plural = "English Home Page links"
    panels = [
        PageChooserPanel('page', 'demo.EnglishHomePage'),
        #InlinePanel(self, 'page', label="Page"),
        SnippetChooserPanel('linkBlock', LinkBlock),
        FieldPanel('position'),
    ]

    def __unicode__(self):
        return ("%s - %s -> %s") %(self.page.title, self.get_position_display(), self.linkBlock.text)

register_snippet(EnglishLinkBlockPlacement)




class SpanishLinkBlockPlacement(models.Model):
    page = ParentalKey('demo.SpanishHomePage', related_name='linkblock_placements')
    linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')
    position = models.CharField(max_length=45, default="content-bottom", 
        choices=POSITION_CHOICES, help_text="""Determines the postion of the link on the page or section.""")


    class Meta:
        verbose_name = "Spanish Home Page link"
        verbose_name_plural = "Spanish Home Page links"

    panels = [
        PageChooserPanel('page', 'demo.SpanishHomePage'),
        SnippetChooserPanel('linkBlock', LinkBlock),
        FieldPanel('position'),
    ]

    def __unicode__(self):
        return ("%s - %s -> %s") %(self.page.title, self.get_position_display(), self.linkBlock.text)

register_snippet(SpanishLinkBlockPlacement)



class SectionPageLinkBlockPlacement(models.Model):
    page = ParentalKey('demo.SectionPage', related_name='linkblock_placements')
    linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')
    position = models.CharField(max_length=45, default="content-bottom", 
        choices=POSITION_CHOICES, help_text="""Determines the postion of the link on the page or section.""")

    class Meta:
        verbose_name = "Section Page link placement"
        verbose_name_plural = "Section Page link placements"

    panels = [
        PageChooserPanel('page', 'demo.SectionPage'),
        SnippetChooserPanel('linkBlock', LinkBlock),
        FieldPanel('position'),
    ]

    def __unicode__(self):
        return ("%s - %s -> %s") %(self.page.title, self.get_position_display(), self.linkBlock.text)

register_snippet(SectionPageLinkBlockPlacement)


class ExplorePageLinkBlockPlacement(models.Model):
    page = ParentalKey('demo.ExploreSectionPage', related_name='linkblock_placements')
    linkBlock = models.ForeignKey('demo.LinkBlock', related_name='+')
    position = models.CharField(max_length=45, default="content-bottom", 
        choices=POSITION_CHOICES, help_text="""Determines the position of the link on the page or section.""")

    class Meta:
        verbose_name = "Explore section link placement"
        verbose_name_plural = "Explore section link placements"

    panels = [
        PageChooserPanel('page', 'demo.ExploreSectionPage'),
        SnippetChooserPanel('linkBlock', LinkBlock),
        FieldPanel('position'),
    ]

    def __unicode__(self):
        return ("%s - %s -> %s") %(self.page.title, self.get_position_display(), self.linkBlock.text)

register_snippet(ExplorePageLinkBlockPlacement)


