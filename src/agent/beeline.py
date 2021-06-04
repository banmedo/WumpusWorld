import sys
sys.path.insert(0, "../..")

from copy import copy
import networkx as nx

from src.world.agent import Agent
from src.world.agent_state import AgentState
from src.world.config import GAME_SETTINGS
from src.world.environment import Environment
from src.world.utils import rand_index, get_adjacent_cells

class BeelineAgent(Agent):
    ACTIONS = ["forward","turn_left","turn_right","shoot"]
    # ACTIONS = ["forward","turn_left","turn_right","grab","shoot","climb"]

    def __init__(self,
                 X = GAME_SETTINGS.SIZE_X,
                 Y = GAME_SETTINGS.SIZE_Y,
                 agent_state = AgentState(),
                 safe_locations = [],
                 beeline_action_list = [],
                 G = nx.Graph(),
                 ):
        self.X = X
        self.Y = Y
        self.agent_state = agent_state
        self.safe_locations = safe_locations
        self.safe_locations.append(self.agent_state.location)
        self.beeline_action_list = beeline_action_list
        self.G = G
        self.entrance = agent_state.location
        self.routed = False

    # convert coordinates to node name
    def coord_to_node(self, coord):
        return "{0},{1}".format(*coord)

    # convert nodename to coordinates
    def node_to_coord(self, node):
        return list(map(lambda x: int(x), node.split(",")))

    # add edge to graph
    def add_edge(self, coord1, coord2, W=1):
        A = self.coord_to_node(coord1)
        B = self.coord_to_node(coord2)
        self.G.add_edge(A, B, weight=W)

    # add edges to all cells that are adjacent to specified cell
    # if they are safe 
    def add_all_edges(self, loc, W=1):
        for adjacent_cell in get_adjacent_cells(loc):
            if (adjacent_cell in self.safe_locations):
                self.add_edge(loc, adjacent_cell)

    # get the shortest path
    def shortest_path(self, coord1, coord2, W='weight'):
        A = self.coord_to_node(coord1)
        B = self.coord_to_node(coord2)
        shortest_route = nx.shortest_path(self.G, A, B, weight=W)
        return list(map(lambda x: self.node_to_coord(x), shortest_route))

    # try to find gold by looking randomly
    def search_for_gold(self, percept):
        action = self.ACTIONS[rand_index(len(self.ACTIONS))]
        if (action == "forward"):
            old_loc = self.agent_state.location
            self.agent_state.act(action, self.X, self.Y)
            new_loc = self.agent_state.location
            if (self.agent_state.location not in self.safe_locations):
                self.safe_locations.append(self.agent_state.location)
            if (old_loc is not new_loc):
                self.add_all_edges(new_loc)
            return action
        else:
            self.agent_state.act(action, self.X, self.Y)
            return action

    # find out which direction you should be facing to go to a 
    # certain cell
    def where_to_face(self, cell_from, cell_to):
        if cell_from[0] == cell_to[0]:
            if cell_from[1] < cell_to[1]:
                face = 0
            else:
                face = 2
        else:
            if cell_from[0] < cell_to[0]:
                face = 1
            else:
                face = 3
        return face

    # find out the actions that you need to take to turn the
    # right way
    def actions_to_turn(self, face_from, face_to):
        face_diff = face_to - face_from
        if face_diff == 1 or face_diff == -3:
            return ["turn_right"]
        elif face_diff == 2 or face_diff == -2:
            return ["turn_right", "turn_right"]
        elif face_diff == 3 or face_diff == -1:
            return ["turn_left"] 
        return []

    # build return plan to return to entrance
    def build_return_plan(self, shortest_path):
        action_list = []
        now_facing = self.agent_state.facing
        for i, loc in enumerate(shortest_path):
            if (i == 0):
                continue
            cell_from = shortest_path[i-1]
            cell_to = shortest_path[i]
            look_where = self.where_to_face(cell_from, cell_to)
            turn_actions = self.actions_to_turn(now_facing, look_where)
            action_list = action_list + turn_actions + ["forward"]
            now_facing = look_where
        self.beeline_action_list = action_list

    # try to get next action
    def next_action(self, percepts):
        if self.agent_state.has_gold:
            if self.agent_state.location == self.entrance:
                return "climb"
            else:
                if self.beeline_action_list == []:
                    shortest_path = self.shortest_path(self.agent_state.location, self.entrance)
                    self.build_return_plan(shortest_path)
                action = self.beeline_action_list.pop(0)
                self.agent_state.act(action, self.X, self.Y)
                return action
        elif percepts.glitter:
            self.agent_state.has_gold = True
            return "grab"
        else:
            return self.search_for_gold(percepts)
