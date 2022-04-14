from coord import Coord
from dir import DIR, get_direction


class Maze:
    def __init__(self, height, width) -> None:
        self.height = height
        self.width = width
        self.cells = [0] * (height * width)

    def set_cell(self, coord: Coord, value: int) -> None:
        if not self.is_valid_coord(coord):
            return

        self.cells[self.get_index(coord)] = value

    def get_cell(self, coord: Coord) -> int:
        if not self.is_valid_coord(coord):
            raise Exception("Invalid coord")

        return self.cells[self.get_index(coord)]

    def can_travel(self, current: Coord, dir: int) -> bool:
        dx = DIR[dir][0]
        dy = DIR[dir][1]

        x = current.col + dx
        y = current.row + dy

        if x < 0 or x >= self.width:
            return False

        if y < 0 or y >= self.height:
            return False

        return True

    def add_wall(self, currentCoord: Coord, dir: int) -> None:
        if not self.is_valid_coord(currentCoord):
            return

        dx = DIR[dir][0]
        dy = DIR[dir][1]

        neighborCoord = Coord(currentCoord.row + dy, currentCoord.col + dx)

        if not self.is_valid_coord(neighborCoord):
            return

        revDir = (dir + 2) % 4

        self.set_cell(currentCoord, self.get_cell(currentCoord) | (1 << dir))
        self.set_cell(neighborCoord, self.get_cell(
            neighborCoord) | (1 << revDir))

    def remove_wall(self, currentCoord: Coord, dir: int) -> None:
        if not self.is_valid_coord(currentCoord):
            return

        dx = DIR[dir][0]
        dy = DIR[dir][1]

        neighborCoord = Coord(currentCoord.row + dy, currentCoord.col + dx)

        if not self.is_valid_coord(neighborCoord):
            return

        revDir = (dir + 2) % 4

        self.set_cell(currentCoord, self.get_cell(currentCoord) & ~(1 << dir))
        self.set_cell(neighborCoord, self.get_cell(
            neighborCoord) & ~(1 << revDir))

    def has_wall(self, first: Coord, second: Coord) -> bool:
        dir = get_direction(first, second)
        revDir = (dir + 2) % 4

        firstCell = self.get_cell(first)
        secondCell = self.get_cell(second)

        return firstCell & (1 << dir) and secondCell & (1 << revDir)

    def is_valid_coord(self, coord: Coord) -> bool:
        return coord.row >= 0 and coord.row < self.height \
            and coord.col >= 0 and coord.col < self.width

    def size(self) -> int:
        return self.width * self.height

    def get_index(self, coord: Coord) -> int:
        return coord.row * self.width + coord.col

    def get_coord(self, index: int) -> Coord:
        return Coord(index//self.width, index % self.height)

    def encode(self):
        res = []

        for row in range(self.height):
            s = ''

            for col in range(self.width):
                s += hex(self.cells[row * self.width + col])[2:]

            res.append(s)

        return res
