from django import template
from django.conf import settings
from django.utils import translation

from demo.models import *

register = template.Library()



@register.inclusion_tag('demo/tags/link_blocks.html', takes_context=True)
def link_blocks(context, page, position):
    """
    LinkBlock snippets

    Usage:

    {% linkblock_placements 'content-bottom' %}

    linkblock_placements is a list, each member contains a linkBlock object

    """

    try:
        linkblock_placements = page.linkblock_placements.filter(position=position)
    except AttributeError:
        linkblock_placements = []
    return {
        'linkblock_placements': linkblock_placements,
        'request': context['request'],
        'position': position
    }


# settings value
@register.assignment_tag
def get_googe_maps_key():
    return getattr(settings, 'GOOGLE_MAPS_KEY', "")


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


def has_menu_children(page):
    if page.get_children().filter(live=True, show_in_menus=True):
        return True
    else:
        return False


# Retrieves the top menu items - the immediate children of the parent page
# The has_menu_children method is necessary because the bootstrap menu requires
# a dropdown class to be applied to a parent
@register.inclusion_tag('demo/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().filter(
        live=True,
        show_in_menus=True
    )
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('demo/tags/hamburger_menu.html', takes_context=True)
def hamburger_menu(context, parent=None, calling_page=None):
    """
    This is a a multilingual hamburger menu link gnerator. It is used in the header
    nav bard.

    """
    
    lang = translation.get_language()
    

    if lang == 'es':
        home_page = SpanishHomePage.objects.all()[0]
    elif lang == 'en':
        home_page = EnglishHomePage.objects.all()[0]
    else:
        raise Exception("You must have an EnglishHomePage or a SpanishHomePage defined")

    generic_pages = home_page.get_children().type(GenericContentPage)
    section_pages = home_page.get_children().type(SectionPage)
    explore_page = home_page.get_children().type(ExploreSectionPage)[0]

    menuitems = []
    for page in generic_pages:
        menuitems.append({'href':page.url, 'verbose':page.title})

    for page in section_pages:
        menuitems.append({'href':"/%s/#%s" %(lang, page.slug) , 'verbose':page.title, 'section_page':True})

    # Split the title on white space and grab first word.
    menuitems.append({'href':"/%s/#%s" %(lang, explore_page.slug) , 'verbose':explore_page.title.split(" ")[0], 'section_page':True})

    # TODO These need to be filled in
    others = [
        {'href':'', 'verbose':'(%s) DATA' %(lang)},
        {'href':'', 'verbose':'(%s) CALENDAR' %(lang)},
        {'href':'', 'verbose':'(%s) NEWS' %(lang)},
        {'href':'', 'verbose':'(%s) SEARCH' %(lang)},
        {'href':'http://crop.apps.pointnineseven.com/visualize/#login=true', 'verbose':'(%s) SIGNUP/LOGIN' %(lang)},
        {'href':'', 'verbose':'(%s) SITEMAP' %(lang)},
    ]

    for page in others:
        menuitems.append({'href':page['href'], 'verbose':page['verbose']})


    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('demo/tags/sections_menu.html', takes_context=True)
def sections_menu(context):
    """
    These are for the explore, learn, and navigate page sections in the header
    """
    lang = translation.get_language()
    if lang == 'es':
        home_page = SpanishHomePage.objects.all()[0]
    elif lang == 'en':
        home_page = EnglishHomePage.objects.all()[0]
    else:
        raise Exception("You must have an EnglishHomePage or a SpanishHomePage defined")

    section_pages = home_page.get_children().type(SectionPage)
    explore_page = home_page.get_children().type(ExploreSectionPage)[0]

    menuitems = []
    for page in section_pages:
        menuitems.append({'href':"/%s/#%s" %(lang, page.slug) , 'verbose':page.title, 'section_page':True})
    
    # Split the title on white space and grab first word.
    menuitems.insert(1, {'href':"/%s/#%s" %(lang, explore_page.slug) , 'verbose':explore_page.title.split(" ")[0], 'section_page':True})

    return {
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('demo/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.filter(
        live=True,
        show_in_menus=True
    )
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the secondary links for the 'also in this section' links
# - either the children or siblings of the current page
@register.inclusion_tag('demo/tags/secondary_menu.html', takes_context=True)
def secondary_menu(context, calling_page=None):
    pages = []
    if calling_page:
        pages = calling_page.get_children().filter(
            live=True,
            show_in_menus=True
        )

        # If no children, get siblings instead
        if len(pages) == 0:
            pages = calling_page.get_other_siblings().filter(
                live=True,
                show_in_menus=True
            )
    return {
        'pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves all live pages which are children of the calling page
#for standard index listing
@register.inclusion_tag(
    'demo/tags/standard_index_listing.html',
    takes_context=True
)
def standard_index_listing(context, calling_page):
    pages = calling_page.get_children().filter(live=True)
    return {
        'pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Person feed for home page
@register.inclusion_tag(
    'demo/tags/person_listing_homepage.html',
    takes_context=True
)
def person_listing_homepage(context, count=2):
    people = PersonPage.objects.filter(live=True).order_by('?')
    return {
        'people': people[:count],
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Blog feed for home page
@register.inclusion_tag(
    'demo/tags/blog_listing_homepage.html',
    takes_context=True
)
def blog_listing_homepage(context, count=2):
    blogs = BlogPage.objects.filter(live=True).order_by('-date')
    return {
        'blogs': blogs[:count],
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Events feed for home page
@register.inclusion_tag(
    'demo/tags/event_listing_homepage.html',
    takes_context=True
)
def event_listing_homepage(context, count=2):
    events = EventPage.objects.filter(live=True)
    events = events.filter(date_from__gte=date.today()).order_by('date_from')
    return {
        'events': events[:count],
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Advert snippets
@register.inclusion_tag('demo/tags/adverts.html', takes_context=True)
def adverts(context):
    return {
        'adverts': Advert.objects.all(),
        'request': context['request'],
    }

@register.simple_tag()
def home_url():
    # provide root url for the current language
    return '/' + translation.get_language()



# Format times e.g. on event page
@register.filter
def time_display(time):
    # Get hour and minute from time object
    hour = time.hour
    minute = time.minute

    # Convert to 12 hour format
    if hour >= 12:
        pm = True
        hour -= 12
    else:
        pm = False
    if hour == 0:
        hour = 12

    # Hour string
    hour_string = str(hour)

    # Minute string
    if minute != 0:
        minute_string = "." + str(minute)
    else:
        minute_string = ""

    # PM string
    if pm:
        pm_string = "pm"
    else:
        pm_string = "am"

    # Join and return
    return "".join([hour_string, minute_string, pm_string])
