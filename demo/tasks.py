from __future__ import absolute_import

from demo.models import EnglishHomePage, SpanishHomePage, ExploreTopic, ExploreSectionPage

from celery import shared_task



@shared_task
def add(x, y):
    return x + y


@shared_task
def update_data_topics(themes):
    """
    Updates the data topics if they match a theme ID.
    """
    for theme in themes:
        # Get Explore Topics from DB
        home_page = EnglishHomePage.objects.all()[0]
        exp_page = home_page.get_descendants().type(ExploreSectionPage)[0]
        # topics = ExploreTopic.objects.live().descendant_of(exp_page).filter(mp_id=theme['id'])
        topics = ExploreTopic.objects.live().filter(mp_id=theme['id'])
        for topic in topics:
            for layer in theme['layers']:
                if not layer['description'] and 'web_services_url' in layer.keys() and layer['web_services_url']:
                    # get the json object
                    response = urllib2.urlopen(layer['web_services_url'] + "?f=pjson")
                    raw = response.read()
                    data = json.loads(raw)
                    layer['description'] = data['description']

            topic.catalog = theme
            topic.save()
