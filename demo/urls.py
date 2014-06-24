from django.conf.urls import *
from demo.views import *


urlpatterns = patterns('',
    # For the set language form.
    (r'en', switch_to_en),
    (r'es', switch_to_es),
)
