from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.management import call_command
from django.dispatch import receiver
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from django.template.response import TemplateResponse
from django.conf import settings
from django.http import HttpResponseRedirect

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from south.signals import post_migrate

from demo.utils import export_event
from demo.snippets import LinkBlock


EVENT_AUDIENCE_CHOICES = (
    ('public', "Public"),
    ('private', "Private"),
)


COMMON_PANELS = (
    FieldPanel('slug'),
    FieldPanel('seo_title'),
    FieldPanel('show_in_menus'),
    FieldPanel('search_description'),
)





class LinkFields(models.Model):
    """
    A link field that acts as a base class to the Carousel Item.
    This is not related to the link blocks.
    """
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True




# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True



# Multilingual Page

class MultiLingualPage(Page):
    """
    Common implementation for common page fields such as the translation links.
    """
    spanish_link = models.ForeignKey(Page, null=True, blank=True, related_name='+')

    # is_abstract = True

    def serve(self, request):
        # Overriden to activate the current session with the proper language.
        user_language = 'en'
        if self.is_spanish():
            user_language = 'es'
        translation.activate(user_language)
        #request.session[translation.LANGUAGE_SESSION_KEY] = user_language

        return TemplateResponse(
            request, 
            self.get_template(request), 
            self.get_context(request)
        )

    def is_english(self):
        # TODO: base this on the type of home page this page sits under (EngishHome)
        return self.url.find('/en/') != -1

    def is_spanish(self):
        # TODO: base this on the type of home page this page sits under (SpanishHome)
        return self.url.find('/es/') != -1

    def english_page(self):
        if self.is_english():
            return self
        elif self.is_spanish():
            return self.__class__.objects.filter(spanish_link=self).first()

    def spanish_page(self):
        english_page = self.english_page()

        if english_page and english_page.spanish_link_id:
            return self.__class__.objects.get(id=english_page.spanish_link_id)

    def english_url(self):
        page = self.english_page()
        if page:
            return self.url
        elif self.is_spanish():
            return self.__class__.objects.filter(spanish_link=self).first()

    def spanish_url(self):
        english_page = self.english_page()

        if english_page and english_page.spanish_link_id:
            return self.__class__.objects.get(id=english_page.spanish_link_id)

    @property
    def search_url(self):
        return self.url + 'search/'

    search_template = 'demo/search_results.html'
    def search_view(self, request):
        # Search
        query_string = request.GET.get('q', None)
        if query_string is not None:
            # Get list of live subpages of the homepage
            # for current language.
            pages = Page.objects.descendant_of(self).live()

            # TODO: Remove pages from PageQuerySet that don't stem
            # from current language's home page.

            # Search them

            # Waiting on wagtail to push PageQuerySet.search() to
            # the public repo.
            pages = pages.search(query_string)
        else:
            pages = Page.objects.none()

        # Pagination
        # TODO

        # Update context
        context = Page.get_context(self, request)
        context['query_string'] = query_string
        context['pages'] = pages
        return TemplateResponse(request, self.search_template, context)

    def route(self, request, path_components):
        if self.live and len(path_components) > 0 and path_components[0] == 'search':
            return self.search_view(request)
        return super(MultiLingualPage, self).route(request, path_components)

    # class Meta:
    #     abstract = True


#
# Lang Root Page
#
class LangRootPage(Page):

    def serve(self, request):
        '''
        Overriden to redirect based language settings. If browser/session/cookie
        language setting is supported by this site, go to the home page for that
        language. Otherwise, go to the home page for this site's default 
        language (the first language listed in the LANGUAGES setting.
        '''
        supported_langs = settings.LANGUAGES
        default_lang = supported_langs[0][0]
        cur_lang = translation.get_language()
        cur_lang_supported = False
        for lang in supported_langs:
            if lang[0] == cur_lang:
                cur_lang_supported = True
                break

        if not cur_lang_supported:
            cur_lang = default_lang

        return HttpResponseRedirect(self.url + cur_lang)

    class Meta:
        verbose_name = "Multi-lingual Root"

LangRootPage.content_panels = [
    FieldPanel('title', classname="full title"),
]

LangRootPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Sectioned Page - acts as an index for any SectionPage that
# is a direct child.
#
class SectionedPage(MultiLingualPage):

    @property
    def sections(self):
        # Get list of live SectionPages that are descendants of this page
        sections = SectionPage.objects.live().descendant_of(self)
        # Order by most recent date first
        #sections = sections.order_by('order')
        return sections

    def get_context(self, request):
        # Get sections
        sections = self.sections
        # Update template context
        context = super(SectionedPage, self).get_context(request)
        context['sections'] = sections
        return context

    class Meta:
        verbose_name = "Sectioned Page"

SectionedPage.content_panels = [
    FieldPanel('title', classname="full title"),
]

SectionedPage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]



#
# English Home Page - acts as an index for any SectionPage that
# is a direct child.
#
class EnglishHomePage(SectionedPage):
    search_name = "Home"

    class Meta:
        verbose_name = "English Home Page"

EnglishHomePage.content_panels = [
    SnippetChooserPanel('linkBlock', LinkBlock),
    FieldPanel('title', classname="full title"),
]

EnglishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Spanish Home Page
#

class SpanishHomePage(SectionedPage):
    search_name = u"Pagina Principal"

    class Meta:
        verbose_name = "Spanish Home Page"

SpanishHomePage.content_panels = [
    FieldPanel('title', classname="full title"),
]

SpanishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Section page
#

class SectionPage(MultiLingualPage):
    body = RichTextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('body', )

    @property
    def section_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(SectionedPage).last()

    class Meta:
        verbose_name = "Page Section"

SectionPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]

SectionPage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ImageChooserPanel('image'),
]
