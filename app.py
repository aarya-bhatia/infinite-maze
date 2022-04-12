from flask import Flask, render_template
from pymongo import MongoClient
import requests

mongo = MongoClient('localhost', 27017)
db = mongo["cs240-project-maze"]
mgdb = db['mg']

app = Flask(__name__)


def validate_grid(num_rows, num_cols, grid):
    if len(grid) != int(num_rows):
        return False
    for row in grid:
        if len(row) != int(num_cols):
            return False
        for col in row:
            if not((col >= '0' and col <= '9') or (col >= 'a' and col <= 'f') or (col >= 'A' and col <= 'F')):
                return False

    return True


def has_available_size(num_rows, num_cols, mg):
    accept_size = mg["accept_size"].split(",")

    for size in accept_size:
        dimensions = size.split(":")
        if (dimensions[0] == "*" or dimensions[0] == num_rows) and (dimensions[1] == '*' or dimensions[1] == num_cols):
            return True

    return False

# Route for "/" (frontend):


@app.route('/', methods=["GET"])
def GET_index():
    return render_template("index.html")

# Route for maze generation:


@app.route('/generateSegment', methods=["GET"])
def GET_maze_segment():
    num_rows = '7'
    num_cols = '7'

    docs = mgdb.find({"status": "available"})

    for mg in docs:
        url = mg["URL"]

        if not has_available_size(num_rows, num_cols, mg):
            continue

        try:
            response = requests.get(url)

            if response.status_code == 200:
                response = response.json()

                if "geom" in response:
                    grid = response["geom"]

                    if validate_grid(num_rows, num_cols, grid):
                        return {"geom": response["geom"]}
        except:
            mg.update_one({"_id": mg["_id"]}, {"$set": {"status", "error"}})

    return {"error": "No servers are available"}, 500
