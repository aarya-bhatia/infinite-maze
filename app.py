from random import randint
from flask import Flask, render_template, request
from pymongo import MongoClient
import util
import requests
from bson.objectid import ObjectId

servers = []

try:
    mongo = MongoClient('localhost', 27017)
    db = mongo["cs240-project-maze"]
except:
    print("Could not connect to the database!")
    exit(1)

app = Flask(__name__)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html"), 200
    else:
        return "OK", 200


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html"), 200
    else:
        return "OK", 200


@app.route('/', methods=["GET"])
def GET_index():
    return render_template("index.html")


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
