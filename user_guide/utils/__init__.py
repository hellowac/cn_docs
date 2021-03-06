import logging

import os

from .rltemplate import RLDocTemplate
from .stylesheet import getStyleSheet, getCnStyleSheet, CnParagraphStyle

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    figures,
    Paragraph,
    Spacer,
    Preformatted,
    PageBreak,
    CondPageBreak,
    Flowable,
    Table,
    TableStyle,
    NextPageTemplate,
    KeepTogether,
    Image,
    XPreformatted,
)
from reportlab.platypus.xpreformatted import PythonPreformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.sequencer import getSequencer
from reportlab.lib.fonts import tt2ps
from xml.sax.saxutils import escape as xmlEscape

from .t_parse import Template


logger = logging.getLogger(__name__)

QFcodetemplate = Template("X$X$", "X")
QFreptemplate = Template("X^X^", "X")
codesubst = "%s<font name=Courier><nobr>%s</nobr></font>"
QFsubst = "%s<font name=Courier><i><nobr>%s</nobr></i></font>"

styleSheet = getStyleSheet()
cn_styleSheet = getCnStyleSheet()

H1 = styleSheet['Heading1']
H2 = styleSheet['Heading2']
H3 = styleSheet['Heading3']
H4 = styleSheet['Heading4']
B = styleSheet['BodyText']
BU = styleSheet['Bullet']
Comment = styleSheet['Comment']
Centred = styleSheet['Centred']
Caption = styleSheet['Caption']

cn_H1 = cn_styleSheet['Heading1']
cn_H2 = cn_styleSheet['Heading2']
cn_H3 = cn_styleSheet['Heading3']
cn_H4 = cn_styleSheet['Heading4']
cn_B = cn_styleSheet['BodyText']
cn_BU = cn_styleSheet['Bullet']
cn_Comment = cn_styleSheet['Comment']
cn_Centred = cn_styleSheet['Centred']
cn_Caption = cn_styleSheet['Caption']

# set up numbering
seq = getSequencer()
seq.setFormat('Chapter', '1')
seq.setFormat('Section', '1')
seq.setFormat('Appendix', 'A')
seq.setFormat('Figure', '1')
seq.chain('Chapter', 'Section')
seq.chain('Chapter', 'Figure')

lessonnamestyle = H2
discussiontextstyle = B
exampletextstyle = styleSheet['Code']

cn_lessonnamestyle = cn_H2
cn_discussiontextstyle = cn_B
cn_exampletextstyle = cn_styleSheet['Code']

# size for every example
examplefunctionxinches = 5.5
examplefunctionyinches = 3
examplefunctiondisplaysizes = (
    examplefunctionxinches * inch,
    examplefunctionyinches * inch,
)

appmode = 0


def quickfix(text):
    """inside text find any subsequence of form $subsequence$.
    Format the subsequence as code.  If similarly if text contains ^arg^
    format the arg as replaceable.  The escape sequence for literal
    $ is $\\$ (^ is ^\\^.
    """
    # logger.info('<<' + '=' * 100)
    # logger.info(f'text: {text}')

    for (template, subst) in [
        (QFcodetemplate, codesubst),
        (QFreptemplate, QFsubst),
    ]:
        fragment = text
        parts = []
        try:
            while fragment:
                try:
                    (matches, index) = template.PARSE(fragment)
                except:
                    raise ValueError
                else:
                    [prefix, code] = matches
                    if code == "\\":
                        part = fragment[:index]
                    else:
                        part = subst % (prefix, code)
                    parts.append(part)
                    fragment = fragment[index:]
        except ValueError:
            parts.append(fragment)
        text = ''.join(parts)

    # logger.info(f'quickfix text: {text}')
    # logger.info('=' * 100 + '>> \n\n')
    return text


def getJustFontPaths():
    '''return afm and pfb for Just's files'''
    import reportlab

    folder = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'
    return os.path.join(folder, 'DarkGardenMK.afm'), os.path.join(
        folder, 'DarkGardenMK.pfb'
    )


