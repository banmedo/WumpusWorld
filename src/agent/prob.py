import sys

from networkx.algorithms.shortest_paths.generic import shortest_path
sys.path.insert(0, "../..")

import networkx as nx
import itertools

from src.world.agent import Agent
from src.world.agent_state import AgentState
from src.world.config import MOVEMOD
from src.world.utils import rand_index, get_valid_adjacent_cells

from pomegranate import (
    ConditionalProbabilityTable, 
    Node, 
    BayesianNetwork,
    DiscreteDistribution
)

class ProbAgent(Agent):
    ACTIONS = ["forward","turn_left","turn_right","shoot"]
    # ACTIONS = ["forward","turn_left","turn_right","grab","shoot","climb"]
    PIT_PROB_CUT = 0.5
    WUMPUS_PROB_CUT = 0.49999

    def __init__(self,
                 env,
                 agent_state = AgentState(),
                 ):
        self.X = env.X
        self.Y = env.Y
        self.pit_prob = env.pit_prob
        self.climb_empty = env.climb_empty

        self.agent_state = agent_state
        self.beeline_action_list = []
        self.search_action_list = []

        self.breeze_locations = {}
        self.stench_locations = {}
        self.wumpus_not_in = [self.agent_state.location]
        self.heard_screech = False
        
        self.safe_locations = [self.agent_state.location]
        
        self.G = nx.Graph()
        self.entrance = agent_state.location

        self.string_nodes = self.all_nodes_as_strings()
        
        # build pit-breeze and wumpus stench models
        self.build_pit_model()
        self.build_wumpus_model()


    # convert coordinates to comma separated string
    def coord_to_node(self, coord):
        return "{0},{1}".format(*coord)

    # convert nodename to coordinates
    def node_to_coord(self, node):
        return list(map(lambda x: int(x), node.split(",")))
    
    def xy_to_index(self, xy):
        return xy[0] * 4 + xy[1]

    def all_nodes_as_strings(self):
        return [self.coord_to_node([x, y]) for x in range(0, self.X) for y in range(0, self.Y)]

    def build_pit_model(self):
        # set up a bayesian network for pits and breezes
        self.pit_model = BayesianNetwork("Pit-Breeze")
        
        # add pit nodes
        # set up a container for pit discrete distributions and the nodes
        pit_dds = {}
        pit_ddns = {}
        for string_node in self.string_nodes:
            # get prob for pit
            p = 0 if string_node == "0,0" else self.pit_prob
            # set up a discrette distribution with 
            pit_dd = DiscreteDistribution({True: p, False: 1 - p})
            pit_node_dd = Node(pit_dd, name = f"pit_{string_node}")
            # add node dd to model and container
            self.pit_model.add_node(pit_node_dd)
            pit_dds[string_node] = pit_dd
            pit_ddns[string_node] = pit_node_dd
        
        # add breeze nodes and edges
        # set up a container for breeze cpds
        # self.breeze_cpds = {}
        for x in range(0,self.X):
            for y in range(0, self.Y):
                node = self.coord_to_node([x, y])
                # get adjacent cells
                adjacent_cells = [[x, y] for x, y in get_valid_adjacent_cells([x, y], self.X, self.Y)]
                # generate possible states for each adjacent cell
                states = list(itertools.repeat([True, False], len(adjacent_cells)))
                # a container for all possible states and it's probability
                cpd = []
                # for each combination of states breeze can be True if any adjacent cell has pit (True) 
                for possible_state in itertools.product(*states):
                    li = list(possible_state)
                    cpd.append([*li, True, True in li])
                    cpd.append([*li, False, not(True in li)])
                # get dependent pit nodes
                dependents = [pit_dds[self.coord_to_node([x, y])] for x, y in adjacent_cells]
                # make the cpd table with all possible states and it's dependents
                breeze_cpd = ConditionalProbabilityTable(cpd, dependents)
                breeze_node_cpd = Node(breeze_cpd, name = f"breeze_{node}")
                # add breeze cpd to the model and container
                self.pit_model.add_node(breeze_node_cpd)
                # self.breeze_cpds[node] = breeze_cpd

                # add edges to pit models of adjacent cells
                for pit_node in [self.coord_to_node([x, y]) for x,y in adjacent_cells]:
                    self.pit_model.add_edge(pit_ddns[pit_node], breeze_node_cpd)

        # bake the model to build it
        self.pit_model.bake()


    def build_wumpus_model(self):
        # set up a bayesian network for wumpus and stench
        self.wumpus_model = BayesianNetwork("Wumpus-Stench")
        # calculate 
        cant_be_at = [self.coord_to_node(cell) for cell in self.wumpus_not_in]
        wumpus_prob = 1 / (self.X * self.Y - len(cant_be_at))
        # create discrete distribution for each possible node
        w_node_probs = {}
        for string_node in self.string_nodes:
            w_node_probs[string_node] = 0 if string_node in cant_be_at else wumpus_prob
        wumpus_dd = DiscreteDistribution(w_node_probs)
        wumpus_dn = Node(wumpus_dd, "wumpus_at")
        self.wumpus_model.add_node(wumpus_dn)

        # create conditional probability tables for breeze that are dependent on wumpus location
        for x in range(0, self.X):
            for y in range(0, self.Y):
                stench_cpd_table = []
                stench_string_node = self.coord_to_node([x, y])
                adjacent_cells = [self.coord_to_node([x, y]) for x, y in get_valid_adjacent_cells([x, y], self.X, self.Y)]
                for wumpus_string_node in self.string_nodes:
                    if wumpus_string_node in adjacent_cells:
                        stench_cpd_table.append([wumpus_string_node, True, True])
                        stench_cpd_table.append([wumpus_string_node, False, False])
                    else:
                        stench_cpd_table.append([wumpus_string_node, True, False])
                        stench_cpd_table.append([wumpus_string_node, False, True])
        
                stench_cpd = ConditionalProbabilityTable(stench_cpd_table, [wumpus_dd])
                stench_cpdn = Node(stench_cpd, f"stench_{stench_string_node}")
                self.wumpus_model.add_node(stench_cpdn)

                # add edge from wumpus to stench
                self.wumpus_model.add_edge(wumpus_dn, stench_cpdn)

        # build the model
        self.wumpus_model.bake()
    

    # add edge to network x graph
    def add_edge(self, coord1, coord2, W=1):
        A = self.coord_to_node(coord1)
        B = self.coord_to_node(coord2)
        self.G.add_edge(A, B, weight=W)


    # add edges to all cells that are adjacent to specified cell
    # if they are safe 
    def add_all_edges(self, loc, W=1):
        for adjacent_cell in get_valid_adjacent_cells(loc, self.X, self.Y):
            if (adjacent_cell in self.safe_locations):
                self.add_edge(loc, adjacent_cell)


    # get the shortest path
    def shortest_path(self, coord1, coord2, W='weight'):
        A = self.coord_to_node(coord1)
        B = self.coord_to_node(coord2)
        shortest_route = nx.shortest_path(self.G, A, B, weight=W)
        return list(map(lambda x: self.node_to_coord(x), shortest_route))


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


    # create action plan with the shortest path
    def build_action_plan(self, shortest_path):
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
        return action_list

    # build search plan to search for gold
    def build_search_plan(self):
        current_loc = self.agent_state.location
        pit_probs = self.get_inferred_pit_probs()
        wumpus_probs = self.get_inferred_wumpus_probs()
        
        # from safe locations find best location to explore
        safe_adjacent = [ get_valid_adjacent_cells(loc, self.X, self.Y) for loc in self.safe_locations ]
        adjacent_flat = [
            coord
            for adjacent in safe_adjacent
            for coord in adjacent
            if coord not in self.safe_locations
        ]
        adjacent_ind = [ self.xy_to_index(coord) for coord in adjacent_flat ]
        adjacent_pit_probs = [ pit_probs[ind] for ind in adjacent_ind ]
        adjacent_wumpus_probs = [ wumpus_probs[ind] for ind in adjacent_ind ]

        # possibilities
        # - pit and wumpus < 50%
        #   - best cells to explore
        # - either pit or wumpus > 50%
        #   - there's high risk involved. Die in a pit or be eaten
        # - pit and wumpus > 50%
        #   - worst cells to explore 
        #   - we filter out these cells since

        # from these possibilities find explore candidates as well as
        # candidates if we need to shoot to identify a path
        explore_candidates = []
        shoot_wumpus_candidates = []
        for i, pit_prob in enumerate(adjacent_pit_probs):
            wum_prob = adjacent_wumpus_probs[i]
            if ((pit_prob < self.PIT_PROB_CUT and self.heard_screech) or 
                (pit_prob < self.PIT_PROB_CUT and wum_prob < self.WUMPUS_PROB_CUT)):
                explore_candidates.append(adjacent_flat[i])
            elif (pit_prob < self.PIT_PROB_CUT and wum_prob > self.WUMPUS_PROB_CUT):
                shoot_wumpus_candidates.append(adjacent_flat[i])

        if (len(explore_candidates) > 0):
            traverse_plans = []
            # find which explore candidate is shortest
            for explore_candidate in explore_candidates:
                # find safe cells next to adjacent candidate
                candidate_adjacent = get_valid_adjacent_cells(explore_candidate, self.X, self.Y)
                cand_adj_safe = [ cell for cell in candidate_adjacent if cell in self.safe_locations ]
                # find route to each "gateways"
                for gateway in cand_adj_safe:
                    # find shortest path to a gateway
                    shortest_path = self.shortest_path(current_loc, gateway)
                    if len(shortest_path) == 1:
                        # if we are at the gateway we know where the agent is facing
                        facing_at_end = self.agent_state.facing
                    else:
                        # if we need to move to get to the gateway - we find out the last move 
                        # to get where agent will be facing
                        facing_at_end = self.where_to_face(shortest_path[-2],shortest_path[-1])
                    # find out the direction to face from gateway to enter candidate cell
                    to_face = self.where_to_face(gateway, explore_candidate)
                    # turns needed to face towards the candidate cell
                    final_turns = self.actions_to_turn(facing_at_end, to_face)
                    # add the action plan to get to gateway, take turns and move into the cell
                    traverse_plan = self.build_action_plan(shortest_path) + final_turns + ["forward"]
                    # add the traverse plan for the cell to a list of plans
                    traverse_plans.append(traverse_plan)
            
            # now sort the traverse plans by the number of steps as we want to explore the one
            # that is closest
            traverse_plans.sort(key = lambda x : len(x))
            # take the shortest traverse plan to explore 
            self.search_action_list = traverse_plans[0]
        elif (self.agent_state.has_arrows() and len(shoot_wumpus_candidates) > 0):
            hunt_plans = []
            # find which explore candidate is shortest
            for hunt_candidate in shoot_wumpus_candidates:
                # find safe cells next to adjacent candidate
                candidate_adjacent = get_valid_adjacent_cells(hunt_candidate, self.X, self.Y)
                cand_adj_safe = [ cell for cell in candidate_adjacent if cell in self.safe_locations ]
                # find route to each "gateways"
                for gateway in cand_adj_safe:
                    # find shortest path to a gateway
                    shortest_path = self.shortest_path(current_loc, gateway)
                    if len(shortest_path) == 1:
                        # if we are at the gateway we know where the agent is facing
                        facing_at_end = self.agent_state.facing
                    else:
                        # if we need to move to get to the gateway - we find out the last move 
                        # to get where agent will be facing
                        facing_at_end = self.where_to_face(shortest_path[-2],shortest_path[-1])
                    # find out the direction to face from gateway to enter candidate cell
                    to_face = self.where_to_face(gateway, hunt_candidate)
                    # turns needed to face towards the candidate cell
                    final_turns = self.actions_to_turn(facing_at_end, to_face)
                    # add the action plan to get to gateway, take turns and move into the cell
                    hunt_plan = self.build_action_plan(shortest_path) + final_turns + ["shoot"]
                    # add the traverse plan for the cell to a list of plans
                    hunt_plans.append(hunt_plan)
            
            # now sort the traverse plans by the number of steps as we want to explore the one
            # that is closest
            hunt_plans.sort(key = lambda x : len(x))
            # take the shortest traverse plan to explore 
            self.search_action_list = hunt_plans[0]
        else:
            return_path = self.shortest_path(current_loc, self.entrance)
            bail_plan = self.build_action_plan(return_path)
            bail_plan.append("climb")
            self.search_action_list = bail_plan


    # get the cell probs for pits
    def get_inferred_pit_probs(self):
        pit_model_pred = self.pit_model.predict_proba(self.breeze_locations)
        pred_items = [pred.items() for pred in pit_model_pred[:self.X * self.Y]]
        return [pred[0][1] for pred in pred_items]

    def get_inferred_wumpus_probs(self):
        wumpus_model_pred = self.wumpus_model.predict_proba(self.stench_locations)
        return [pred[1] for pred in wumpus_model_pred[0].items()]

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


    # try to get next action
    def next_action(self, percepts):
        # mark current location as safe location
        current_loc = self.agent_state.location
        if (current_loc not in self.safe_locations):
            self.safe_locations.append(current_loc)

        # add breeze and stench perception to appropriate dictionaries  
        current_node = self.coord_to_node(current_loc)
        if (f"breeze_{current_node}" not in self.breeze_locations):
            self.breeze_locations[f"breeze_{current_node}"] = percepts.breeze
        if (f"stench_{current_node}" not in self.stench_locations):
            self.stench_locations[f"stench_{current_node}"] = percepts.stench
        self.heard_screech = self.heard_screech or percepts.screech

        # print(len(self.pit_model.predict_proba(self.breeze_locations)))
        # print(len(self.wumpus_model.predict_proba(self.stench_locations)))

        if self.agent_state.has_gold:
            if current_loc == self.entrance:
                return "climb"
            else:
                if self.beeline_action_list == []:
                    shortest_path = self.shortest_path(current_loc, self.entrance)
                    self.beeline_action_list = self.build_action_plan(shortest_path)
                action = self.beeline_action_list.pop(0)
                self.agent_state.act(action, self.X, self.Y)
                return action
        elif percepts.glitter:
            self.agent_state.has_gold = True
            return "grab"
        else:
            if self.search_action_list == []:
                self.build_search_plan()
            action = self.search_action_list.pop(0)
            if (action == "forward"):
                self.agent_state.act(action, self.X, self.Y)
                new_loc = self.agent_state.location
                if not self.heard_screech:
                    # add new location to list where wumpus is not in
                    # if we are wrong, the game terminates and agent is dead
                    # so it doesn't matter. It doesn't matter if wumpus is dead 
                    # either
                    if new_loc not in self.wumpus_not_in:
                        self.wumpus_not_in.append(new_loc)
                    # update the wumpus prob model with where wumpus can't be
                    self.build_wumpus_model()
                if (current_loc is not new_loc):
                    self.add_all_edges(new_loc)
                return action
            elif (action == "shoot"):
                self.agent_state.act(action, self.X, self.Y)
                # add all cells that the agent is facing to safe location as
                # either wumpus isn't there or it's dead
                move_vector = MOVEMOD[self.agent_state.get_direction()]
                # find cells that the arrows can go through
                x = current_loc[0]
                y = current_loc[1]
                while True:
                    x = x + move_vector[0]
                    y = y + move_vector[1]
                    if (x < 0 or x > self.X ) or (y < 0 or y> self.Y):
                        break
                    if [x, y] not in self.wumpus_not_in:
                        self.wumpus_not_in.append([x, y])
                self.build_wumpus_model()
                return action
            else:
                self.agent_state.act(action, self.X, self.Y)
                return action
