from flask import Flask, jsonify
from random_mg import RandomMazeGenerator

app = Flask(__name__)


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = RandomMazeGenerator(7, 7).create().encode()
    print(maze)
    return jsonify({"geom": maze}), 200