# for testing
def NOP(*x, **y):
    return None


def CPage(inches):
    getStory().append(CondPageBreak(inches * inch))


def newPage():
    getStory().append(PageBreak())


def nextTemplate(templName):
    f = NextPageTemplate(templName)
    getStory().append(f)


def disc(text, klass=Paragraph, style=discussiontextstyle):
    text = quickfix(text)
    P = klass(text, style)
    getStory().append(P)


def cn_disc(text, klass=Paragraph, style=cn_discussiontextstyle):
    text = quickfix(text)
    P = klass(text, style)
    getStory().append(P)


def restartList():
    getSequencer().reset('list1')


def list1(text, doBullet=1):
    text = quickfix(text)
    if doBullet:
        text = '<bullet><seq id="list1"/>.</bullet>' + text
    P = Paragraph(text, BU)
    getStory().append(P)


def bullet(text):
    text = u'<bullet><font name="Symbol">\u2022</font></bullet>' + quickfix(
        text
    )
    P = Paragraph(text, style=BU)
    getStory().append(P)


def cn_bullet(text):
    text = u'<bullet><font name="Symbol">\u2022</font></bullet>' + quickfix(
        text
    )
    P = Paragraph(text, style=cn_BU)
    getStory().append(P)


def eg(text, before=0.1, after=0, klass=PythonPreformatted):
    space(before)
    disc(text, klass=klass, style=exampletextstyle)
    space(after)


def cn_eg(text, before=0.1, after=0, klass=PythonPreformatted):
    space(before)
    disc(text, klass=klass, style=cn_exampletextstyle)
    space(after)


def npeg(text, before=0.1, after=0):
    eg(text, before=before, after=after, klass=XPreformatted)


def cn_npeg(text, before=0.1, after=0):
    cn_eg(text, before=before, after=after, klass=XPreformatted)


def space(inches=1.0 / 6):
    if inches:
        getStory().append(Spacer(0, inches * inch))


def EmbeddedCode(code, name='t'):
    eg(code)
    disc("produces")
    exec(code + ("\ngetStory().append(%s)\n" % name))


def startKeep():
    return len(getStory())


def endKeep(s):
    store = getStory()
    k = KeepTogether(store[s:])
    store[s:] = [k]


def title(text):
    """Use this for the document title only"""
    disc(text, style=styleSheet['Title'])


def cn_title(text):
    """Use this for the document title only"""
    disc(text, style=cn_styleSheet['Title'])


# AR 3/7/2000 - defining three new levels of headings; code
# should be swapped over to using them.


def headingTOC(text):
    getStory().append(PageBreak())
    p = Paragraph(text, H1)
    getStory().append(p)


def cn_headingTOC(text):
    getStory().append(PageBreak())
    p = Paragraph(text, cn_H1)
    getStory().append(p)


def heading1(text):
    """Use this for chapters.  Lessons within a big chapter
    should now use heading2 instead.  Chapters get numbered."""
    getStory().append(PageBreak())
    p = Paragraph('Chapter <seq id="Chapter"/> ' + quickfix(text), H1)
    getStory().append(p)


def cn_heading1(text):
    getStory().append(PageBreak())
    p = Paragraph('第 <seq id="Chapter"/> 章  ' + quickfix(text), cn_H1)
    getStory().append(p)


def Appendix1(
    text,
):
    global appmode
    getStory().append(PageBreak())
    if not appmode:
        seq.setFormat('Chapter', 'A')
        seq.reset('Chapter')
        appmode = 1
    p = Paragraph('Appendix <seq id="Chapter"/> ' + quickfix(text), H1)
    getStory().append(p)


def cn_Appendix1(text):
    global appmode
    getStory().append(PageBreak())
    if not appmode:
        seq.setFormat('Chapter', 'A')
        seq.reset('Chapter')
        appmode = 1
    p = Paragraph('附录 <seq id="Chapter"/> ' + quickfix(text), cn_H1)
    getStory().append(p)


