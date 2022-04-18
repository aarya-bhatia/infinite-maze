from datetime import datetime
import os
from random import randint
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, render_template_string, request, session
from pymongo import MongoClient
import util
import requests
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
import re

load_dotenv()

servers = []

EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

try:
    mongo = MongoClient('localhost', 27017)
    db = mongo["cs240-project-maze"]
except:
    print("Could not connect to the database!")
    exit(1)


def init():
    if db.servers.count_documents({}) == 0:
        server0 = {
            "URL": "http://localhost:24001",
            "description": "Letter maze generator",
            "status": "available",
            "owner_name": "Aarya",
            "owner_email": "aarya.bhatia1678@gmail.com",
            "accept_size": "*:*"
        }

        inserted = db.servers.insert_one(server0)

        if inserted:
            print("Served added: ", str(inserted.inserted_id))
    else:
        print("Server :24001 exists")


init()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", data={"logged_in": session["logged_in"]})
    else:
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "Please fill in all fields...", 400

        # query the db for a user with this username
        found = db.users.find_one({"username": username})

        # If not found, query the db for a user with email=<username>:
        if not found:
            found = db.users.find_one({"email": username})

            if not found:
                return "Account not found", 400

        # compare the passwords if user found
        if util.hash(password) == found["password"]:
            # save session data
            session['user_id'] = str(found["_id"])
            session['username'] = str(found["username"])
            session['logged_in'] = True
            return f"Account found: {found['username']}", 200
        else:
            return "Passwords do not match! Please try again", 400


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", data={"logged_in": session["logged_in"]})
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # some validation

        if not username or not email or not password:
            return "Please fill in all fields to register...", 400

        if len(password) < 3:
            return "Password too short! Please use a password longer than 3 characters.", 400

        # regex validation

        if not USERNAME_REGEX.match(username):
            return "Please enter a username that contain alphanumeric or underscore as the only characters.", 400

        if not EMAIL_REGEX.match(email):
            return "Please enter a valid email address!", 400

        # username should be unique so check for any duplicate account
        found = db.users.find_one({"username": username})
        if found:
            return "This username is taken! Please try using a different username...", 400

        # Create new account

        new_user = db.users.insert_one({
            "username": username,
            "email": email,
            "password": util.hash(password)
        })

        # save session data

        session["user_id"] = str(new_user.inserted_id)
        session["username"] = username
        session["logged_in"] = True

        # return to homepage

        return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    # delete session data
    session.clear()
    session['logged_in'] = False
    # return to index
    return redirect('/')


@app.route('/server/edit/<server_id>', methods=["GET"])
def EditServer(server_id):
    server = db.servers.find_one({"_id": ObjectId(server_id)})
    if not server:
        return "Server not found", 400

    # print(dumps(server))
    print(server)

    return render_template('server-form.html', data={
        "title": "Edit Server Form",
        "logged_in": session["logged_in"],
        "server": server
    })


@app.route('/server/delete/<server_id>', methods=["GET"])
def DeleteServer(server_id):
    if db.servers.delete_one({"_id": ObjectId(server_id)}):
        return redirect('/servers')


@app.route('/server-registration', methods=["GET", "POST"])
def RegisterServer():
    if request.method == "GET":
        return render_template('server-form.html',
                               data={"title": "Register Server Form",
                                     "logged_in": session["logged_in"], "server": {}})
    else:
        # url, description, status, owner_name, owner_email, accept_size
        id = request.form['_id']
        url = request.form['URL']
        description = request.form['description']
        status = request.form['status'] or 'available'
        owner_name = request.form['owner_name']
        owner_email = request.form['owner_email']
        accept_size = request.form['accept_size'] or '*:*'

        if not url:
            return "URL cannot be empty...", 400

        if id:
            # UPDATE EXISTING SERVER
            server = db.servers.update_one(
                {
                    "_id": ObjectId(id)
                },
                {
                    "$set": {
                        "date_modified": datetime.now(),
                        "URL": url,
                        "description": description,
                        "status": status,
                        "owner_name": owner_name,
                        "owner_email": owner_email,
                        "accept_size": accept_size
                    }
                })

            if not server:
                return "Error while updating server!", 400
        else:
            # CREATE NEW SERVER
            now = datetime.now()

            server = db.servers.insert_one({
                "date_created": now,
                "date_modified": now,
                "URL": url,
                "description": description,
                "status": status,
                "owner_name": owner_name,
                "owner_email": owner_email,
                "accept_size": accept_size
            })

            if not server:
                return "Error while creating server!", 400

        return redirect('/servers')


@ app.route('/servers', methods=['GET'])
def FindServers():
    server_list = db.servers.find()
    if server_list:
        server_list = list(server_list)
        return render_template('servers.html', data={"logged_in": session["logged_in"], "servers": server_list})

    return "Cannot find servers", 500


@ app.route('/', methods=["GET"])
def GET_index():
    print(session)
    return render_template("index.html",  data={"logged_in": session["logged_in"]})


@ app.route('/generateSegment', methods=["GET"])
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
                                  "$set": {"status": "error"}})

    return {"error": "No servers are available"}, 500
