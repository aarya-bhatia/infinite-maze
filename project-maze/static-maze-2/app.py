from flask import Flask, jsonify, request
from maze.maze import Maze

app = Flask(__name__)


@app.route('/', methods=["GET"])
def GET_maze_segment():
    height = request.args.get('height') or 7
    width = request.args.get('width') or 7
    maze = Maze(height=height, width=width)
    return jsonify({"geom": maze.encode()}), 200
