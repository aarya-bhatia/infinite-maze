from random import randint
from flask import Flask, jsonify
from custom_mg import CustomMazeGenerator

app = Flask(__name__)

letter_maps = [
    [
        'x.x.x',
        'x.x.x',
        'x.x.x',
        'x...x',
        'xx.xx',
    ],

    [
        "xxx",
        ".x.",
        "xxx",
        ".x.",
        "xxx"
    ],

    [
        "xxxx",
        ".xxx",
        "..xx",
        "...x",
    ],

    [
        "xxxx",
        "xxx.",
        "xx..",
        "x...",
    ],

    [
        'xx..xx',
        '...xx.',
        '.x....',
        'xxxx..',
        '..x...',
        'x....x'
    ]
]


@app.route('/', methods=["GET"])
def GET_maze_segment():
    letter_map = letter_maps[randint(0, len(letter_maps)-1)]

    maze = CustomMazeGenerator(
        height=7, width=7, letter_map=letter_map).create()
    print(maze.encode())

    return jsonify({"geom": maze.encode()}), 200