def heading2(text):
    """Used to be 'lesson'"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(
        '<seq template="%(Chapter)s.%(Section+)s "/>' + quickfix(text), H2
    )
    getStory().append(p)


def cn_heading2(text):
    """Used to be 'lesson'"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(
        '<seq template="%(Chapter)s.%(Section+)s "/>' + quickfix(text), cn_H2
    )
    getStory().append(p)


def heading3(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H3)
    getStory().append(p)


def cn_heading3(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), cn_H3)
    getStory().append(p)


def image(path, width=None, height=None):
    s = startKeep()
    space(0.2)
    import reportlab

    rlDocImageDir = os.path.join(
        os.path.dirname(reportlab.__file__), 'docs', 'images'
    )
    getStory().append(Image(os.path.join(rlDocImageDir, path), width, height))
    space(0.2)
    endKeep(s)


def cn_image(path, width=None, height=None):
    s = startKeep()
    space(0.2)
    import reportlab

    rlDocImageDir = os.path.join(
        os.path.dirname(reportlab.__file__), 'docs', 'images'
    )
    getStory().append(Image(os.path.join(rlDocImageDir, path), width, height))
    space(0.2)
    endKeep(s)


def heading4(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H4)
    getStory().append(p)


def cn_heading4(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), cn_H4)
    getStory().append(p)


def todo(text):
    """Used for notes to ourselves"""
    getStory().append(Paragraph(quickfix(text), Comment))


def cn_todo(text):
    """Used for notes to ourselves"""
    getStory().append(Paragraph(quickfix(text), cn_Comment))


def centred(text):
    getStory().append(Paragraph(quickfix(text), Centred))


def cn_centred(text):
    getStory().append(Paragraph(quickfix(text), cn_Centred))


def caption(text):
    getStory().append(Paragraph(quickfix(text), Caption))


def cn_caption(text):
    getStory().append(Paragraph(quickfix(text), cn_Caption))


class Illustration(figures.Figure):
    """The examples are all presented as functions which do
    something to a canvas, with a constant height and width
    used.  This puts them inside a figure box with a caption."""

    def __init__(self, operation, caption, width=None, height=None):
        stdwidth, stdheight = examplefunctiondisplaysizes
        if not width:
            width = stdwidth
        if not height:
            height = stdheight
        # figures.Figure.__init__(self, stdwidth * 0.75, stdheight * 0.75)
        figures.Figure.__init__(
            self,
            width,
            height,
            'Figure <seq template="%(Chapter)s-%('
            'Figure+)s"/>: ' + quickfix(caption),
        )
        self.operation = operation

    def drawFigure(self):
        # shrink it a little...
        # self.canv.scale(0.75, 0.75)
        self.operation(self.canv)


class CnIllustration(figures.Figure):
    """The examples are all presented as functions which do
    something to a canvas, with a constant height and width
    used.  This puts them inside a figure box with a caption."""

    def __init__(self, operation, caption, width=None, height=None):
        stdwidth, stdheight = examplefunctiondisplaysizes
        if not width:
            width = stdwidth
        if not height:
            height = stdheight
        # figures.Figure.__init__(self, stdwidth * 0.75, stdheight * 0.75)
        figures.Figure.__init__(
            self,
            width,
            height,
            '图 <seq template="%(Chapter)s - %('
            'Figure+)s"/> : ' + quickfix(caption),
            captionFont=tt2ps('SourceHanSansSC', 0, 1),
        )
        self.operation = operation

    def drawFigure(self):
        # shrink it a little...
        # self.canv.scale(0.75, 0.75)
        self.operation(self.canv)


def illust(operation, caption, width=None, height=None):
    i = Illustration(operation, caption, width=width, height=height)
    getStory().append(i)


def cn_illust(operation, caption, width=None, height=None):
    i = CnIllustration(operation, caption, width=width, height=height)
    getStory().append(i)


