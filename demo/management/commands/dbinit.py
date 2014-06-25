
from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):
    help = 'Adds the p97dev superuser'
    

    def handle(self, *args, **options):
        from demo import dbinit

