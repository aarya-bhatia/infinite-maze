# Maze Generators

## Letter Maze Generator

This class builds a maze in the shape of the letter I using a 'Letter Map'. Some values in this class are currently hard-coded, but it can be extended into something dynamic. The letter map specifies the inner shape of I using an array of strings. Each string represents one row of the letter and contains either a '.' or a 'x'. A x means that the position belongs to the boundary of the letter, but a dot means that there is blank space. Since we only specified 3 columns for the letter I, the rest of the columns for the 7x7 maze can be varied using a random 'offset'. The way our create function generates this maze is that, we iterate over the letter map array and at every 'x', we add 4 walls to that cell. Then we remove those walls that are adjacent to another x, so that we outline the boundary of the shape but not fill in.

## Random Maze Generator

The random maze generator class works on a Union-rank algorithm which uses a Disjoint set data structure, implemented in the maze/dset.py file. The union-set algorithm is used for cycle detection in our random maze.

The RandomMazeGenrator class which is a subclass of the MazeGenerator creates a maze by breaking random walls until all cells are connected to each other. We partition the grid into single-cell sets. As we join any two cells by removing their walls, the cells merge into a bigger set. When all the cells are merged together, we have successfully finished the algorithm. This function ensures that the maze will be solvable and every cell has a path to every other cell. In addition to that, we create 4 random exits on all 4 sides of the maze.
