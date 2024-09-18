from flask import Flask, render_template, request, redirect, abort, flash, send_file, make_response
import os
import utils.crypto as crypto
from utils.img2pdf import img2pdf
from uuid import uuid4
from random import randrange, choice
import json
import string

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
        if "F-Signature" in list(request.headers.keys()) and str(crypto.b32decrypt(request.headers["F-DATA-PROTECT"])).rstrip("\0") == request.headers["F-S-DATA"]:
            return crypto.b32encode(crypto.b32verify(request.headers["F-SIGNATURE"], request.headers["F-S-DATA"]))
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

    for i in request.form.keys():
        if i[0] != '.':
            a = fshuffle(os.listdir(f'./questions/{predmet}/{class_}/{i}'))[:int(request.form.get(i))]
            for j in a:
                if j[0] != '.':
                    zadanija.append(f'./questions/{predmet}/{class_}/{i}/{j}')

    ansvers = img2pdf(f'{os.getcwd()}/static/variants/pdfs/{variant_id}', zadanija)
    with open(f"./variants_map/{variant_id}", "w") as f:
        f.write("\n".join(zadanija))
    for i in range(len(ansvers)):
        ansvers[i] = f'{i + 1}) {ansvers[i].split("_")[0][:ansvers[i].rfind(".")].capitalize()}'
    with open(f'{os.getcwd()}/static/variants/answers/{variant_id}.txt', 'w') as f:
        f.write(f'Вариант № {variant_id}' + '\n')
        f.write('\n'.join(list(map(lambda x: x.split('_')[0], ansvers))))
    return redirect(f'/get_var/{variant_id}')


@app.route('/get_var/<variant>')
def get_var(variant):
    return render_template('get_var.html', variant=variant, e_var=crypto.b32crypt(str(variant)).decode("utf-8"))


@app.route('/test/<variant>', methods=["GET", "POST"])
def gen_test(variant):
    result = []
    current_count = 0
    variant = int(crypto.b32decrypt(variant).rstrip("\0"))
    if request.method == "POST":
        if os.path.exists(f"./user_answers/{request.form.get('name')}_{variant}"):
            return abort(404)
        for quest, ans in request.form.items():
            if quest == "name":
                continue
            rans = crypto.b32decrypt(quest).rstrip("\0")
            rans = os.path.split(rans)[-1].lower()
            rans = rans.split("_")[0]
            rans = rans[:rans.rfind(".")]
            result.append([rans, ans])
            if rans == ans.lower():
                current_count += 1
        result.append(current_count)
        with open(f"./user_answers/{request.form.get('name')}_{variant}", "w") as f:
            json.dump(result, f, ensure_ascii=False)
    with open(f"./variants_map/{variant}") as f:
        questions = f.read().split("\n")
        print(crypto.b32crypt(questions[0]))
    responce = make_response(render_template("test.html", questions=list(map(lambda x: crypto.b32crypt(x).decode("utf-8"), questions))))
    s_str = ''.join([choice(string.ascii_uppercase) for i in range(64)])
    responce.headers["F-S-DATA"] = s_str
    responce.headers["F-DATA-PROTECT"] = crypto.b32crypt(s_str).decode("utf-8")
    return responce

@app.route('/select_var')
def select_var():
    return render_template('select_var.html', variants=[i[:-4] for i in os.listdir('./static/variants/pdfs') if i[0] != '.'])


@app.route("/api/get_question/<question>")
def get_questions(question):
    f = str(crypto.b32decrypt(question))
    print(f)
    if os.path.exists(f):
        return send_file(f)
    else:
        return abort(404)


app.run()
