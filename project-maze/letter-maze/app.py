import sys
from flask import Flask, jsonify
from random import randint

sys.path.append('../maze/')

from maze import Coord
from maze import DIR
from maze import MazeGenerator

letterMap = ["...",
             "xxx",
             ".x.",
             ".x.",
             ".x.",
             "xxx",
             "..."]


class LetterMazeGenerator(MazeGenerator):
    def create(self):
        w = len(letterMap[0])
        offset = randint(0, 4)

        for row in self.height:
            for col in self.width:
                if col < offset or col > offset + w or letterMap[row][col] == '.':
                    self.maze.set_cell(Coord(row, col), 0x0)
                else:
                    self.maze.set_cell(Coord(row, col), 0xf)

                    for index, dir in enumerate(DIR):
                        dx = dir[0]
                        dy = dir[1]

                        map_x = col - offset + dx
                        map_y = row + dy

                        if letterMap[map_y][map_x] == 'x':
                            # remove wall in this dir
                            self.maze.set_cell(Coord(row, col), self.maze.get_cell(
                                Coord(row, col)) & ~(1 << index))

        return self.maze


app = Flask(__name__)

sys.path.append('../maze/')


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = LetterMazeGenerator(7, 7).create().encode()
    return jsonify({"geom": maze}), 200
