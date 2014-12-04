from __future__ import absolute_import

import urllib2, json

from django.core.mail import mail_managers

from demo.models import EnglishHomePage, SpanishHomePage, ExploreTopic, ExploreSectionPage

from celery import shared_task

@shared_task
def update_data_topics():
    """
    Updates the data topics if they match a theme ID.
    """
    # First get the updated data catalog from Marine Portal.
    email_body = "Attempting to update the CROP Data Catalog.\n\nFetching new catalog.\n"
    url = "http://planner.caribbean-mp.org/data_manager/get_catalog_json/"

    response = urllib2.urlopen(url)
    raw = response.read()
    data = json.loads(raw)
    themes = data['themes']

    email_body += "Got %s themes. \n" % len(themes)

    email_body += "The following Data Topics (Themes) where updated\n\n"
    for theme in themes:
        # Get Explore Topics from DB
        topics = ExploreTopic.objects.live().filter(mp_id=theme['id'])
        email_body += "Processing MP Theme (%s) %s\n" %( theme['id'], theme['name'])

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
            email_body += "- updated CMS topic (%s) %s\n" %(topic.mp_id, topic.title)
    print email_body
    mail_managers('CROP Data Catalog Updated', email_body, fail_silently=True)
