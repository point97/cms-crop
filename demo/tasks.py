from __future__ import absolute_import

import urllib2, json

from django.core.mail import mail_managers

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
    email_body = "The following Data Topics where updated\n\n"
    for theme in themes:
        # Get Explore Topics from DB
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
            email_body += "(%s) %s\n" %(topic.mp_id, topic.title)

    mail_managers('CROP Data Catalog Updated', email_body, fail_silently=True)
