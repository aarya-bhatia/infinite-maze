from random import randint
from maze.maze import Maze
from maze.coord import Coord
from maze.dir import *

if __name__ == '__main__':
    maze = Maze(5, 4)
    assert(maze.coord(3) == Coord(0, 3))
    assert(not maze.is_valid(maze.coord(21)))
    assert(maze.is_valid(maze.coord(maze.size() - 1)))

    for i in range(10):
        r = randint(0, maze.size() - 1)
        assert(r == maze.index(maze.coord(r)))

    current = Coord(0, 0)
    neighbor = Coord(0, 1)

    assert(get_direction(current, neighbor) == EAST)
    assert(get_direction(neighbor, current) == WEST)

    assert((get_direction(current, neighbor) + 2) %
           4 == get_direction(neighbor, current))

    assert(not maze.has_wall(current, neighbor))
    assert(not maze.has_wall(neighbor, current))

    maze.add_wall(current, 2)

    assert(maze.has_wall(current, neighbor))
    assert(maze.has_wall(neighbor, current))

    maze.remove_wall(current, 2)

    assert(not maze.has_wall(current, neighbor))
    assert(not maze.has_wall(neighbor, current))

    print(maze.encode())
