import os
import sys

from django.core.management.base import NoArgsCommand
from django.conf import settings

from whoosh import index

from docbucket.models import DOCUMENT_WHOOSH_SCHEMA, Document


class Command(NoArgsCommand):
    help = 'Reindex all documents'

    def handle_noargs(self, *args, **options):
        print 'Clearing current index...'
        if not os.path.exists(settings.WHOOSH_INDEX):
            os.mkdir(settings.WHOOSH_INDEX)
        index.create_in(settings.WHOOSH_INDEX, DOCUMENT_WHOOSH_SCHEMA)
        print 'Indexing documents...'
        for document in Document.objects.all():
            document.save()  # A save will trigger a re-index of the document
            sys.stdout.write('.')
            sys.stdout.flush()
        print '\nAll done.'
