# THIS FILE CONTAIS A SET OF CONFIGS FOR THE GAME

# CONSTANTS
MOVEMOD = {"N":(0, 1), "E":(1, 0), "S":(0, -1), "W":(-1, 0)}

# CLASSES
# Game parameters
class GAME_SETTINGS:
    SIZE_X = 4
    SIZE_Y = 4
    CLIMB_EMPTY = True
    PIT_PROB = 0.2
    ARROWS = 1

# Draw Definitions
class DIMS:
    CELL_SIZE = 100 # pixel size of each cell
    CELL_OUT_WIDTH = 2
    
# Color definitions
class COLORS:
    CELL_FILL = (239,121,138)
    CELL_OUTLINE = (255,255,255)
    AGENT = (65, 157, 120)
    WUMPUS = (147, 22, 33)
    PIT = (45, 48, 71)
    GOLD = (255, 253, 130)

# action points
class POINTS:
    GOLD = 1000
    DEATH = -1000
    ACTION = -1
    ARROW = -10
