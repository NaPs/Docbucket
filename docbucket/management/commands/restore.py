import sys
import json
import zipfile
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from docbucket.models import Document


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class Command(BaseCommand):
    help = 'Restore documents saved by the backup command'
    args = '<input filename>'

    def handle(self, input_filename, *args, **options):
        output = zipfile.ZipFile(input_filename, 'r')
        documents = json.loads(output.read('documents.json'))
        print 'Importing documents...'
        for document in documents:
            doc = Document(title=document['title'],
                           created_on=datetime.strptime(document['created_on'][:19], DATETIME_FORMAT),
                           last_access_on=datetime.strptime(document['last_access_on'][:19], DATETIME_FORMAT),
                           document=ContentFile(output.read('files/%s' % document['key']),
                                                u'%s.pdf' % document['title'].replace('/', '-')))
            doc.save()
            doc.tags = ', '.join(['"%s"' % t for t in document['tags']])
            sys.stdout.write('.')
            sys.stdout.flush()
        print '\nAll done.'

