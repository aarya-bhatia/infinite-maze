from datetime import datetime
from flask import Flask, render_template
import requests

mg_db = [
    {
        "id": "1",
        "url": "http://127.0.0.1:24000/",
        "last_access": None,
        "status": "available", # possible values are available, waiting, error
        "accept_size": "*:*"
    }
]

retry_time = 5*60 #seconds

app = Flask(__name__)

def is_valid_mg(mg):
    if "last_access" not in mg or mg["last_access"] is None:
        mg["last_access"] = datetime.now().isoformat()

    last_access = datetime.fromisoformat(mg["last_access"])
    status = mg["status"]

    if status == "error":
        return False

    if status == "waiting":
        delta = datetime.now() - last_access

        if delta.seconds >= retry_time:
           mg["status"] = "available"
        else:
            return False
    
    return True

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
    print(mg_db)

    num_rows = '7'
    num_cols = '7'

    for mg in mg_db:
        url = mg["url"]

        if not is_valid_mg(mg) or mg["status"] != "available":
            continue 

        if not has_available_size(num_rows, num_cols, mg):
            continue

        mg["last_access"] = datetime.now().isoformat()

        try:
            response = requests.get(url)

            if response.status_code == 200:
                response = response.json()
                
                if "geom" in response:
                    grid = response["geom"]

                    if validate_grid(num_rows, num_cols, grid):
                        return {"geom": response["geom"]}

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        mg["status"] = "waitig"
    
    # end for loop;

    # no available servers
    return {"error": "Internal server error"}, 500
