import datetime
import math
import os
import re
import string
import time
import urllib.parse
import random

from flask import Flask, render_template, request, jsonify, make_response, redirect
import firebase_admin

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import jwt

# Setup/Config
cred = credentials.Certificate('project.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://asianbot-96876-default-rtdb.firebaseio.com'
})
root = db.reference('/')
db_password = root.child("passwords")
db_games = root.child("games")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


def decode(token):
    try:
        decoded = jwt.decode(token, os.getenv("JWTSecret"), "HS256")
    except:
        return None
    return decoded

def generate_id():
    "".join(str(random.randint(1, 9)) for _ in range(5))


@app.route('/')
def page_home():
    if "token" not in request.cookies:
        return render_template("homepage.html", title="Homepage", data={})
    token = decode(request.cookies["token"])
    if not token:
        return render_template("homepage.html", title="Homepage", data={})
    else:
        return render_template("homepage.html", title="Homepage", data=token)

@app.route('/student')
def page_student():
    if "token" not in request.cookies:
        return render_template("student.html", title="Choose Class", data={})
    token = decode(request.cookies["token"])
    if not token:
        return redirect("/?error=login")

    classes = root.child("users").child(token['uname']).child("classes").get()
    res = {}

    for item in classes:
        res[item] = root.child("classes").child(item).get()
        res[item]["teacher_realname"] = root.child("users").child(res[item]['teacher']).child("name").get()

    return render_template("student.html", title="Choose Class", data=token, classes=res)

@app.route('/api/login/asdev', methods=["POST"])
def api_login_asdev():
    token = jwt.encode({
        "id": str(root.child("users").child("achen10").child("id").get()),
        "uname": "achen10",
        "name": "Andrew Chen",
        "iat": math.floor(datetime.datetime.timestamp(datetime.datetime.now())), # Now
        "exp": math.floor(datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(days=30)))
    }, key=os.getenv("JWTSecret"), algorithm="HS256")

    res = make_response(token, 200)
    res.set_cookie("token", token)

    return res


@app.route('/class/<path:id>', defaults={"page": "info", "args": None})
@app.route('/class/<path:id>/<path:page>', defaults={"args": None})
@app.route('/class/<path:id>/<path:page>/<path:args>')
def class_general(id, page, args):
    if "token" not in request.cookies:
        return render_template("student.html", title="Homepage", data={})
    token = decode(request.cookies["token"])
    if not token:
        return redirect("/?error=login")

    data = root.child("classes").child(str(id)).get()
    data["teacher_realname"] = root.child("users").child(data['teacher']).child("name").get()

    kwargs = {
        "data": token,
        "title": data['name'],
        "page": page,
        "classdata": data,
        "classid": id,
    }

    if not page or page not in ["work", "grades", "infractions"]:
        page = "info"

    if page == "work":
        if args:
            kwargs["page"] = "work_assignment"
            kwargs["work_data"] = root.child("assignments").child(args).get()
        else:
            kwargs["work"] = {}
            if "work" in data:
                for work in data["work"]:
                    kwargs["work"][work] = root.child("assignments").child(work).get()

    return render_template("class.html", **kwargs)