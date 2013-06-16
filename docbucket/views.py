import os
import re
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse
from django.core.files import File
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from tagging.models import Tag
from whoosh import index
from whoosh.qparser import MultifieldParser
from pgmagick import Image, FilterTypes, Blob

from .models import Document
from .compilers import load_compilers


def home(request):
    """ Docbucket index page.
    """
    ctx = {'recent_documents': Document.objects.all().order_by('-created_on')[:5],
           'total_count': Document.objects.count(),
           'total_tags': Document.tags.count(),
           'total_size': sum(x.document.size for x in Document.objects.all())}
    return render(request, 'home.html', ctx)


def show(request, doc_id):
    """ Show a document.
    """

    document = get_object_or_404(Document, id=doc_id)
    document.touch()
    return render(request, 'show.html', {'document': document})


def list(request, tag_name=None):
    """ List documents.
    """
    if tag_name is None:
        documents = Document.objects.all()
    else:
        tag = Tag.objects.get(name=tag_name)
        documents = Document.tagged.with_any(tag)

    pages = Paginator(documents, 30)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        documents = pages.page(page)
    except (EmptyPage, InvalidPage):
        documents = pages.page(pages.num_pages)

    return render(request, 'list.html', {'documents': documents.object_list,
                                         'paginator': documents})


def search(request):
    ix = index.open_dir(settings.WHOOSH_INDEX)
    query = request.GET.get('query', None)
    page = request.GET.get('page', 1)
    if isinstance(page, unicode) and page.isdigit():
        page = int(page)
    else:
        page = 1
    found = None

    if query is not None and query != u'':
        query = query.replace('+', ' AND ').replace(' -', ' NOT ')
        parser = MultifieldParser(('title', 'content', 'doc_id'),
                                   schema=ix.schema)
        try:
            parsed_query = parser.parse(query)
        except:
            parsed_query = None

        if query is not None:
            searcher = ix.searcher()
            found = searcher.search_page(parsed_query, page, pagelen=30)

    found_docs = []
    for i, found_doc in enumerate(found):
        doc = Document.objects.get(id=found_doc['doc_id'])
        #found_docs.append({'doc': doc, 'score': found.score(i)})
        found_docs.append(doc)

    cntx = {'documents': found_docs, 'search': found, 'query': query,
            'page_results': len(found_docs), 'next_page': page + 1,
            'previous_page': page - 1, 'page': page,
            'max_pages': found.pagecount}

    return render(request, 'search.html', cntx)


def create(request, compiler):
    """ Document creation page.
    """
    compilers = load_compilers()
    compiler = compilers[compiler]()
    if request.method == 'POST':
        form = compiler.get_form(request.POST)
        if form.is_valid():
            doc = Document()
            doc.title = form.cleaned_data.get('title')
            # Create the PDF itself:
            pages = form.cleaned_data.get('pages')
            pages = [os.path.join(settings.INCOMING_DIRECTORY, p) for p in pages]
            pdf_output = compiler.compile_files(pages)
            doc.document = File(pdf_output, name='%s.pdf' % doc.title.replace('/', '-'))
            doc.save()

            # The document must exists before to be tagged:
            doc.tags = form.cleaned_data.get('tags')

            # Delete the original files:
            for page in pages:
                os.unlink(page)

            return redirect('show', doc_id=doc.id)

    else:
        form = compiler.get_form()

    return render(request, 'create.html', {'form': form})


def thumbnail(request, type, identifier):
    response = HttpResponse(mimetype='image/png')
    size = str(request.GET.get('size', '190x270'))
    if not re.match('\d+[x]\d+', size):
        size = '190x270'

    cache_key = 'thumbnail:%s:%s:%s' % (type, identifier, size)
    cached = cache.get(cache_key)
    if cached is None:
        if type == 'file':
            file_ = str(os.path.join(settings.INCOMING_DIRECTORY, identifier))
        elif type == 'document':
            document = get_object_or_404(Document, pk=identifier)
            file_ = Blob(document.document.read())

        image = Image(file_)
        image.filterType(FilterTypes.SincFilter)
        image.scale(size)

        output = Blob()
        image.write(output, 'png')
        response.write(output.data)
        cache.set(cache_key, output.data)
    else:
        response.write(cached)

    return response


@csrf_exempt
def ajax_document(request, doc_id):
    """ Update a document (used by ajax).

    This view will be replaced by a more complete API later.
    """

    document = get_object_or_404(Document, id=doc_id)
    field = request.POST.get('name')
    value = request.POST.get('value')
    if field == 'title' and value.strip():
        document.title = value
    elif field == 'tags':
        document.tags = value
    document.save()
    return HttpResponse()


@csrf_exempt
def ajax_tags(request):
    """ Get all used tags.
    """
    tags = [{'tag': t.name} for t in Document.tags.all()]
    return HttpResponse(json.dumps({'tags': tags}))