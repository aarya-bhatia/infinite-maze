from datetime import datetime, timezone, tzinfo
from flask import Flask, jsonify, request
import requests
from maze.dir import *
from maze.coord import *
from maze.maze import *

app = Flask(__name__)

count = 0
cache = None
http_date_format = "%a, %d %b %Y %H:%M:%S GMT"

# pattern = [
#     '.xxxxxx',
#     '..xxxxx',
#     '...xxxx',
#     'x...xxx',
#     'xx...xx',
#     'xxx...x',
#     'xxxx...',
# ]


def get_maze():
    height = 7
    width = 7
    maze = Maze(height=height, width=width)

    pattern = []

    for y in range(7):
        row = ''
        for x in range(7):
            if abs(y-x) < 2:
                row += '.'
            else:
                row += 'x'
        print(row)
        pattern.append(row)

    for row in range(7):
        for col in range(7):
            if pattern[row][col] == 'x':
                continue

            for i in range(4):
                dx, dy = dir_vec_arr[i]

                x = col + dx
                y = row + dy

                if not maze.is_valid(Coord(y, x)):
                    continue

                if pattern[y][x] == 'x':
                    maze.add_wall(Coord(row, col), i)

    return maze


@app.route('/', methods=["GET"])
def GET_maze_segment():
    global count
    print(f'static-maze 1 count is {count}')

    count += 1

    maze = get_maze()

    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = f"public,max-age={365*24*60*60}"
    response.headers["Age"] = 0

    return response, 200


@app.route('/test', methods=['GET'])
def test():
    global cache

    if cache:
        now = datetime.now(tz=timezone.utc)

        prevDate = cache['date']
        cache['date'] = now
        timeElapsed = now - prevDate
        print("Time Elapsed: " + str(timeElapsed))
        cache["age"] = cache['age']+int(timeElapsed.total_seconds())
        if cache['age'] <= cache['max-age']:
            print("HIT")
            print(cache)
            return jsonify({
                "geom": cache['geom']
            }), 200

    print("MISS")
    response = requests.get('http://127.0.0.1:24002/')

    if response.status_code == 200:
        # print(response.headers)

        data = response.json()
        geom = []

        if "geom" in data:
            geom = data["geom"]

        if "Cache-Control" not in response.headers or response.headers["Cache-Control"] == 'no-store':
            return {"geom": geom}, 200

        date = response.headers["Date"]
        date = datetime.strptime(
            date, http_date_format).replace(tzinfo=timezone.utc)

        age = response.headers["Age"]
        cacheControl = response.headers["Cache-Control"].strip().split(",")
        maxAge = 0

        for keyValue in cacheControl:
            if len(keyValue) > 0 and keyValue.split('=')[0] == 'max-age':
                maxAge = keyValue.split('=')[1]

        cache = {
            "date": date,
            "max-age": int(maxAge),
            "age": int(age),
            "geom": geom
        }

        print(cache)

        return jsonify({"geom": geom}), 200

    return "", 500
