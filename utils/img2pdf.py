import os.path

from fpdf import FPDF
from PIL import Image
from math import ceil
from os import listdir, getcwd

#max a4 size: 210,297
#1px=0.264583 mm

PAGE_SIZE_Y = 297 # размер страници
PAGE_SIZE_X = 210
PIXEL_SIZE = 0.264583 # размер пикселя в мм
SHAKAL = 0.5 # Степень сжатия изображения
OTSTUP_PX = 5

current_number = 1

VARIANT = ""

TEXT_HEIGHT = 20
TEXT_HEIGHT_MM = ceil(TEXT_HEIGHT * PIXEL_SIZE)
ZATICHKA_WEIGHT = 0

IMAGE_INTERVAL = 20

FONT_PATH = f"{getcwd()}/utils/data/timesnewromanpsmt.ttf"

img_on_pages = [] #Размещение картинок на страницах
img_sizes = [] # размеры картинок в mm
allowed_types = ['jpg', 'jpeg', 'png'] # Разрешённые типы


def px_to_mm(px): # преобразование пикселей в милиметры
    return ceil(px * PIXEL_SIZE * SHAKAL)


def get_shakal_coef(x):
    return (PAGE_SIZE_X - OTSTUP_PX * 2) / px_to_mm(x)


def get_sizes(image_paths: list): # Получение размеров изоюражений из папки images
    for i in image_paths:
        if i.split('.')[-1] in allowed_types:
            im = Image.open(i)
            width, height = im.size
            if px_to_mm(height) > PAGE_SIZE_Y - OTSTUP_PX * 2:
                print(ceil(height * PIXEL_SIZE))
                continue
            img_sizes.append((i, height * get_shakal_coef(width), width * get_shakal_coef(width)))
            im.close()
    img_sizes.sort(reverse=True, key=lambda x: x[1])


def make_page(current_number): # Создание удоборимой страници
    images_size = OTSTUP_PX + TEXT_HEIGHT
    ans = [(f"text:Вариант №{VARIANT}", OTSTUP_PX, ZATICHKA_WEIGHT)]
    while images_size < PAGE_SIZE_Y - OTSTUP_PX and len(img_sizes):
        for i in range(len(img_sizes)):
            if images_size + px_to_mm(img_sizes[i][1]) + TEXT_HEIGHT + TEXT_HEIGHT <= PAGE_SIZE_Y - OTSTUP_PX:
                images_size += px_to_mm(img_sizes[i][1]) + TEXT_HEIGHT + TEXT_HEIGHT
                ans.append((f"text:№{current_number}", TEXT_HEIGHT, ZATICHKA_WEIGHT))
                ans.append(img_sizes.pop(i))
                ans.append(("text:Ответ", TEXT_HEIGHT, ZATICHKA_WEIGHT))
                current_number += 1
                break
            if i == len(img_sizes):
                return ans, current_number
            if images_size + px_to_mm(img_sizes[-1][1]) + TEXT_HEIGHT + TEXT_HEIGHT > PAGE_SIZE_Y - OTSTUP_PX:
                return ans, current_number
    return ans, current_number


def make_pages(image_paths: list): # Планировка страниц
    get_sizes(image_paths)
    current_number = 1
    while len(img_sizes) != 0:
        page, current_number = make_page(current_number)
        if page:
            img_on_pages.append(page)


 
def img2pdf(pdf_name: str, image_paths: list): # Отрисовка страниц
    global VARIANT
    VARIANT = pdf_name.split('/')[-1]
    pdf = FPDF()
    pdf.add_font("Rus", fname=FONT_PATH, style="", uni=True)
    make_pages(image_paths)
    answers = []
    for i in img_on_pages:
        pdf.add_page()
        pos = OTSTUP_PX
        pdf.set_font("Rus", "", TEXT_HEIGHT)
        for j in i:
            if j[0].split(':')[0] == "text":
                pdf.text(OTSTUP_PX, pos + TEXT_HEIGHT, j[0].split(':')[1])
                pos = pos + TEXT_HEIGHT
            else:
                pdf.image(f'{j[0]}', x=OTSTUP_PX, y=pos, w=px_to_mm(j[2]), h=px_to_mm(j[1]))
                answers.append(os.path.split(j[0])[-1])
                pos = pos + px_to_mm(j[1])
    pdf.output(f"{pdf_name}.pdf")
    img_on_pages.clear()
    img_sizes.clear()
    return answers