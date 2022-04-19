from maze.coord import Coord
from maze.dir import dir_vec_arr, get_direction


class Maze:
    def __init__(self, height, width) -> None:
        """Initialise a maze with <height> rows and <width> columns with no walls"""
        self.height = height
        self.width = width
        self.cells = [0] * (height * width)

    def can_travel(self, current: Coord, direction: int) -> bool:
        """Checks if we can travel from the cell at the current coord in the given direction"""
        if not self.is_valid(current):
            return False

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)

        if not self.is_valid(neighbor):
            return False

        return True

    def add_wall(self, current: Coord, direction: int) -> None:
        """Add a wall from the cell at current coord to the cell at the coord in the direction given, and vice versa"""
        if not self.is_valid(current):
            return

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)
        reverse_direction = (direction + 2) % 4

        if not self.is_valid(neighbor):
            return

        self.cells[self.index(current)] |= (1 << direction)
        self.cells[self.index(neighbor)] |= (1 << reverse_direction)

    def remove_wall(self, current: Coord, direction: int) -> None:
        """Remove the wall from the cell at current coord to the cell at the coord in the direction given, and vice versa"""
        if not self.is_valid(current):
            return

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)
        reverse_direction = (direction + 2) % 4

        if not self.is_valid(neighbor):
            return

        self.cells[self.index(current)] &= ~(1 << direction)
        self.cells[self.index(neighbor)] &= ~(1 << reverse_direction)

    def has_wall(self, first: Coord, second: Coord) -> bool:
        """Check if there exist wall between cells at given coord"""
        direction = get_direction(first, second)
        firstCell = self.cells[self.index(first)]

        if firstCell & (1 << direction) == 0:
            return False

        secondCell = self.cells[self.index(second)]
        reverse_direction = (direction + 2) % 4

        if secondCell & (1 << reverse_direction) == 0:
            return False

        return True

    def is_valid(self, coord: Coord) -> bool:
        """Checks if the cell given by coord is contained inside the maze."""
        return coord.row >= 0 and coord.row < self.height \
            and coord.col >= 0 and coord.col < self.width

    def size(self) -> int:
        """Return the size of the maze"""
        return self.width * self.height

    def index(self, coord: Coord) -> int:
        """Get the index of a cell in maze by given coord"""
        return coord.row * self.width + coord.col

    def coord(self, index: int) -> Coord:
        """Get the coord of the cell at given index in the array"""
        return Coord(index//self.width, index % self.width)

    def encode(self):
        """Encode the maze into a string array by encoding each cell with a single hexadecimal digit."""
        res = []

        for row in range(self.height):
            s = ''

            for col in range(self.width):
                s += hex(self.cells[row * self.width + col])[2:]

            res.append(s)

        return res
