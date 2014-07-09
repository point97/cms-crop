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



# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
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

    @property
    def explore_sections(self):
        # Get list of live SectionPages that are descendants of this page
        sections = ExploreSectionPage.objects.live().descendant_of(self)
        # Order by most recent date first
        #sections = sections.order_by('order')
        return sections

    def get_context(self, request):
        # Get sections
        sections = self.sections
        explore_sections = self.explore_sections

        # Update template context
        context = super(SectionedPage, self).get_context(request)
        context['sections'] = sections
        context['explore_sections'] = explore_sections
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
class EnglishHomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.EnglishHomePage', related_name='carousel_items')


class EnglishHomePage(SectionedPage):
    search_name = "Home"
    subpage_types = ['demo.SectionPage', 'demo.ExploreSectionPage']

    class Meta:
        verbose_name = "English Home Page"

EnglishHomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    InlinePanel(EnglishHomePage, 'linkblock_placements', label="Link blocks"),
    InlinePanel(EnglishHomePage, 'carousel_items', label="Carousel items"),

]

EnglishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Spanish Home Page
#
class SpanishHomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.SpanishHomePage', related_name='carousel_items')

class SpanishHomePage(SectionedPage):
    search_name = u"Pagina Principal"
    subpage_types = ['demo.SectionPage', 'demo.ExploreSectionPage']

    class Meta:
        verbose_name = "Spanish Home Page"

SpanishHomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    InlinePanel(SpanishHomePage, 'linkblock_placements', label="Link blocks"),
    InlinePanel(SpanishHomePage, 'carousel_items', label="Carousel items"),
]

SpanishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Section page
#

class SectionPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.SectionPage', related_name='carousel_items')

class SectionPage(MultiLingualPage):
    body = RichTextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['demo.ExploreSectionPage']
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
    ImageChooserPanel('image'),
    InlinePanel(SpanishHomePage, 'carousel_items', label="Carousel items"),
]

SectionPage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    
]


"""
Explore Pages
 - Topics
 -- DataPriorities 
 -- DataCatalogs
"""


class ExplorePageIndex(MultiLingualPage):
    """
    Acts as an index life SectionedPage for English and
    Spanish HomePage's
    """
    body = RichTextField(blank=True, null=True)
    sidebar_title = models.CharField(max_length=255, null=True, blank=True)

    @property
    def topics(self):
        # Get list of live ExploreTopic pages that are descendants of this page
        topics = ExploreTopic.objects.live().descendant_of(self)
        # Order by most recent date first
        # topics = topics.order_by('order')
        return topics

    @property
    def topic_pics(self):
        pics = []
        for topic in self.topics:
            obj = {'image':topic.image,
                   'link':"#", 
                   'caption':topic.title,

                   }
            pics.append(obj)
        return pics

    @property
    def data_catalogs(self):
        """
        Returns a list of topics (ordered according to self.topics). 
        Each item contains a dict with the kollowing keywords
        - topic
        - catalogs
        """
        out = [ {"topic": topic, "catalogs": topic.catalogs} for topic in self.topics]
        return out

    @property
    def data_priorities(self):
        """
        Returns a list of priorities (ordered according to self.topics). 
        Each item contains a dict with the kollowing keywords
        - topic
        - priorities
        """
        out = [ {"topic": topic, "priorities": topic.priorities} for topic in self.topics]
        return out

    def get_context(self, request):
        # Update template context
        context = super(ExplorePageIndex, self).get_context(request)
        context.update({
            'topics': self.topics,
            'data_catalogs': self.data_catalogs,
            'data_priorities': self.data_priorities,
            'pics': self.pics,

        })
        return context

    class Meta:
        verbose_name = "Explore Page Indexes - DO NOT USE"


class ExploreCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.ExploreSectionPage', related_name='carousel_items')


class ExploreSectionPage(ExplorePageIndex):
    subpage_types = ['demo.ExploreTopic']
    class Meta:
        verbose_name = "Explore Section Page"

ExploreSectionPage.content_panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('sidebar_title'),
    ]


class ExploreTopic(MultiLingualPage):
    short_description = models.CharField(max_length=255, null=True, blank=True)
    long_description = RichTextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subpage_types = ['demo.DataCatalogPage', 'demo.DataPriorityPage']

    @property
    def topic_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(ExploreSectionPage).last()

    @property
    def catalogs(self):
        out = DataCatalogPage.objects.live().descendant_of(self)
        return out

    @property
    def priorities(self):
        out = DataPriorityPage.objects.live().descendant_of(self)
        return out

    def get_context(self, request):
        context = super(ExplorePageIndex, self).get_context(request)
        context.update({
            'catalogs': self.catalogs,
            'priorities': self.priorities
        })
        return context


    class Meta:
        verbose_name = "Explore Topic"


