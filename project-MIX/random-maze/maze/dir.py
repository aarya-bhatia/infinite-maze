from maze.coord import Coord


DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]

WEST = 0
SOUTH = 1
EAST = 2
NORTH = 3


def get_direction(first: Coord, second: Coord) -> int:
    dx = second.col - first.col
    dy = second.row - first.row

    for i, d in enumerate(DIR):
        if dx == d[0] and dy == d[1]:
            return i

    return -1
