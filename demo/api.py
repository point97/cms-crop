from tastypie.resources import ModelResource
from demo.models import EventPage


class EventPageResource(ModelResource):
    class Meta:
        queryset = EventPage.objects.filter(live=True)
        resource_name = 'event'
        allowed_methods = ['get']
