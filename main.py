import json

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, NextPageTemplate

# ─── Регистрация шрифтов ──────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont("Menu", "data/menu.ttf"))
# ─── Контент ──────────────────────────────────────────────────────────────────
OUTPUT_FILE = "menu.pdf"
with open(f'data/menu.json', 'r', encoding='utf-8') as f:
    file = json.load(f)
    sections = file['entries']
blue_list = ['Завтраки', 'Первые блюда', 'Вторые блюда', 'Шашлыки', 'Холодные закуски', 'Шаурма']
# ─── Цвета ────────────────────────────────────────────────────────────────────
BG_COLOR = colors.HexColor("#000000")
TEXT_COLOR = colors.HexColor("#ffffff")
BLUE_LINK_COLOR = colors.HexColor("#4ABFC8")
RED_LINK_COLOR = colors.HexColor("#d53128")
# ─── Стили ────────────────────────────────────────────────────────────────────
main_title_style = ParagraphStyle(
    "DocTitle", fontName="Menu", fontSize=40, leading=60, alignment=1, textColor=TEXT_COLOR)
# Ссылки
blue_link_style = ParagraphStyle(
    "TOCLinkBlue", fontName="Menu", fontSize=31, leading=45, alignment=1, textColor=BLUE_LINK_COLOR)
red_link_style = ParagraphStyle(
    "TOCLinkRed", fontName="Menu", fontSize=31, leading=45, alignment=1, textColor=RED_LINK_COLOR)
# Заголовки
blue_heading_style = ParagraphStyle(
    "SectionHeadingBlue", fontName="Menu", fontSize=40, leading=50, spaceBefore=24, spaceAfter=10,
    textColor=BLUE_LINK_COLOR)
red_heading_style = ParagraphStyle(
    "SectionHeadingRed", fontName="Menu", fontSize=40, leading=50, spaceBefore=24, spaceAfter=10,
    textColor=RED_LINK_COLOR)
# Основной текст
body_style = ParagraphStyle("Body", fontName="Menu", fontSize=30, leading=35, textColor=TEXT_COLOR)


# ─── Функции ──────────────────────────────────────────────────────────────────
def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_COLOR)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    if doc.page == 1:
        canvas.drawImage("data/main.jpg", x=0, y=0, width=A4[0], height=A4[1], mask="auto")
    if doc.page == 10:
        canvas.drawImage("data/last.jpg", x=0, y=0, width=A4[0], height=A4[1], mask="auto")


def make_dotted_line(name, price, font_name, font_size):
    max_width = A4[0] - 120
    name_width = stringWidth(name, font_name, font_size)
    price_width = stringWidth(str(price), font_name, font_size)
    dot_width = stringWidth(".", font_name, font_size)

    available = max_width - name_width - price_width
    dot_count = int(available / dot_width) - 3

    return f'{name}{"." * dot_count}{price}'


def make_toc_link(section):
    color = "#4ABFC8" if section["title"] in blue_list else "#d53128"
    style = blue_link_style if section["title"] in blue_list else red_link_style
    return Paragraph(f'<a href="#{section["anchor"]}" color="{color}">{section["title"]}</a>', style)


# ─── Сборка ───────────────────────────────────────────────────────────────────
first_page_frame = Frame(x1=10, y1=60, width=A4[0] - 20, height=A4[1] - 300, id="first")
later_pages_frame = Frame(x1=60, y1=0, width=A4[0] - 120, height=A4[1] - 10, id="later")

first_template = PageTemplate(id="First", frames=first_page_frame, onPage=draw_background)
later_template = PageTemplate(id="Later", frames=later_pages_frame, onPage=draw_background)

doc = BaseDocTemplate(OUTPUT_FILE, pagesize=A4)
doc.addPageTemplates([first_template, later_template])

story = []
story.append(NextPageTemplate("Later"))
# ─── Заполнение меню ──────────────────────────────────────────────────────────
story.append(Paragraph("Содержание:", main_title_style))

FRAME_WIDTH = A4[0] - 40
rows = []
for i in range(0, len(sections), 2):
    left = make_toc_link(sections[i])
    right = make_toc_link(sections[i + 1]) if i + 1 < len(sections) else Paragraph("", blue_link_style)
    rows.append([left, right])

toc_table = Table(rows, colWidths=[FRAME_WIDTH / 2, FRAME_WIDTH / 2])
toc_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
]))

story.append(toc_table)
story.append(PageBreak())
story.append(NextPageTemplate("Later"))

for section in sections:
    style = blue_heading_style if section["title"] in blue_list else red_heading_style
    story.append(Paragraph(f'<a name="{section["anchor"]}"/>{section["title"]}', style))

    # for item in section['menu']:
    #     line = make_dotted_line(item["name"], item["price"], "Menu", 30)
    #     story.append(Paragraph(line, body_style))

    LATER_FRAME_WIDTH = A4[0] - 120
    for item in section['menu']:
        row = [[Paragraph(item["name"], body_style), Paragraph(str(item["price"]), body_style)]]

        price_width = stringWidth(str(item["price"]), "Menu", 30) + 10

        item_table = Table(row, colWidths=[LATER_FRAME_WIDTH - price_width, price_width])
        item_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Menu"),
            ("FONTSIZE", (0, 0), (-1, -1), 30),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_COLOR),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(item_table)

# ─── Генерация PDF ────────────────────────────────────────────────────────────
doc.build(story)
print(f"Создан: {OUTPUT_FILE}")
