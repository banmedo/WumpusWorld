# This file contains the utility/helper functions
import random

from numpy import sqrt, square

def rand_index(max):
    return random.randint(0, max-1)

def rand_prob():
    return random.uniform(0,1)

def rand_cell_not_origin(X,Y):
    x = rand_index(X)
    y = rand_index(Y)
    if [x,y] == [0,0]:
        return rand_cell_not_origin(X,Y)
    else:
        return [x,y]

def clamp(x, low, high):
    return max(low, min(x, high))

def get_adjacent_cells(coords):
    return list(map(lambda x: [coords[0]+x[0], coords[1]+x[1]], [[0,1],[1,0],[0,-1],[-1,0]]))

def calc_distance(point_a, point_b):
    return sqrt(square(point_b[0] - point_a[0]) + square(point_b[1] - point_a[1]))
