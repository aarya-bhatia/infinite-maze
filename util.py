def validate_grid(num_rows, num_cols, grid):
    if len(grid) != int(num_rows):
        return False
    for row in grid:
        if len(row) != int(num_cols):
            return False
        for col in row:
            if not((col >= '0' and col <= '9') or (col >= 'a' and col <= 'f') or (col >= 'A' and col <= 'F')):
                return False

    return True


def has_available_size(num_rows, num_cols, server):
    accept_size = server["accept_size"].split(",")

    for size in accept_size:
        dimensions = size.split(":")
        if (dimensions[0] == "*" or dimensions[0] == num_rows) and (dimensions[1] == '*' or dimensions[1] == num_cols):
            return True

    return False
