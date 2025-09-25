from flask import Flask, render_template, request
import db

app = Flask(__name__)
db.setup()


@app.route("/")
@app.route("/<name>")
def hello(name=None):
    return render_template("hello.html", name=name, guestbook=db.get_guestbook())


@app.post("/submit")
def submit():
    name = request.form.get("name")
    text = request.form.get("text")
    db.add_post(name, text)
    return render_template("hello.html", name=None, guestbook=db.get_guestbook())
