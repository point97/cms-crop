from tastypie.constants import ALL
from tastypie.resources import ModelResource
from demo.models import EventPage


class EventPageResource(ModelResource):
    """
    Endpoint /api/v1/event/?format=json

    """
    class Meta:
        queryset = EventPage.objects.filter(live=True)
        resource_name = 'event'
        allowed_methods = ['get']
        filtering = {
            'date_from':ALL,
            'url_path':ALL
        }

    
    def dehydrate_url_path(self, bundle):
        """
        For some reason we need to remove the /langroot/ prefix
        """

        return bundle.obj.url_path.replace("/langroot", "");
