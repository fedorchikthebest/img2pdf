from fpdf import FPDF
from PIL import Image
from math import ceil
from os import listdir

#max a4 size: 210,297
#1px=0.264583 mm

PAGE_SIZE_Y = 297 # размер страници
PAGE_SIZE_X = 210
PIXEL_SIZE = 0.264583 # размер пикселя в мм
SHAKAL = 0.5 # Степень сжатия изображения
OTSTUP_PX = 5

img_on_pages = [] #Размещение картинок на страницах
img_sizes = [] # размеры картинок в mm
allowed_types = ['jpg', 'jpeg', 'png'] # Разрешённые типы


def px_to_mm(px): # преобразование пикселей в милиметры
    return ceil(px * PIXEL_SIZE * SHAKAL)


def get_shakal_coef(x):
    return (PAGE_SIZE_X - OTSTUP_PX * 2) / px_to_mm(x)


def get_sizes(): # Получение размеров изоюражений из папки images
    for i in listdir('./images'):
        if i.split('.')[-1] in allowed_types:
            im = Image.open(f'./images/{i}')
            width, height = im.size
            if px_to_mm(height) > PAGE_SIZE_Y - OTSTUP_PX * 2:
                print(ceil(height * PIXEL_SIZE))
                continue
            img_sizes.append((i, height, width))
            im.close()
    img_sizes.sort(reverse=True, key=lambda x: x[1])


def make_page(): # Создание удоборимой страници
    images_size = OTSTUP_PX
    ans = []
    while images_size < PAGE_SIZE_Y - OTSTUP_PX and len(img_sizes):
        for i in range(len(img_sizes)):
            if images_size + px_to_mm(img_sizes[i][1]) <= PAGE_SIZE_Y - OTSTUP_PX:
                images_size += px_to_mm(img_sizes[i][1])
                ans.append(img_sizes.pop(i))
                break
            if i == len(img_sizes):
                return ans
            if images_size + px_to_mm(img_sizes[-1][1]) > PAGE_SIZE_Y - OTSTUP_PX:
                return ans
    return ans


def make_pages(): # Планировка страниц
    get_sizes()
    while len(img_sizes) != 0:
        page = make_page()
        if page:
            img_on_pages.append(page)


 
def run(): # Отрисовка страниц
    pdf = FPDF()
    make_pages()
    for i in img_on_pages:
        print(i)
        pdf.add_page()
        pos =  OTSTUP_PX
        for j in i:
            pdf.image(f'./images/{j[0]}', x=OTSTUP_PX, y=pos, w=px_to_mm(j[2]) * get_shakal_coef(j[2]), h=px_to_mm(j[1]) * get_shakal_coef(j[2]))
            pos = pos + px_to_mm(j[1]) * get_shakal_coef(j[2])
    pdf.output("images.pdf")


if __name__ == '__main__':
    run()