class GraphicsDrawing(Illustration):
    """Lets you include reportlab/graphics drawings seamlessly,
    with the right numbering."""

    def __init__(self, drawing, caption):
        figures.Figure.__init__(
            self,
            drawing.width,
            drawing.height,
            'Figure <seq template="%(Chapter)s-%('
            'Figure+)s"/>: ' + quickfix(caption),
        )
        self.drawing = drawing

    def drawFigure(self):
        d = self.drawing
        d.wrap(d.width, d.height)
        d.drawOn(self.canv, 0, 0)


class CnGraphicsDrawing(CnIllustration):
    """Lets you include reportlab/graphics drawings seamlessly,
    with the right numbering."""

    def __init__(self, drawing, caption):
        figures.Figure.__init__(
            self,
            drawing.width,
            drawing.height,
            '图 <seq template="%(Chapter)s - %('
            'Figure+)s"/> : ' + quickfix(caption),
            captionFont=tt2ps('SourceHanSansSC', 0, 1),
        )
        self.drawing = drawing

    def drawFigure(self):
        d = self.drawing
        d.wrap(d.width, d.height)
        d.drawOn(self.canv, 0, 0)


def draw(drawing, caption):
    d = GraphicsDrawing(drawing, caption)
    getStory().append(d)


def cn_draw(drawing, caption):
    d = CnGraphicsDrawing(drawing, caption)
    getStory().append(d)


class ParaBoxBase(figures.Figure):
    def wrap(self, availWidth, availHeight):
        """Left 30% is for attributes, right 50% for sample,
        10% gutter each side."""
        self.x0 = availWidth * 0.05  # left of box
        self.x1 = availWidth * 0.1  # left of descriptive text
        self.x2 = availWidth * 0.5  # left of para itself
        self.x3 = availWidth * 0.9  # right of para itself
        self.x4 = availWidth * 0.95  # right of box
        self.width = self.x4 - self.x0
        self.dx = 0.5 * (availWidth - self.width)

        paw, self.pah = self.para.wrap(self.x3 - self.x2, availHeight)
        self.pah = self.pah + self.style.spaceBefore + self.style.spaceAfter
        prw, self.prh = self.pre.wrap(self.x2 - self.x1, availHeight)
        self.figureHeight = max(self.prh, self.pah) * 10.0 / 9.0
        return figures.Figure.wrap(self, availWidth, availHeight)

    def getStyleText(self, style):
        """Converts style to preformatted block of text"""
        lines = []
        for key, value in style.__dict__.items():
            lines.append('%s = %s' % (key, value))
        lines.sort()
        return '\n'.join(lines)

    def drawFigure(self):

        # now we fill in the bounding box and before/after boxes
        self.canv.saveState()
        self.canv.setFillGray(0.95)
        self.canv.setDash(1, 3)
        self.canv.rect(
            self.x2 - self.x0,
            self.figureHeight * 0.95 - self.pah,
            self.x3 - self.x2,
            self.para.height,
            fill=1,
            stroke=1,
        )

        self.canv.setFillGray(0.90)
        self.canv.rect(
            self.x2 - self.x0,  # spaceBefore
            self.figureHeight * 0.95 - self.pah + self.para.height,
            self.x3 - self.x2,
            self.style.spaceBefore,
            fill=1,
            stroke=1,
        )

        self.canv.rect(
            self.x2 - self.x0,  # spaceBefore
            self.figureHeight * 0.95 - self.pah - self.style.spaceAfter,
            self.x3 - self.x2,
            self.style.spaceAfter,
            fill=1,
            stroke=1,
        )

        self.canv.restoreState()
        # self.canv.setFillColor(colors.yellow)
        self.para.drawOn(
            self.canv, self.x2 - self.x0, self.figureHeight * 0.95 - self.pah
        )
        self.pre.drawOn(
            self.canv, self.x1 - self.x0, self.figureHeight * 0.95 - self.prh
        )

    def getStyleText(self, style):
        """Converts style to preformatted block of text"""
        lines = []
        for key, value in sorted(style.__dict__.items()):
            if key not in ('name', 'parent'):
                lines.append('%s = %s' % (key, value))
        return '\n'.join(lines)


