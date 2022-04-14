# Infinite Maze API

## Maze Generation

### Documentation

The following information explains the classes and modules used for this project.

For our backend, we follow an OOP approach to desgin. We have created a base "maze" module containing some helper classes and a "MazeGenerator" class that other generators can override.

- maze
  - coord.py/Coord
    - A class to represent coordinates or positions in the maze by a row and column
  - dir.py
    - DIR: contains a fixed array of 2-dimensional tuples with useful property:
      - Firstly, the i-th index of the array corresponds with the direction (North/South/East/West) which encodes the i-th bit of the cell in the maze. For example, if a cell has a north wall it might have a value of `0b1000`, which is the hex digit 8. So, the North bit is the third bit of this number. Therefore, NORTH is also the third member of the array. If we know which index of the array the direction is in, we can find out how to encode a cell by simply `1 << i` where i is the index.
      - The actual numbers in the tuple, `(dx,dy)` represent the value that when added to a cell with coordinate `(x,y)` equals to the coordinate `(x+dx,y+dy)` of the new cell, when we take one step in the given DIR (index of the array tells the direction). For example, we are at coord (0,0) and we need to take a step in the EAST direction. EAST is the second element of the array and is equal to (1, 0). So the change in x-direction is 1 and the change in y-direction is 0. The new coordinate after moving 1 cell EAST is `(0,0) + (1,0) = (1,0)`.
    - get_direction(first,second) is a function that accepts two coords and calculates the direction that the second coord is in from the first. The direction will be normalised to a unit value. Assume we only move in 4 directions, N-E-S-W.
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

## Data and Middleware

We use a mongodb database for this project.

Database Name: cs240-project-maze

Collections

**mg**: This collection is used to store the URLs for the different backends and maze generators along with metadata that is flexible to changes. This collection follows the following schema:

```{}
{
  _id: ObjectId,
  developmentURL: String,
  URL: String,
  status: String,
  accept_size: String
}
```

Other possible fields include "owner_name", "owner_email" to indicate the owner for that server and a contact information to notify them in case of ay errors/maintainence/changes to the API.

- The URL contains the endpoint for the backend to generate a maze segment and return it as JSON. The developmentURL is optional, if we want to separate the URL from production.
- The status string contains a key such as "available" to indicate that this server is functional. If a backend that is registered in this table fails to work, the status can be modified to "error" or "busy" so that the middleware can try another backend. By default, the middleware gets the "available" servers only. In the future, we can add the "busy" status in case a server is facing a high load. In that case, we can store a "last_access" datetime key in the schema. Then, we can check if the time the server was last accessed was over some value, we can retry that server. Or we can split the servers by location and change that on a daily basis, to balance the load. The users will still see the server results as the final data is going to be persistent on this website.
- The accept size is a key that is static for now. We will store a comma separated list of sizes in the format "<# rows>:<# cols>" where each pair is separated by a colon as shown. This can be useful if our generators can produce different sized mazes and our middleware wants to fetch a particular size maze. Furthermore, for ease, if the rows or columns are set to \* then that acts like a wildcard and means the maze generator can produce a maze with any size. Ex. \*:\* means that any row and any column is okay.

Our middleware does the following validation on each request to `/generateSegment`.

- The middleware gets the list of servers that are currently available for use from the database.
- We search this list to find a server that accepts 7x7 maze sizes and make a get request to the server. It returns a JSON response with the key "geom" containing the data for the maze. The data encoding is still the same. We have a list of "7" strings that each contain "7" hex digits. Each of those hex digits represent the positions of the walls for that cell. The North wall is at position 3, then East, South and West on position 0.
- The middleware ensures that this format is followed. If the data is corrupted in any way, we change the status for this server to "error". At this point, we would like to notify the owner of the server that they have a issue. Therefore, we can add a field to the schema to hold owner name and email.
- If all is okay, the request is forwarded to the frontend where it is rendered for the end user.

## Tasks to add to Middleware

- The frontend is not sending back any data as of now. We would like to keep track of the users real location on the maze and also have some kind of authentication so we can remember where the user last was in the maze.
- The middleware should accept maze data and user data from the frontend on each request to update the required information in the database.

## Features to Implement in Future

1. I want to implement a user auth system to let users create accounts. We can then associate some data to their ID such as statistics about their lifetime using our app. This will make it more engaging for users to try the app and share their scores. For example, we can store information such as the total distanced travelled by the user. Later, we can award 'badges' to users who complete some challenges such as for exploring 'some distance' (like 10000px) of maze.
   1. We can create use the following method to do so: The frontend will regularly ping the backend with the current displacement of the user, or on every request when generating a segment. The backend will update the information in the database for the user who is currently authenticated on the site.
2. We want there to exist a camera system which moves the scree when we cross the edge of the window creating mazes. There screen should 'scroll' with the user into the next maze. This task is mostly a frontend related task. It would involve a fair amount of javascript.
