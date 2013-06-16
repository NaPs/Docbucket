from cStringIO import StringIO

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams


class Pdf(object):

    def __init__(self, pdf_file):
        parser = PDFParser(pdf_file)
        self._doc = PDFDocument()
        parser.set_document(self._doc)
        self._doc.initialize
        self._doc.set_parser(parser)

    @property
    def pages(self):
        return len(tuple(self._doc.get_pages()))

    def to_text(self):
        rsrcmgr = PDFResourceManager()
        output = StringIO()
        laparams = LAParams()
        laparams.detect_vertical = True
        laparams.all_texts = True
        laparams.word_margin = 0.4
        device = TextConverter(rsrcmgr, output, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in self._doc.get_pages():
                interpreter.process_page(page)
        return output.getvalue().decode('utf-8', 'ignore')