import datetime
import math
import os
import re
import string
import time
import urllib.parse
import random
import requests

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
        return redirect("/?error=login")
    token = decode(request.cookies["token"])
    if not token:
        return redirect("/?error=login")

    if token["teach"]:
        return redirect("/teacher")

    classes = root.child("users").child(token['uname']).child("classes").get()
    res = {}

    for item in classes:
        res[item] = root.child("classes").child(item).get()
        res[item]["teacher_realname"] = root.child("users").child(res[item]['teacher']).child("name").get()

    return render_template("student.html", title="Choose Class", data=token, classes=res)


@app.route('/teacher')
def page_teacher():
    if "token" not in request.cookies:
        return redirect("/?error=login")
    token = decode(request.cookies["token"])
    if not token:
        return redirect("/?error=login")
    if not token["teach"]:
        return redirect("/student")

    classes = root.child("users").child(token['uname']).child("classes").get()
    res = {}

    for item in classes:
        res[item] = root.child("classes").child(item).get()
        res[item]["teacher_realname"] = root.child("users").child(res[item]['teacher']).child("name").get()

    return render_template("teacher.html", title="Choose Class", data=token, classes=res)


@app.route('/api/login/asdev', methods=["POST"])
def api_login_asdev():
    token = jwt.encode({
        "id": str(root.child("users").child("achen10").child("id").get()),
        "uname": "achen10",
        "name": str(root.child("users").child("achen10").child("name").get()),
        "iat": math.floor(datetime.datetime.timestamp(datetime.datetime.now())), # Now
        "exp": math.floor(datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(days=30))),
        "teach": False
    }, key=os.getenv("JWTSecret"), algorithm="HS256")

    res = make_response(token, 200)
    res.set_cookie("token", token)

    return res


@app.route('/api/login/asgrad', methods=["POST"])
def api_login_asgrad():
    token = jwt.encode({
        "id": str(root.child("users").child("mrjgrad").child("id").get()),
        "uname": "mrjgrad",
        "name": str(root.child("users").child("mrjgrad").child("name").get()),
        "iat": math.floor(datetime.datetime.timestamp(datetime.datetime.now())), # Now
        "exp": math.floor(datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(days=30))),
        "teach": True
    }, key=os.getenv("JWTSecret"), algorithm="HS256")

    res = make_response(token, 200)
    res.set_cookie("token", token)

    return res


@app.route('/class/<path:id>', defaults={"page": "info", "args": None})
@app.route('/class/<path:id>/<path:page>', defaults={"args": None})
@app.route('/class/<path:id>/<path:page>/<path:args>')
def class_general(id, page, args):
    if "token" not in request.cookies:
        return redirect("/?error=login")
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
    elif page == "infractions":
        if token["teach"]:
            kwargs["infractions_students"] = {}
            for student in kwargs["classdata"]["students"]:
                s = root.child("users").child(str(student))
                kwargs["infractions_students"][s.child("name").get() or student] = s.child("violations").get() or []
        else:
            kwargs["infractions"] = root.child("users").child(str(token["uname"])).child("violations").get() or []
    elif page == "grades":
        kwargs["work"] = {}
        if "work" in data:
            for work in data["work"]:
                kwargs["work"][work] = root.child("assignments").child(work).get()
        if token["teach"]:
            kwargs["students"] = []
            for student in kwargs["classdata"]["students"]:
                kwargs["students"].append([student, root.child("users").child(str(student)).child("name").get()])
        kwargs["grades"] = root.child("classes").child(str(id)).child("grades").get()

    return render_template("class.html", **kwargs)


@app.route("/api/violations/new", methods=["POST"])
def new_violation():
    data = request.get_json()
    violation_type = data.get("type")
    auth = data.get("jwt")
    timestamp = math.floor(datetime.datetime.timestamp(datetime.datetime.now()))

    decoded = decode(auth)

    if not decoded:
        return "Invalid authentication token", 401

    violations = root.child("users").child(decoded["uname"]).child("violations").get() or []
    violations.append({"type": violation_type, "time": timestamp})

    root.child("users").child(decoded["uname"]).child("violations").set(violations)

    name = root.child("users").child(decoded["uname"]).child("name").get()
    requests.post("https://postmail.invotes.com/send", json={
        "access_token": "b27p549060fgy42skc4d5uf2",
        "text": f'Dear parent of {name}:\nYour child {name} was not doing their homework today. They instead {violation_type}. Please take immediate action.\n\nSincerely,\n\tAsianBot Child Management Team',
        "subject": "Your child is not doing their homework"
    },  headers={'Content-Type': 'application/json'})

    return "Success", 200
