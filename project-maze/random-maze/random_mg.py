from maze.coord import Coord
from maze.dset import DSet
from maze.maze import Maze
from maze.dir import dir_vec_arr, EAST, NORTH, SOUTH, WEST, get_direction
from maze.mg import MazeGenerator
from random import randint, shuffle


class RandomMazeGenerator(MazeGenerator):

    def __init__(self, num_rows=7, num_cols=7):
        super().__init__(num_rows, num_cols)

    def create(self) -> Maze:
        dset = DSet(self.width * self.height)

        for index in range(self.maze.size()):
            self.maze.cells[index] = 0xf

        while dset.size(0) < self.maze.size():

            currentIndex = randint(0, self.maze.size() - 1)
            currentCoord = self.maze.coord(currentIndex)

            dirs = [i for i in dir_vec_arr]
            shuffle(dirs)

            for dir in dirs:
                dx = dir[0]
                dy = dir[1]

                neighborCoord = Coord(
                    currentCoord.row + dy, currentCoord.col + dx)

                if not self.maze.is_valid(neighborCoord):
                    continue

                neighborIndex = self.maze.index(neighborCoord)

                if dset.find(currentIndex) == dset.find(neighborIndex):
                    continue

                dset.union(currentIndex, neighborIndex)

                dir = get_direction(currentCoord, neighborCoord)
                self.maze.remove_wall(currentCoord, dir)

                break

        # create exits

        randrow1 = randint(0, self.maze.height - 1)
        randrow2 = randint(0, self.maze.height - 1)
        randcol1 = randint(0, self.maze.width - 1)
        randcol2 = randint(0, self.maze.width - 1)

        index = self.maze.index(Coord(0, randcol1))
        self.maze.cells[index] &= ~(1 << NORTH)

        index = self.maze.index(Coord(self.maze.height-1, randcol2))
        self.maze.cells[index] &= ~(1 << SOUTH)

        index = self.maze.index(Coord(randrow1, self.maze.width - 1))
        self.maze.cells[index] &= ~(1 << EAST)

        index = self.maze.index(Coord(randrow2, 0))
        self.maze.cells[index] &= ~(1 << WEST)

        return self.maze


if __name__ == '__main__':
    maze = RandomMazeGenerator(7, 7).create()
    print(maze.encode())
