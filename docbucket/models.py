from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import tagging
from whoosh import fields, index

from .pdf import Pdf

class Document(models.Model):

    """ Represent a document managed by Docbucket
    """

    title = models.CharField(_('Title'), max_length=200)
    document = models.FileField(upload_to='documents')

    created_on = models.DateTimeField(auto_now_add=True)
    last_access_on = models.DateTimeField(auto_now_add=True)

    @property
    def pages(self):
        pdf = Pdf(self.document)
        return pdf.pages

    def touch(self):
        """ Touch the document and set the last access date to now.
        """
        self.last_access_on = datetime.now()
        self.save()


tagging.register(Document)


DOCUMENT_WHOOSH_SCHEMA = fields.Schema(title=fields.TEXT(stored=True),
                                       content=fields.TEXT,
                                       doc_id=fields.ID(stored=True, unique=True))


@receiver(post_save, sender=Document)
def document_update_index(sender, instance, created, **kwargs):
    """ Callback called each time a document is saved to update the search index.
    """
    ix = index.open_dir(settings.WHOOSH_INDEX)
    writer = ix.writer()
    pdf = Pdf(instance.document)
    if created:
        writer.add_document(title=instance.title,
                            content=pdf.to_text(),
                            doc_id=unicode(instance.id))
    else:
        writer.update_document(title=instance.title,
                               content=pdf.to_text(),
                               doc_id=unicode(instance.id))
    writer.commit()


@receiver(pre_delete, sender=Document)
def document_delete_index(sender, instance, **kwargs):
    """ Callback called each time a document is deleted to update the search index.
    """
    ix = index.open_dir(settings.WHOOSH_INDEX)
    ix.delete_by_term('doc_id', str(instance.id))
    ix.commit()