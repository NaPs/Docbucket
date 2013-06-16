import os

from django.core.management.base import NoArgsCommand
from django.conf import settings

from whoosh import index

from docbucket.models import DOCUMENT_WHOOSH_SCHEMA


class Command(NoArgsCommand):
    help = 'Create the index of search engine'

    def handle_noargs(self, *args, **options):
        if not os.path.exists(settings.WHOOSH_INDEX):
            os.mkdir(settings.WHOOSH_INDEX)
            index.create_in(settings.WHOOSH_INDEX, DOCUMENT_WHOOSH_SCHEMA)
