from itertools import chain

from django import forms
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.core.urlresolvers import reverse


class PageSelector(forms.Widget):
    def __init__(self, attrs=None, choices=()):
        super(PageSelector, self).__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs)
        output = []
        output.append(u'<div id="pages"%s>' % forms.widgets.flatatt(final_attrs))
        output.append(u'<div class="btn-group">')
        output.append(u'<button class="action select btn btn-mini" href="#">Select all</button>')
        output.append(u'<button class="action deselect btn btn-mini" href="#">Deselect all</button>')
        output.append(u'</div>')
        output.append(u'<ul class="thumbnails">')
        pages = self.render_pages(name, choices, value)
        if pages:
            output.append(pages)
        output.append('</ul></div>')
        return mark_safe(u'\n'.join(output))

    def render_pages(self, name, choices, selected_pages):
        selected_pages = tuple([force_unicode(v) for v in selected_pages])
        output = []
        choices = self._reorder_choices_from_selected(selected_pages, chain(self.choices, choices))
        for i, (page_filename, page_name) in enumerate(choices):
            output.append(self.render_page(i, name, selected_pages, page_filename, page_name))
        return u'\n'.join(output)

    def render_page(self, idx, name, selected_pages, page_filename, page_name):
        page_filename = force_unicode(page_filename)
        page_name = page_name if len(page_name) < 16 else '%s...' % page_name[:16]
        checked = (page_filename in selected_pages) and u' checked="checked"' or ''
        # opts = (reverse('thumbnail-file', args=(page_filename,)), name, idx, name, checked,
        #         escape(page_filename), name, idx, conditional_escape(force_unicode(page_name)))
        opts = {'thumbnail': reverse('thumbnail-file', args=(page_filename,)),
                'name': name,
                'idx': idx,
                'checked': checked,
                'escaped_filename': escape(page_filename),
                'shown_filename': conditional_escape(force_unicode(page_name))}

        return (u'<li class="span3">'
                 '<div class="thumbnail">'
                 '<a href="%(thumbnail)s?size=800x800&format=.png" style="display: block;">'
                 '<img src="%(thumbnail)s?size=190x270"/>'
                 '</a>'
                 '<input id="id_%(name)s_%(idx)s" name="%(name)s"%(checked)s '
                 'value="%(escaped_filename)s" type="checkbox" class="check"/>'
                 '<label for="id_%(name)s_%(idx)s" class="pull-right">%(shown_filename)s</label>'
                 '</div></li>') % opts

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        for value1, value2 in zip(initial, data):
            if force_unicode(value1) != force_unicode(value2):
                return True
        return False

    def _reorder_choices_from_selected(self, selected, choices):
        choices = dict(choices)
        ordered_choices = list(selected)
        for c in choices:
            if c not in ordered_choices:
                ordered_choices.append(c)
        real_choices = []
        for c in ordered_choices:
            real_choices.append((c, choices[c]))
        return real_choices
