from flask import Flask, jsonify, request
from maze.coord import Coord
from maze.dir import *
from maze.maze import Maze

app = Flask(__name__)

mazeLayout = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0xf, 0, 0, 0, 0xf, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0xf, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0xf, 0, 0, 0, 0xf, 0],
    [0, 0, 0, 0, 0, 0, 0],
]


def createBlock(height, width) -> Maze:
    maze = Maze(height, width)

    for i in range(height * width):
        maze.cells[i] = 0
        coord = maze.coord(i)

        if coord.row == 0:
            maze.cells[i] |= (1 << NORTH)

        if coord.col == 0:
            maze.cells[i] |= (1 << WEST)

        if coord.row == height - 1:
            maze.cells[i] |= (1 << SOUTH)

        if coord.col == width - 1:
            maze.cells[i] |= (1 << EAST)

    return maze


def insertSubMaze(maze: Maze, submaze: Maze, xoff, yoff):
    if submaze.width > maze.width or submaze.height > maze.height:
        raise Exception("submaze is larger than maze")

    if xoff + submaze.width > maze.width or yoff + submaze.height > maze.height:
        raise Exception("submaze is out of bounds")

    for i in range(submaze.width * submaze.height):
        for d in range(4):
            if submaze.cells[i] & (1 << d) != 0:
                maze.add_wall(submaze.coord(i), d)

    return maze


def createMaze() -> Maze:
    my_maze = Maze(7, 7)

    l_eye = createBlock(1, 1)
    r_eye = createBlock(1, 1)

    print(l_eye.encode())
    print(r_eye.encode())

    my_maze = insertSubMaze(my_maze, l_eye, 1, 1)
    my_maze = insertSubMaze(my_maze, r_eye, 5, 1)

    mouth = createBlock(2, 3)

    print(mouth.encode())

    for col in range(3):
        mouth.remove_wall(Coord(0, col), NORTH)

    my_maze = insertSubMaze(my_maze, mouth, 2, 3)

    return my_maze


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = Maze(7, 7)

    for row in range(7):
        for col in range(7):
            maze.cells[maze.index(Coord(row, col))] = mazeLayout[row][col]

    print(maze.encode())

    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = f"public,max-age={365*24*60*60}"
    response.headers["Age"] = 0

    return response, 200


if __name__ == '__main__':
    maze = Maze(7, 7)

    for row in range(7):
        for col in range(7):
            maze.cells[maze.index(Coord(row, col))] = mazeLayout[row][col]

    print(maze.encode())
