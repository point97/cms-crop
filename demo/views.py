import urllib2, json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from demo.models import MultiLingualPage, EnglishHomePage, ExploreSectionPage, ExploreTopic

from tasks import add, update_data_topics

def switch_to_en(request):
    return _switch_to_lang(request, 'en')

def switch_to_es(request):
    return _switch_to_lang(request, 'es')

def _switch_to_lang(request, dest_lang):
    '''
    Find the page object (should be a MultilingualPage) for the page
    that sent this POST and redirect to the matching page for the
    requested language.

    If no matching page is found, redirect to the home page for the
    destination language which should also be a MultilingualPage. 
    Loading a MultilingualPage is expected to set the session's
    language so that static translations also take affect.
    '''

    if request.method == 'POST':
        page_id = request.POST.get('requesting_page_id', None)
        if page_id is None:
            return

    page = get_object_or_404(MultiLingualPage, id=page_id)
    dest = '/' + dest_lang # default to homepage url

    if dest_lang == 'es' and page.is_english() and page.spanish_page() is not None:
        dest = page.spanish_page().url

    elif dest_lang == 'en' and page.is_spanish() and page.english_page() is not None:
        dest = page.english_page().url

    return HttpResponseRedirect(dest)


def webhook(request):
    """
    Usage:
        Send a GET request to the /webhook/?token=a5680aa0-3473-11e4-8c21-0800200c9a66&action=update-catalog
        If token passes validation then the appropriate action
    Params:

    - token - Unique token
    - action - Only cvalue accepted is 'update-catalog'


    Data catalog

    themes
        id
        layers : []

    """

    if request.method == 'GET':

        qd = request.GET
        token = qd['token']
        action = qd['action']

        if token == 'a5680aa0-3473-11e4-8c21-0800200c9a66':
            if action == 'update-catalog':
                url = "http://crop.apps.pointnineseven.com/data_manager/get_catalog_json/"

                print "Updating catalog"
                response = urllib2.urlopen(url)
                raw = response.read()
                data = json.loads(raw)

                # Get themes and layers from the JSON object
                themes = data['themes']

                update_data_topics.delay(themes)

                return HttpResponse('Got it. Cool beans.')


    res = HttpResponse('Unauthorized')
    res.status_code = 401
    return res



