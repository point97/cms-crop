from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# BASE_URL required for notification emails
BASE_URL = 'http://caribbean-mp.org'


BROKER_URL = 'redis://'
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_LOG_COLOR = False

try:
    from .local import *
except ImportError:
    pass