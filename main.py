from flask import Flask, render_template, request, redirect, abort, flash
import os
from utils.img2pdf import img2pdf
from uuid import uuid4
from random import randrange

app = Flask(__name__)


def fshuffle(arr:list) -> list:
    for i in range(len(arr) // 2):
        r = randrange(0, len(arr))
        arr[i], arr[r] = arr[r], arr[i]
    return arr


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/var')
def select_predmet():
    return render_template('select_class.html', classes=list(filter(lambda x: x != ".gitkeep", os.listdir(f'./questions'))))


@app.route('/var/<predmet>')
def get_class(predmet):
    return render_template('select_predmet.html', predmets=os.listdir(f'./questions/{predmet}'), cl=predmet)


@app.route('/var/<predmet>/<class_>', methods=["GET", "POST"])
def generate(predmet, class_):
    if request.method == "GET":
        questions = []
        for i in os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}'):
            questions.append((i, len(os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}'))))
        return render_template("select_questions.html", questions=questions)
    zadanija = []
    ansvers = []
    variant_id = 0
    try:
        with open(f'{os.getcwd()}/questions/var.bin', 'rb') as f:
            variant_id = int.from_bytes(f.read()) + 1
        with open(f'{os.getcwd()}/questions/var.bin', 'wb') as f:
            f.write(variant_id.to_bytes(8))
    except FileNotFoundError:
        with open(f'{os.getcwd()}/questions/var.bin', 'wb') as f:
            f.write(variant_id.to_bytes(8))
    for i in request.form.keys():
        if i != '.DS_Storage':
            a = fshuffle(os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}'))[:int(request.form.get(i))]
            for j in a:
                zadanija.append(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}/{j}')
        ansvers += a
    with open(f'{os.getcwd()}/static/variants/answers/{variant_id}.txt', 'w') as f:
        f.write('\n'.join(list(map(lambda x: x.split('_')[0], ansvers))))
    img2pdf(f'{os.getcwd()}/static/variants/pdfs/{variant_id}', zadanija)
    return redirect(f'/get_var/{variant_id}')


@app.route('/get_var/<variant>')
def get_var(variant):
    return render_template('get_var.html', variant=variant)


@app.route('/select_var')
def select_var():
    return render_template('select_var.html', variants=[i[:-4] for i in os.listdir('./static/variants/pdfs')])


app.run()
