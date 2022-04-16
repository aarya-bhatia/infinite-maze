from random import randint
from maze.coord import Coord
from maze.dir import dir_vec_arr
from maze.mg import MazeGenerator

letterMap = ["...",
             "xxx",
             ".x.",
             ".x.",
             ".x.",
             "xxx",
             "..."]


class LetterMazeGenerator(MazeGenerator):
    def __init__(self, offset=None):
        super().__init__(7, 7)

        if offset:
            self.offset = offset
        else:
            self.offset = randint(0, 3)

    def create(self):
        for i in range(self.width * self.height):
            self.maze.cells[i] = 0

        for row in range(7):
            for col in range(3):
                if letterMap[row][col] == '.':
                    continue

                current = Coord(row, self.offset + col)

                for i in range(4):
                    dx, dy = dir_vec_arr[i]

                    x = col + dx
                    y = row + dy

                    if x < 0 or x >= 3 or y < 0 or y >= 7:
                        continue
                    elif letterMap[y][x] == 'x':
                        self.maze.remove_wall(current, i)
                    else:
                        self.maze.add_wall(current, i)

        return self.maze


if __name__ == '__main__':
    maze = LetterMazeGenerator(0).create()
    print(maze.encode())
