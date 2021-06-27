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

def get_valid_adjacent_cells(coords, X, Y):
    adjacent_cells = get_adjacent_cells(coords)
    return [[x, y] for x, y in adjacent_cells if (x>=0 and x<X) and (y>=0 and y<Y)]

# Given a cell coordinates and a grid array return what is in the grid array at those coords
def get_neighbors(coords, array):
    adjacent_cells = get_adjacent_cells(coords)
    return list(map(lambda x, y: array[x][y], adjacent_cells))

def calc_distance(point_a, point_b):
    return sqrt(square(point_b[0] - point_a[0]) + square(point_b[1] - point_a[1]))