class ParaBox(ParaBoxBase):
    """Illustrates paragraph examples, with style attributes on the left"""

    descrStyle = ParagraphStyle(
        'description', fontName='Courier', fontSize=8, leading=9.6
    )

    def __init__(self, text, style, caption):
        super().__init__(0, 0, caption)
        self.text = text
        self.style = style
        self.para = Paragraph(text, style)

        styleText = self.getStyleText(style)
        self.pre = Preformatted(styleText, self.descrStyle)


class CnParaBox(ParaBoxBase):
    descrStyle = ParagraphStyle(
        'description', fontName='SourceHanSansSC', fontSize=8, leading=9.6
    )

    def __init__(self, text, style, caption):
        super().__init__(0, 0, caption=caption, captionFont='SourceHanSansSC')
        self.text = text
        self.style = style
        self.para = Paragraph(text, style)

        styleText = self.getStyleText(style)
        self.pre = Preformatted(styleText, self.descrStyle)


class ParaBox2Base(figures.Figure):
    def wrap(self, availWidth, availHeight):
        self.width = availWidth * 0.9
        colWidth = 0.4 * self.width
        lw, self.lh = self.left.wrap(colWidth, availHeight)
        rw, self.rh = self.right.wrap(colWidth, availHeight)
        self.figureHeight = max(self.lh, self.rh) * 10.0 / 9.0
        return figures.Figure.wrap(self, availWidth, availHeight)

    def drawFigure(self):
        self.left.drawOn(
            self.canv, self.width * 0.05, self.figureHeight * 0.95 - self.lh
        )
        self.right.drawOn(
            self.canv, self.width * 0.55, self.figureHeight * 0.95 - self.rh
        )


class ParaBox2(ParaBox2Base):
    """Illustrates a paragraph side-by-side with the raw
    text, to show how the XML works."""

    def __init__(self, text, caption):
        figures.Figure.__init__(self, 0, 0, caption)
        descrStyle = ParagraphStyle(
            'description', fontName='Courier', fontSize=8, leading=9.6
        )
        self.text = text
        self.left = Paragraph(xmlEscape(text), descrStyle)
        self.right = Paragraph(text, B)


class CnParaBox2(ParaBox2Base):
    def __init__(self, text, caption):
        figures.Figure.__init__(
            self, 0, 0, caption, captionFont='SourceHanSansSC'
        )
        descrStyle = ParagraphStyle(
            'description', fontName='SourceHanSansSC', fontSize=8, leading=9.6
        )
        self.text = text
        self.left = Paragraph(xmlEscape(text), descrStyle)
        self.right = Paragraph(text, cn_B)


def parabox(text, style, caption):
    p = ParaBox(
        text,
        style,
        'Figure <seq template="%(Chapter)s-%(Figure+)s"/>: '
        + quickfix(caption),
    )
    getStory().append(p)


def cn_parabox(text, style, caption):
    p = CnParaBox(
        text,
        style,
        '图 <seq template="%(Chapter)s-%(Figure+)s"/>: ' + quickfix(caption),
    )
    getStory().append(p)


def parabox2(text, caption):
    p = ParaBox2(
        text,
        'Figure <seq template="%(Chapter)s-%(Figure+)s"/>: '
        + quickfix(caption),
    )
    getStory().append(p)


def cn_parabox2(text, caption):
    p = CnParaBox2(
        text,
        '图 <seq template="%(Chapter)s-%(Figure+)s"/>: ' + quickfix(caption),
    )
    getStory().append(p)


def pencilnote():
    from . import examples

    getStory().append(examples.NoteAnnotation())


from reportlab.lib.colors import tan, green


def handnote(xoffset=0, size=None, fillcolor=tan, strokecolor=green):
    from . import examples

    getStory().append(
        examples.HandAnnotation(xoffset, size, fillcolor, strokecolor)
    )


# make a singleton, created when requested rather
# than each time a chapter imports it.
_story = []


def setStory(story=[]):
    global _story
    _story = story


def getStory():
    return _story
