# Random Maze Generator

Module: random-maze

- dset.py/Dset
  - A class for a Disjoint set data structure.
  - This class is used for union-set algorithm for cycle detection in the random maze generator.
- random_mg.py/RandomMazeGenrator
  - This is a type of MazeGenerator which creates a maze randomly. The only thing it ensures is that a maze will be solvable and every cell has a path to every other cell. In addition to that, I create 4 random exits on all 4 sides of the maze.
- app.py
