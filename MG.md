# Maze Generators

## Letter Maze Generator

This class builds a maze in the shape of the letter I using a 'Letter Map'. Some values in this class are currently hard-coded, but it can be extended into something dynamic. The letter map specifies the inner shape of I using an array of strings. Each string represents one row of the letter and contains either a '.' or a 'x'. A x means that the position belongs to the boundary of the letter, but a dot means that there is blank space. Since we only specified 3 columns for the letter I, the rest of the columns for the 7x7 maze can be varied using a random 'offset'. The way our create function generates this maze is that, we iterate over the letter map array and at every 'x', we add 4 walls to that cell. Then we remove those walls that are adjacent to another x, so that we outline the boundary of the shape but not fill in.

## Random Maze Generator

The random maze generator class works on a Union-rank algorithm which uses a Disjoint set data structure, implemented in the maze/dset.py file. The union-set algorithm is used for cycle detection in our random maze.

The RandomMazeGenrator class which is a subclass of the MazeGenerator creates a maze by breaking random walls until all cells are connected to each other. We partition the grid into single-cell sets. As we join any two cells by removing their walls, the cells merge into a bigger set. When all the cells are merged together, we have successfully finished the algorithm. This function ensures that the maze will be solvable and every cell has a path to every other cell. In addition to that, we create 4 random exits on all 4 sides of the maze.

### maze

- coord.py/Coord
  - A class to represent coordinates or positions in the maze by a row and column
- dir.py/DIR: contains a fixed array of 2-dimensional tuples with useful property:
  - Firstly, the i-th index of the array corresponds with the direction (North/South/East/West) which encodes the i-th bit of the cell in the maze. For example, if a cell has a north wall it might have a value of `0b1000`, which is the hex digit 8. So, the North bit is the third bit of this number. Therefore, NORTH is also the third member of the array. If we know which index of the array the direction is in, we can find out how to encode a cell by simply `1 << i` where i is the index.
  - The actual numbers in the tuple, `(dx,dy)` represent the value that when added to a cell with coordinate `(x,y)` equals to the coordinate `(x+dx,y+dy)` of the new cell, when we take one step in the given DIR (index of the array tells the direction). For example, we are at coord (0,0) and we need to take a step in the EAST direction. EAST is the second element of the array and is equal to (1, 0). So the change in x-direction is 1 and the change in y-direction is 0. The new coordinate after moving 1 cell EAST is `(0,0) + (1,0) = (1,0)`.
- dir.py/get_direction(first,second): A function that accepts two coords and calculates the direction that the second coord is in from the first. The direction will be normalised to a unit value. Assume we only move in 4 directions, N-E-S-W.
- maze.py/Maze
  - A maze class to represent a single maze instance.
  - A maze stores a list of cells. The values of the cell correspond to the walls the cell has i.e. if the 1st element of the list is 0b1000, the cell #1 i.e. the cell at (1,0) has a wall in the North side.
  - The maze also stores the no. of rows and cols as the 'height' and 'width' data member.
  - The list index is mapped to the 2d coord using the bijective function `(row,col) --> row * width + col`, and vice versa: `coord --> (coord // width, coord % height)`.
  - The maze provides functions to add and remove walls from a cell identified by a coordinate (row, column). The set_cell and get_cell functions internally update the encoding of the cell in the array to match with the state of the maze. There are several other functions that are useful, such as the `is_valid_coord` function which checks if a coord is contained in the maze.
  - The encode function can convert the array into an encoded form, that is used by the backend to send as a response.
- mg.py/MazeGenerator:
  - Base class for maze generators.
  - creates a maze instance in the constructor
  - all subclasses override the create() function which returns a maze