ExploreTopic.content_panels = [
    FieldPanel('title'),
    FieldPanel('short_description'),
    FieldPanel('long_description'),
    ImageChooserPanel('image'),

]


class DataCatalogIndex(MultiLingualPage):
    """
    Acts as an index for the DataCatelogs which are subpages of ExploreTopics

    """
    def get_context(self, request):
        # Update template context
        context = super(DataCatalogIndex, self).get_context(request)
        context.update({})
        return context

    class Meta:
        verbose_name = "Data Catalog Indexes - DO NOT USE"


class DataCatalogPage(DataCatalogIndex):
    body = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = "Data Catalog Page"

DataCatalogPage.content_panels = [
    FieldPanel('title'),
    FieldPanel('body')

]

class DataPriorityIndex(MultiLingualPage):
    """
    Acts as an index for the DataCatelogs which are subpages of ExploreTopics

    """
    def get_context(self, request):
        # Update template context
        context = super(DataPriorityIndex, self).get_context(request)
        
        context.update({})
        return context

    class Meta:
        verbose_name = "Data Priority Indexes - DO NOT USE"


class DataPriorityPage(DataPriorityIndex):
    body = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = "Data Priority"
        verbose_name_plural = "Data Priorities"

DataPriorityPage.content_panels = [
    FieldPanel('title'),
    FieldPanel('body'),
    FieldPanel('spanish_link', classname="spanish link")
]


###############################
# Events Pages Stuff
###############################
# Event index page

class EventIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.EventIndexPage', related_name='related_links')


class EventIndexPage(MultiLingualPage):
    intro = RichTextField(blank=True)

    indexed_fields = ('intro', )

    subpage_types = ['demo.EventPage']

    @property
    def events(self):
        # Get list of live event pages that are descendants of this page
        events = EventPage.objects.live().descendant_of(self)

        # Filter events list to get ones that are either
        # running now or start in the future
        events = events.filter(date_from__gte=date.today())

        # Order by date
        events = events.order_by('date_from')

        return events

EventIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(EventIndexPage, 'related_links', label="Related links"),
]

EventIndexPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
]


# Event page

class EventPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.EventPage', related_name='carousel_items')


class EventPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.EventPage', related_name='related_links')


class EventPageSpeaker(Orderable, LinkFields):
    page = ParentalKey('demo.EventPage', related_name='speakers')
    first_name = models.CharField("Name", max_length=255, blank=True)
    last_name = models.CharField("Surname", max_length=255, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def name_display(self):
        return self.first_name + " " + self.last_name

    panels = [
        FieldPanel('first_name'),
        FieldPanel('last_name'),
        ImageChooserPanel('image'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]


class EventPage(MultiLingualPage):
    date_from = models.DateField("Start date")
    date_to = models.DateField(
        "End date",
        null=True,
        blank=True,
        help_text="Not required if event is on a single day"
    )
    time_from = models.TimeField("Start time", null=True, blank=True)
    time_to = models.TimeField("End time", null=True, blank=True)
    audience = models.CharField(max_length=255, choices=EVENT_AUDIENCE_CHOICES, default="public")
    location = models.CharField(max_length=255, blank=True, help_text="help me")
    body = RichTextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True, help_text="")
    cost = models.CharField(max_length=255, blank=True)
    signup_link = models.URLField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('get_audience_display', 'location', 'body')

    @property
    def event_index(self):
        # Find closest ancestor which is an event index
        return self.get_ancestors().type(EventIndexPage).last()

    def serve(self, request):
        if "format" in request.GET:
            if request.GET['format'] == 'ical':
                # Export to ical format
                response = HttpResponse(
                    export_event(self, 'ical'),
                    content_type='text/calendar',
                )
                response['Content-Disposition'] = 'attachment; filename=' + self.slug + '.ics'
                return response
            else:
                # Unrecognised format error
                message = 'Could not export event\n\nUnrecognised format: ' + request.GET['format']
                return HttpResponse(message, content_type='text/plain')
        else:
            # Display event page as usual
            return super(EventPage, self).serve(request)

EventPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('short_description'),
    FieldPanel('date_from'),
    FieldPanel('date_to'),
    FieldPanel('time_from'),
    FieldPanel('time_to'),
    FieldPanel('location'),
    #FieldPanel('audience'),
    FieldPanel('cost'),
    FieldPanel('signup_link'),
    InlinePanel(EventPage, 'carousel_items', label="Carousel items"),
    FieldPanel('body', classname="full"),
    InlinePanel(EventPage, 'speakers', label="Speakers"),
    InlinePanel(EventPage, 'related_links', label="Related links"),
]

EventPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ImageChooserPanel('feed_image'),
]




