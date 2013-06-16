import os
import sys
import json
import zipfile

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from docbucket.models import Document


class Command(BaseCommand):
    help = 'Generate an archive of all documents'
    args = '<output filename>'

    def handle(self, output_filename, *args, **options):
        documents = []
        output = zipfile.ZipFile(output_filename, 'w')
        print 'Copying documents...'
        for i, document in enumerate(Document.objects.all()):
            documents.append({'key': i,
                              'title': document.title,
                              'created_on': document.created_on,
                              'last_access_on': document.last_access_on,
                              'tags': [x.name for x in document.tags]})
            output.writestr('files/%s' % i, document.document.read())
            sys.stdout.write('.')
            sys.stdout.flush()
        print '\nWriting metadata...'
        output.writestr('documents.json', json.dumps(documents, cls=DjangoJSONEncoder))
        print 'All done.'