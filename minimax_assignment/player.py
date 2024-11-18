#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
import math
from copy import deepcopy

def utility_fn(player, node):
    if player == "A":
        return node.state.player_scores[0]
    elif player == 'B':
        return node.state.player_scores[1]
    else:
        raise ValueError(f"Invalid player: {player}!")

def get_movement(node1, node2):
    xA0, yA0 = node1.state.hook_positions[0] # node
    xA1, yA1 = node2.state.hook_positions[0] # child
    if (xA0 == 19 and xA1 == 0) and xA0 - xA1 < 0: # 18 - 19
        return 'right'
    elif (xA0 == 0 and xA1 == 19) and xA0 - xA1 > 0:
        return 'left'
    elif (yA0 - yA1 < 0): # 0 1
        return 'down'
    elif (yA0 - yA1 > 0): # 1 0
        return 'up'
    elif xA0 == xA1 and yA0 == yA1:
        return 'stay'
    else:
        raise ValueError(f"Fucking bugs! ({xA0}, {yA0}) ({xA1}, {yA1})!")
    

class AlphaBetaAlg(object):
    def __init__(self):
        self.next_move = None
        self.best_score = - math.inf
    
    def alphabeta(self, node: Node, depth, alpha, beta, player):
        if depth == 0 and node.compute_and_get_children():
            v = utility_fn(player, node)
        elif player == 'A':
            v = - math.inf
            for child in node.compute_and_get_children():
                v = max(v, self.alphabeta(child, depth-1, alpha, beta, 'B'))
                if v > alpha:
                    alpha = v
                    if alpha > self.best_score:
                        self.best_score = max(alpha, self.best_score)
                        self.next_move = get_movement(node, child)
                        print("Debug: ", node, child)
                if beta <= alpha:
                    break
        elif player == 'B':
            v = math.inf
            for child in node.compute_and_get_children():
                v = min(v, self.alphabeta(child, depth-1, alpha, beta, 'A'))
                if v < beta:
                    beta = v
                if beta <= alpha:
                    break
        return v

# def compute_next_move(node, depth, alpha, beta, player):
#     # next_move = None
#     # best_score = - math.inf
#     recorder = []
#     def alphabeta(node: Node, depth, alpha, beta, player):
#         if depth == 0 and node.compute_and_get_children():
#             v = utility_fn(player, node)
#         elif player == 'A':
#             v = - math.inf
#             for child in node.compute_and_get_children():
#                 v = max(v, alphabeta(child, depth-1, alpha, beta, 'B'))
#                 if v > alpha:
#                     alpha = v
#                     recorder.append([alpha, get_movement(node, child)])
#                     # if alpha > best_score:
#                     #     best_score = max(alpha, best_score)
#                     #     next_move = get_movement(node, child)
#                 if beta <= alpha:
#                     break
#         elif player == 'B':
#             v = math.inf
#             for child in node.compute_and_get_children():
#                 v = min(v, alphabeta(child, depth-1, alpha, beta, 'A'))
#                 if v < beta:
#                     beta = v
#                 if beta <= alpha:
#                     break
#         return v
#     print(recorder)
#     sorted_recoder = sorted(recorder, key=lambda x: -x[0])
#     return sorted_recoder[0][1]


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def search_best_next_move(self, initial_tree_node):
        """
        Use minimax (and extensions) to find best possible next move for player 0 (green boat)
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE USING MINIMAX ###
        
        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!
        # alpha, beta = 0, 0 # alpha and beta are zeros at the begining
        # cur_player = 'A'
        # depth = 2
        # random_move = random.randrange(5)
        # return ACTION_TO_STR[random_move]
        agent = AlphaBetaAlg()
        agent.alphabeta(initial_tree_node, 2, 0, 0, 'A')
        print("Debug: ", agent.next_move)
        return agent.next_move
