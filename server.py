from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import io
import db
import json
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET"]

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


db.setup()


#### AUTH STUFF ####


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()

    session["user"] = token

    return redirect(url_for("hello"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("hello", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
@app.route("/<name>")
def hello(name=None):
    if name is not None and name != "":
        print(name)
        session["name"] = name
    return render_template(
        "hello.html", name=session.get("name"), guestbook=db.get_guestbook()
    )


@app.post("/submit")
def submit():
    name = request.form.get("name")
    text = request.form.get("text")
    print(request.files)
    print(len(request.files))
    file = request.files["image"]
    print(file.filename)

    with db.get_db_cursor(True) as cur:
        cur.execute(
            "insert into images (contents) values (%s) returning id;", (file.read(),)
        )
        print(next(cur))

    db.add_post(name, text)
    return render_template("hello.html", name=None, guestbook=db.get_guestbook())


@app.route("/images/<int:image_id>")
def get_image(image_id):
    # (get a cursor "cur")
    with db.get_db_cursor(True) as cur:
        cur.execute("SELECT * FROM images where id=%s", (image_id,))
        image_row = cur.fetchone()  # just another way to interact with cursors

        # in memory pyhton IO stream
        stream = io.BytesIO(image_row["contents"])

        # use special "send_file" function
        return send_file(stream, download_name="image")
