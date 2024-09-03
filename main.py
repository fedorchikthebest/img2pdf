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


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        var = request.form.get('var')
        return render_template('get_var.html', variant=var)
    return render_template('index.html')


@app.route('/var')
def select_predmet():
    return render_template('select_class.html', classes=list(filter(lambda x: x[0] != "." and x != 'var.bin', os.listdir(f'./questions'))))


@app.route('/var/<predmet>')
def get_class(predmet):
    return render_template('select_predmet.html', predmets=list(filter(lambda x: x[0] != "." and x != 'var.bin', os.listdir(f'./questions/{predmet}'))), cl=predmet)


@app.route('/var/<predmet>/<class_>', methods=["GET", "POST"])
def generate(predmet, class_):
    if request.method == "GET":
        questions = []
        for i in os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}'):
            if i != '.DS_Store':
                questions.append((i, len(os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}'))))
                questions.sort()
        return render_template("select_questions.html", questions=questions)
    zadanija = []
    ansvers = []
    variant_id = 0
    try:
        with open(f'{os.getcwd()}/questions/var.bin', 'rb') as f:
            variant_id = int.from_bytes(f.read(), "big") + 1
        with open(f'{os.getcwd()}/questions/var.bin', 'wb') as f:
            f.write(variant_id.to_bytes(8, "big"))
    except FileNotFoundError:
        with open(f'{os.getcwd()}/questions/var.bin', 'wb') as f:
            f.write(variant_id.to_bytes(8, "big"))
    cnt = 0
    for i in request.form.keys():
        if i[0] != '.':
            a = fshuffle(os.listdir(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}'))[:int(request.form.get(i))]
            for j in a:
                if j[0] != '.':
                    zadanija.append(f'{os.getcwd()}/questions/{predmet}/{class_}/{i}/{j}')

    ansvers = img2pdf(f'{os.getcwd()}/static/variants/pdfs/{variant_id}', zadanija)
    for i in range(len(ansvers)):
        ansvers[i] = f'{i + 1}) {ansvers[i][:ansvers[i].rfind(".")].capitalize()}'
    with open(f'{os.getcwd()}/static/variants/answers/{variant_id}.txt', 'w') as f:
        f.write(f'Вариант № {variant_id}' + '\n')
        f.write('\n'.join(list(map(lambda x: x.split('_')[0], ansvers))))
    return redirect(f'/get_var/{variant_id}')


@app.route('/get_var/<variant>')
def get_var(variant):
    return render_template('get_var.html', variant=variant)


@app.route('/select_var')
def select_var():
    return render_template('select_var.html', variants=[i[:-4] for i in os.listdir('./static/variants/pdfs') if i[0] != '.'])


app.run()
