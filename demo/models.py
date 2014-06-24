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
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from south.signals import post_migrate

from demo.utils import export_event


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
# English Home Page
#

class EnglishHomePage(MultiLingualPage):
    body = RichTextField(blank=True)

    indexed_fields = ('body', )
    search_name = "Homepage"

    class Meta:
        verbose_name = "English Home Page"

EnglishHomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]

EnglishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#
# Spanish Home Page
#

class SpanishHomePage(MultiLingualPage):
    body = RichTextField(blank=True)

    indexed_fields = ('body', )
    search_name = u"Pagina Principal"

    class Meta:
        verbose_name = "Spanish Home Page"

SpanishHomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]

SpanishHomePage.promote_panels = [
    FieldPanel('spanish_link', classname="spanish link"),
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


# Signal handler to load demo data from fixtures after migrations have completed
@receiver(post_migrate)
def import_demo_data(sender, **kwargs):
    # post_migrate will be fired after every app is migrated; we only want to do the import
    # after demo has been migrated
    if kwargs['app'] != 'demo':
        return

    # Check that there isn't already meaningful data in the db that would be clobbered.
    # A freshly created databases should contain no images, tags or snippets
    # and just two page records: root and homepage.
    #if Image.objects.count() or Tag.objects.count() or Advert.objects.count() or Page.objects.count() > 2:
    if Image.objects.count() or Tag.objects.count() or Page.objects.count() > 2:
        return

    # furthermore, if any page has a more specific type than Page, that suggests that meaningful
    # data has been added
    for page in Page.objects.all():
        if page.specific_class != Page:
            return

    import os, shutil
    from django.conf import settings

    fixtures_dir = os.path.join(settings.PROJECT_ROOT, 'demo', 'fixtures')
    fixture_file = os.path.join(fixtures_dir, 'initial_data.json')
    image_src_dir = os.path.join(fixtures_dir, 'images')
    image_dest_dir = os.path.join(settings.MEDIA_ROOT, 'original_images')

    call_command('loaddata', fixture_file, verbosity=0)

    # if not os.path.isdir(image_dest_dir):
    #     os.makedirs(image_dest_dir)

    # for filename in os.listdir(image_src_dir):
    #     shutil.copy(os.path.join(image_src_dir, filename), image_dest_dir)
