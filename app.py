from flask import Flask, render_template, request, abort, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from catalog_data import PRODUCTS, DISEASES
from reviews_data import REVIEWS

app = Flask(__name__)

app.secret_key = "miracle-hangover-secret-key"

USERS = {}


def show_catalog(disease, errors):
    products = PRODUCTS
    selected = None

    for d in DISEASES:
        if d["slug"] == disease:
            selected = d

    if selected is not None:
        products = []
        for p in PRODUCTS:
            if disease in p["diseases"]:
                products.append(p)
    return render_template("catalog.html", products=products, selected=selected, errors=errors)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/catalog")
def catalog():
    disease = request.args.get("disease", "")
    errors = []
    return show_catalog(disease, errors)


@app.route("/product/<int:product_id>")
def product(product_id):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return render_template("product.html", product=p, diseases=DISEASES)

    abort(404)

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", reviews=REVIEWS)


@app.route("/buy", methods=["POST"])
def buy():
    disease = request.form.get("disease", "")
    chosen = []
    errors = []
    total = 0

    for p in PRODUCTS:
        qty_text = request.form.get("qty_" + str(p["id"]), "0")

        try:
            qty = int(qty_text)
        except ValueError:
            qty = -1

        if qty < 0 or qty > p["stock"]:
            errors.append("«" + p["name"] + "»: количество должно быть от 0 до " + str(p["stock"]) + ".")
        elif qty > 0:
            cost = p["price"] * qty
            chosen.append({"name": p["name"], "price": p["price"], "qty": qty, "cost": cost})
            total = total + cost

    if len(chosen) == 0 and len(errors) == 0:
        errors.append("Укажите количество хотя бы для одного товара.")

    if len(errors) > 0:
        return show_catalog(disease, errors)

    return render_template("order.html", chosen=chosen, total=total)


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "" or password == "":
            errors.append("Введите логин и пароль.")
        elif username not in USERS or not check_password_hash(USERS[username], password):
            errors.append("Неверный логин или пароль.")

        if len(errors) == 0:
            session["user"] = username
            return redirect("/catalog")

    return render_template("login.html", errors=errors, username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        USERS[username] = generate_password_hash(password)
        session["user"] = username
        return redirect("/catalog")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)