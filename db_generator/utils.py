import math

def get_srid_from_point(x, y):
    if y < 0:
        base_srid = 32700
    else:
        base_srid = 32600
    return base_srid + math.floor((x+186)/6)
    if x == 180:
        return base_srid + 60