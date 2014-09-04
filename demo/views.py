import urllib2, json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from demo.models import MultiLingualPage, EnglishHomePage, ExploreSectionPage, ExploreTopic



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
        Send a GET request to the /webhook/?token=XXXXXXX&action=update-catalog
        If token passes validation then the appropriate action
    Params:

    - token - Unique token
    - action - Only cvalue accepted is 'update-catalog'


    Data catalog

    themes -- > ExploreTopics
    """

    if request.method == 'GET':

        qd = request.GET
        token = qd['token']
        action = qd['action']

        if token == 'a5680aa0-3473-11e4-8c21-0800200c9a66':
            if action == 'update-catalog':
                url = "http://crop.apps.pointnineseven.com/data_manager/get_json/"

                print "Updating catalog"
                response = urllib2.urlopen(url)
                raw = response.read()
                data = json.loads(raw)
                
                # Get themese and layers
                themes = data['themes']
                theme_ids = map(lambda x: x['id'], themes)
                all_layers = data['layers']

                # Get current Explore Topics from DB
                home_page = EnglishHomePage.objects.all()[0]
                exp_page = home_page.get_descendants().type(ExploreSectionPage)[0]
                # index = home_page.get_descendants().type(ExplorePageIndex)
                topics = ExploreTopic.objects.live().descendant_of(exp_page)

                # Loop over current topics and either update or delete them
                for topic in topics:
                    if topic.mp_id in theme_ids:
                        # update the info

                        # get the theme and its layers
                        theme = filter(lambda x: int(x['id']) == topic.mp_id, themes)[0]
                        layers = []
                        for layer_id in theme['layers']:
                            obj = filter(lambda x: int(x['id']) == layer_id, all_layers)[0] 
                            layers.append(obj)

                        rendered = render_to_string('demo/data_catalog.html', {'layers': layers})

                        topic.title = theme['display_name']
                        topic.short_description = theme['description']
                        topic.long_description = rendered
                        #catalogs = DataCatalogPage.objects.live().descendant_of(topic)

                        import pdb; pdb.set_trace()
                        topic.save()

                    elif not topic.default_topic:
                        # delete the topic if it is not the default topic
                        print 'Deleting topic %s' %(topic)


                return HttpResponse('Got it. Cool beans.')

    
    res = HttpResponse('Unauthorized')
    res.status_code = 401
    return res


