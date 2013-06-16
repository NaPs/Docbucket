import os
from StringIO import StringIO

from django.conf import settings

from PIL import Image


def make_thumbnails(filename):
    image = Image.open(filename)
    thumbnails = {}

    for name, size in settings.THUMBNAILS_SIZES.iteritems():
        thumb = image.copy()
        thumb.thumbnail(size, Image.ANTIALIAS)
        thumb_file = StringIO()
        thumb.save(thumb_file, format='PNG')
        thumb_file.seek(0)
        thumbnails[name] = thumb_file

    return thumbnails