from flask import Flask, jsonify
from letter_mg import LetterMazeGenerator

app = Flask(__name__)


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = LetterMazeGenerator().create().encode()
    print(maze)
    return jsonify({"geom": maze}), 200
