"""Render the checked two-page Markdown write-up; documentation-only dependency."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/assessment_writeup.pdf'
INK = colors.HexColor('#152B3A')
STYLES = {
    'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=17,leading=20,textColor=INK,spaceAfter=8),
    'heading':ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=10.3,leading=12.5,textColor=INK,spaceBefore=7,spaceAfter=4),
    'body':ParagraphStyle('body',fontName='Helvetica',fontSize=8.6,leading=11.5,textColor=colors.HexColor('#26333B'),spaceAfter=6),
    'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=8,leading=10),
}


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#CCD7DE'))
    canvas.line(38,36,A4[0]-38,36)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(INK)
    canvas.drawString(38,23,'Insurance audit assessment | Frozen H1 / bounded H4 submission')
    canvas.drawRightString(A4[0]-38,23,str(document.page))
    canvas.restoreState()


def build():
    text=(ROOT/'docs/assessment_writeup.md').read_text()
    story=[]
    for page_no,page in enumerate(text.split('<!-- pagebreak -->')):
        if page_no:story.append(PageBreak())
        for block in page.strip().split('\n\n'):
            if block.startswith('|'):
                cells=[[c.strip() for c in row.strip('|').split('|')] for row in block.splitlines()]
                cells=[row for row in cells if not all(set(c)<=set('-: ') for c in row)]
                content=[[Paragraph(escape(c),STYLES['cell']) for c in row] for row in cells]
                table=Table(content,colWidths=[170,174,174],hAlign='LEFT')
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EEF2')),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7F9')]),
                    ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),
                    ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
                story.extend([table,Spacer(1,4)])
            else:
                style='title' if block.startswith('# ') else 'heading' if block.startswith('## ') else 'body'
                value=block.removeprefix('## ').removeprefix('# ')
                story.append(Paragraph(escape(value).replace('\n',' '),STYLES[style]))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=33,bottomMargin=48,
                          title='Contract-grounded invoice auditing',author='Insurance audit assessment',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUT)

if __name__=='__main__':build()
