from flask import Flask, jsonify
from maze.coord import Coord
from maze.dir import *
from maze.maze import Maze

app = Flask(__name__)

mazeLayout = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0xf, 0, 0, 0, 0xf, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0xf, 0, 0, 0, 0xf, 0],
    [0, 0, 0, 0, 0, 0, 0],
]


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = Maze(7, 7)

    for row in range(7):
        for col in range(7):
            coord = Coord(row, col)

            if mazeLayout[row][col] == 0xf:
                maze.add_wall(coord, 0)
                maze.add_wall(coord, 1)
                maze.add_wall(coord, 2)
                maze.add_wall(coord, 3)

    response = jsonify({"geom": maze.encode()})

    response.headers["Cache-Control"] = f"public,max-age={365*24*60*60}"
    response.headers["Age"] = 0

    return response, 200
