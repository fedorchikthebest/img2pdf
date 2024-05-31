from flask import Flask, render_template, request, redirect, abort, flash
import os
from utils.img2pdf import img2pdf
from uuid import uuid4
from random import choice

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/var')
def select_class():
    return render_template('select_class.html', classes=os.listdir(f'./questions'))


@app.route('/var/<class_>')
def get_class(class_):
    return render_template('select_predmet.html', predmets=os.listdir(f'./questions/{class_}'), cl=class_)


@app.route('/var/<class_>/<predmet>')
def generate(class_, predmet):
    zadanija = []
    ansvers = []
    variant_id = uuid4()
    for i in os.listdir(f'./questions/{class_}/{predmet}'):
        if i != '.DS_Storage':
            a = choice(os.listdir(f'./questions/{class_}/{predmet}/{i}'))
            zadanija.append(f'./questions/{class_}/{predmet}/{i}/{a}')
        ansvers.append(a)
    with open(f'./static/variants/answers/{variant_id}.txt', 'w') as f:
        f.write('\n'.join(list(map(lambda x: x.split('_')[0], ansvers))))
    img2pdf(f'./static/variants/pdfs/{variant_id}', zadanija)
    return redirect(f'/get_var/{variant_id}')


@app.route('/get_var/<variant>')
def get_var(variant):
    return render_template('get_var.html', variant=variant)


@app.route('/select_var')
def select_var():
    return render_template('select_var.html', variants=[i[:-4] for i in os.listdir('./static/variants/pdfs')])


app.run()