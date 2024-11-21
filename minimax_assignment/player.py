#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE
import math
from time import time


def utility_fn(player, node):
    """计算节点的评估值，考虑当前分数、正在捕获的鱼和距离最近的鱼的距离"""
    state = node.state
    player_scores = state.get_player_scores()
    caught = state.get_caught()
    hook_positions = state.get_hook_positions()
    fish_positions = state.get_fish_positions()
    fish_scores = state.get_fish_scores()
    
    score_diff = player_scores[0] - player_scores[1]
    
    p0_score = TYPE_TO_SCORE[caught[0]] if caught[0] is not None else 0
    p1_score = TYPE_TO_SCORE[caught[1]] if caught[1] is not None else 0
    
    closest_fish_distance = float('inf')
    if not caught[0] and fish_positions:  # 如果没有在捕鱼，才考虑距离
        for fish_idx, fish_pos in fish_positions.items():
            if fish_scores[fish_idx] > 0 and caught[1] != fish_idx:  # 只考虑正分值的鱼 & 没被捕获的鱼
                dist = abs(hook_positions[0][0] - fish_pos[0]) + abs(hook_positions[0][1] - fish_pos[1])
                closest_fish_distance = min(dist, closest_fish_distance)
    distance_factor = 0 if closest_fish_distance == float('inf') else closest_fish_distance
    dist_score = 0.
    if not caught[0] and fish_positions:  # 如果没有在捕鱼，才考虑距离
        for fish_idx, fish_pos in fish_positions.items():
            if fish_scores[fish_idx] > 0 and caught[1] != fish_idx:  
                dist = abs(hook_positions[0][0] - fish_pos[0]) + abs(hook_positions[0][1] - fish_pos[1])
                # considering the value of fishes.
                if dist * fish_scores[fish_idx] != 0:
                    dist_score += (1 / dist  * fish_scores[fish_idx])
    final_score = score_diff + p0_score - p1_score + dist_score - distance_factor * 20
    
    return final_score if player == 'A' else -final_score

# def utility_fn(player, node):
#     """计算节点的评估值，考虑当前分数、正在捕获的鱼和距离最近的鱼的距离"""
#     state = node.state
#     player_scores = state.get_player_scores()
#     caught = state.get_caught()
#     hook_positions = state.get_hook_positions()
#     fish_positions = state.get_fish_positions()
#     fish_scores = state.get_fish_scores()
    
#     # score difference before
#     score_diff = player_scores[0] - player_scores[1]
    
#     # fish scores.
#     p0_score = TYPE_TO_SCORE[caught[0]] if caught[0] is not None else 0
#     p1_score = TYPE_TO_SCORE[caught[1]] if caught[1] is not None else 0
    
#     # calculating the nearest fishes' distances with positive scores.
#     closest_fish_distance = float('inf')
#     if not caught[0] and fish_positions:  
#         for fish_idx, fish_pos in fish_positions.items():
#             if fish_scores[fish_idx] > 0:  
#                 dist = math.hypot(
#                     hook_positions[0][0] - fish_pos[0],
#                     hook_positions[0][1] - fish_pos[1]
#                 )
#                 closest_fish_distance = min(closest_fish_distance, dist)
    
#     distance_factor = 0 if closest_fish_distance == float('inf') else closest_fish_distance * 0.1
    
#     # 计算总分
#     final_score = score_diff + p0_score - p1_score - distance_factor
    
#     return final_score if player == 'A' else -final_score

class AlphaBetaAlg(object):
    def __init__(self, init_depth=3):
        self.init_depth = init_depth
        self.next_move = None
        self.start_time = time()
        self.time_limit = 0.08  # 100ms
        self.found_good_move = False
    
    def is_time_left(self):
        return time() - self.start_time < self.time_limit
    
    def alphabeta(self, node, depth, alpha, beta, player):
        if not self.is_time_left():
            raise TimeoutError("Timeout")
        if depth == 0 or not node.compute_and_get_children():
            score = utility_fn(player, node)
            caught = node.state.get_caught()
            if caught[0] is not None and TYPE_TO_SCORE[caught[0]] > 0:
                self.found_good_move = True
            return score
            
        children = node.compute_and_get_children()
        
        if player == 'A':
            v = float('-inf')
            best_move = 'stay'
            for child in children:
                if  not self.is_time_left():
                    raise TimeoutError("Timeout")
                score = self.alphabeta(child, depth-1, alpha, beta, 'B')
                if score > v:
                    v = score
                    if depth == self.init_depth:
                        next_move = child.move if child.move is not None else 0
                        self.next_move = ACTION_TO_STR[next_move]
                alpha = max(alpha, v)
                if beta <= alpha or self.found_good_move or not self.is_time_left():
                    break
                    
        else:  # player B
            v = float("inf")
            for child in children:
                if  not self.is_time_left():
                    raise TimeoutError("Timeout")
                score = self.alphabeta(child, depth-1, alpha, beta, 'A')
                v = min(v, score)
                beta = min(beta, v)
                if beta <= alpha or self.found_good_move:
                    break
        return v

def make_decision(initial_node):
    depth = 7
    
    agent = AlphaBetaAlg(init_depth=depth)
    try:
        score = agent.alphabeta(initial_node, depth, float("-inf"), float("inf"), 'A')
    except TimeoutError as e:
        print(e)
    if agent.found_good_move or not agent.is_time_left():
        print(f"depth {depth} done, movement: {agent.next_move}")
        return agent.next_move
    return agent.next_move

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
        next_move = make_decision(initial_tree_node)
        return next_move
