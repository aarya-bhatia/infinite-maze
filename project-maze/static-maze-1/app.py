from flask import Flask, jsonify, request
from maze.dir import *
from maze.coord import *
from maze.maze import *

app = Flask(__name__)

# pattern = [
#     '.xxxxxx',
#     '..xxxxx',
#     '...xxxx',
#     'x...xxx',
#     'xx...xx',
#     'xxx...x',
#     'xxxx...',
# ]


def get_maze():
    height = 7
    width = 7
    maze = Maze(height=height, width=width)

    pattern = []

    for y in range(7):
        row = ''
        for x in range(7):
            if abs(y-x) < 2:
                row += '.'
            else:
                row += 'x'
        print(row)
        pattern.append(row)

    for row in range(7):
        for col in range(7):
            if pattern[row][col] == 'x':
                continue

            for i in range(4):
                dx, dy = dir_vec_arr[i]

                x = col + dx
                y = row + dy

                if not maze.is_valid(Coord(y, x)):
                    continue

                if pattern[y][x] == 'x':
                    maze.add_wall(Coord(row, col), i)

    return maze


@app.route('/', methods=["GET"])
def GET_maze_segment():

    return jsonify({"geom": get_maze().encode()}), 200
