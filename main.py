from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename
import store
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.JPG', '.PNG', '.GIF']
app.config['UPLOAD_PATH'] = './static/uploads'


@app.route('/')
def home():
    return render_template('index.html', product_records=store.produits_page_accueil(),
                           line_records=store.lignes_produits_page_accueil())


@app.route('/get-ligne')
def get_ligne():
    ligne = request.args.get('ligne', default='*', type=str)
    return render_template('details_ligne.html', state=store.ligne_detail(ligne),
                           products=store.recherche_produits_par_ligne(ligne))


@app.route('/get-produit')
def get_produit():
    produit = request.args.get('produit', default='*', type=str)
    return render_template('details_produit.html', state=store.produit_detail(produit))


@app.route("/recherche", methods=['POST'])
def recherche():
    key_word = request.form['keyword']
    page = request.args.get('page', default=1, type=int)
    if page <= 0:
        page = 1
    return render_template('recherche.html', product_records=store.recherche_produit(key_word, page), keyword=key_word,
                           page=page)


@app.route("/modifier-ligne", methods=['POST'])
def modifier_ligne():
    save_image(request.files['image'])
    return render_template('details_ligne.html', state=store.modifier_ligne(request))


@app.route("/modifier-produit", methods=['POST'])
def modifier_produit():
    save_image(request.files['image'])
    return render_template('details_produit.html', state=store.modifier_produit(request))


@app.route("/create-produit", methods=['POST'])
def create_produit():
    save_image(request.files['image'])
    return render_template('details_produit.html', state=store.create_produit(request))


@app.route("/supprimer-produit", methods=['POST'])
def supprimer_produit():
    store.supprimer_produit(request)
    return render_template('index.html', product_records=store.produits_page_accueil(),
                           line_records=store.lignes_produits_page_accueil())


@app.route("/create-ligne",methods=['POST'])
def create_ligne():
    save_image(request.files['image'])
    return render_template('details_ligne.html', state=store.create_ligne(request))


def save_image(image):
    filename = secure_filename(image.filename)
    if filename != "":
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        image.save(os.path.join(app.config['UPLOAD_PATH'], filename))


if __name__ == '__main__':
    app.run(debug=True)
