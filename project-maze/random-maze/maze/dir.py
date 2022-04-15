from maze.coord import Coord


DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]

WEST = 0
SOUTH = 1
EAST = 2
NORTH = 3


def sgn(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def get_direction(first: Coord, second: Coord) -> int:
    dx = sgn(second.col - first.col)
    dy = sgn(second.row - first.row)

    for i, d in enumerate(DIR):
        if dx == d[0] and dy == d[1]:
            return i

    return -1
