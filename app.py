import os
from random import randint
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, render_template_string, request, session
from pymongo import MongoClient
import util
import requests
from bson.objectid import ObjectId
from bson.json_util import loads, dumps

load_dotenv()

servers = []

try:
    mongo = MongoClient('localhost', 27017)
    db = mongo["cs240-project-maze"]
except:
    print("Could not connect to the database!")
    exit(1)

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        data = {
            "session": loads(session)
        }
        return render_template("login.html", data=data)
    else:
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "Please fill in all fields...", 400

        found = db.users.find_one({"username": username})

        if found:
            user = dumps(found)
            print(user)
            session['user_id'] = str(found["_id"])
            session['username'] = found["username"]
            session['logged_in'] = True
            return f"Account found: {found['username']}", 200
        else:
            return "Account not found", 400


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        data = {
            "session": session
        }
        return render_template("register.html", data=data)
    else:
        return "Todo", 200


@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    session.pop('user')
    return redirect('/')


@app.route('/', methods=["GET"])
def GET_index():
    data = {
        "session": session
    }
    return render_template("index.html", data=data)


@app.route('/generateSegment', methods=["GET"])
def GET_maze_segment():
    """Route for maze generation"""
    num_rows = '7'
    num_cols = '7'

    if not servers:
        docs = db.servers.find({"status": "available"})

        if docs:
            for server in docs:
                servers.append(server)

    while len(servers) > 0:
        r = randint(0, len(servers)-1)
        server = servers[r]
        servers.remove(server)

        url = server["URL"]

        if not util.has_available_size(num_rows, num_cols, server):
            continue

        try:
            response = requests.get(url)

            if response.status_code == 200:
                response = response.json()

                if "geom" in response:
                    grid = response["geom"]

                    if util.validate_grid(num_rows, num_cols, grid):
                        return {"geom": response["geom"]}
        except:
            db.servers.update_one({"_id": ObjectId(server["_id"])}, {
                                  "$set": {"status", "error"}})

    return {"error": "No servers are available"}, 500
