from datetime import datetime, timezone
import os
from random import randint
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, jsonify
from pymongo import MongoClient
import util
import requests
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
import re

load_dotenv()

servers = []

active_users = []

EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")
HTTP_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

serverCache = {}
CACHE_HIT_COUNT = 0

serverFrequency = {}

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


def get_servers():
    if servers:
        return

    docs = db.servers.find({"status": "available"})

    if docs:
        for server in docs:
            servers.append(server)


@ app.route('/generateSegment', methods=["GET"])
def GET_maze_segment():
    """Route for maze generation"""

    global servers
    global serverCache
    global HTTP_DATE_FORMAT
    global CACHE_HIT_COUNT
    global serverFrequency

    num_rows = '7'
    num_cols = '7'

    print("Server Cache => " + str(serverCache))

    # If server list is empty, it will be filled with available servers that are fetched from the database
    if not servers:
        get_servers()

    # Get maze coordinates

    x = request.args.get('x') or 0
    y = request.args.get('y') or 0

    maze = db.mazes.find_one({"x": x, "y": y})

    if maze:
        return jsonify({"geom": maze["geom"]}), 200

    # Generate Maze

    # Pick MG: randomly choose servers from the list till a valid one is found
    while len(servers) > 0:
        r = randint(0, len(servers)-1)
        server = servers[r]
        servers.remove(server)

        url = server["URL"]

        if not util.has_available_size(num_rows, num_cols, server):
            continue

        serverId = str(server["_id"])

        # If the cache exists for current server, do not request to it again
        if serverId in serverCache:
            cache = serverCache[serverId]
            cacheDate = cache['date']

            now = datetime.now(tz=timezone.utc)

            timeElapsed = now - cacheDate
            timeElapsedSec = int(timeElapsed.total_seconds())

            print("Time Elapsed: " + str(timeElapsed))

            cache['date'] = now
            cache['age'] = cache.get('age', 0) + timeElapsedSec

            if cache['age'] <= cache['max-age']:
                print("HIT")
                print(cache)

                CACHE_HIT_COUNT += 1

                serverFrequency[serverId] = serverFrequency.get(
                    serverId, 0) + 1

                return jsonify({"geom": cache['geom']}), 200
            else:
                # Cache has expired
                print("Cache expired")
                del serverCache[serverId]

        try:
            print("Cache not found or expired")
            # Make request to Maze Generator Server
            response = requests.get(url)

            if response.status_code == 200:
                content = response.json()

                if "geom" in content:
                    geom = content["geom"]

                    if util.validate_grid(num_rows, num_cols, geom):
                        print(response.headers)

                        # check if maze is static
                        if "Cache-Control" not in response.headers or response.headers["Cache-Control"] == 'no-store':
                            serverFrequency[serverId] = serverFrequency.get(
                                serverId, 0) + 1
                            print("Using dynamic maze generator: " + url)

                            db.mazes.insert_one({
                                "geom": geom,
                                "url": server["url"],
                                "server_id": server["_id"],
                                "x": x,
                                "y": y
                            })

                            return jsonify({"geom": geom}), 200

                        date = response.headers["Date"]

                        if date:
                            date = datetime.strptime(
                                date, HTTP_DATE_FORMAT).replace(tzinfo=timezone.utc)
                        else:
                            date = datetime.now(tz=timezone.utc)

                        age = response.headers["Age"]
                        cacheControl = response.headers["Cache-Control"].strip().split(
                            ",")
                        maxAge = 0

                        for keyValue in cacheControl:
                            if len(keyValue) > 0 and keyValue.split('=')[0] == 'max-age':
                                maxAge = keyValue.split('=')[1]

                        serverCache[serverId] = {
                            "date": date,
                            "max-age": int(maxAge),
                            "age": int(age),
                            "geom": geom,
                            "x": x,
                            "y": y
                        }

                        serverFrequency[serverId] = serverFrequency.get(
                            serverId, 0) + 1

                        db.mazes.insert_one({
                            "geom": geom,
                            "url": server["url"],
                            "server_id": server["_id"],
                            "x": x,
                            "y": y
                        })

                        return jsonify({"geom": geom}), 200

                    # Invalid grid format
                    else:
                        pass

                # 'geom' key not present
                else:
                    pass

            # status code != 200
            else:
                pass
        except:
            print("Error with Server: " + server["URL"])
            db.servers.update_one({"_id": ObjectId(server["_id"])}, {
                                  "$set": {"status": "error"}})

    return jsonify({"error": "No servers are available"}), 500


@app.route('/locals', methods=['GET'])
def GET_locals():
    return jsonify({"cache": serverCache, "hit_count": CACHE_HIT_COUNT, "frequency": serverFrequency}), 200


@app.route('/move', methods=['GET'])
def GET_moveUser():
    maze_id = request.args.get('maze_id')
    x = request.args.get('x')
    y = request.args.get('y')

    db.mazes.update_one({"_id": ObjectId(maze_id)}, {
                        "$push": {"steps": {"x": x, "y": y}}})

    return "", 200
