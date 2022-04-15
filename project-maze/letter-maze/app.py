from flask import Flask, jsonify
from random import randint
from maze.coord import Coord
from maze.dir import DIR
from maze.mg import MazeGenerator

letterMap = ["...",
             "xxx",
             ".x.",
             ".x.",
             ".x.",
             "xxx",
             "..."]


class LetterMazeGenerator(MazeGenerator):
    def __init__(self):
        super().__init__(7, 7)

    def create(self):
        offset = randint(0, 3)

        for i in range(self.width * self.height):
            self.maze.cells[i] = 0

        for row in range(7):
            for col in range(3):
                if letterMap[row][col] == '.':
                    continue

                self.maze.set_cell(Coord(row, offset + col), 0xf)

                for i in range(4):
                    dir = DIR[i]

                    dx = dir[0]
                    dy = dir[1]

                    x = col + dx
                    y = row + dy

                    if x >= 0 and x < 3 and y >= 0 and y < 7 and letterMap[y][x] == 'x':
                        self.maze.remove_wall(Coord(row, offset + col), i)

        return self.maze


app = Flask(__name__)


@app.route('/', methods=["GET"])
def GET_maze_segment():
    maze = LetterMazeGenerator().create().encode()
    return jsonify({"geom": maze}), 200


if __name__ == '__main__':
    maze = LetterMazeGenerator().create()
    print(maze.encode())
