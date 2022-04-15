import sys
from flask import Flask, jsonify
from random_mg import RandomMazeGenerator

app = Flask(__name__)

sys.path.append('../maze/')


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = RandomMazeGenerator(7, 7).create().encode()
    return jsonify({"geom": maze}), 200
