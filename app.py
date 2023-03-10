import datetime
import math
import os
import re
import string
import time
import urllib.parse

from flask import Flask, render_template, request, jsonify, make_response, redirect
import firebase_admin

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import jwt

# Setup/Config
cred = credentials.Certificate('project.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://logle-e6f2a-default-rtdb.firebaseio.com/'
})
root = db.reference('/')
db_password = root.child("passwords")
db_games = root.child("games")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route('/')
def page_home():
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWTSECRET"), "HS256")
    except:
        return render_template("homepage.html", title="Homepage", uname="")
    else:
        return render_template("homepage.html", title="Homepage", uname=decoded['uname'])

