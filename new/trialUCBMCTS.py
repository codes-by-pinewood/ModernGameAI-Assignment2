from captureAgents import CaptureAgent
import random, time, util
from tree import Tree
from game import Directions
import game
import json
from collections import defaultdict

import math

#################
# Team creation #
#################

# def createTeam(firstIndex, secondIndex, isRed,
#                first = 'MCTSAgent', second = 'MCTSAgent'):
#   """
#   This function should return a list of two agents that will form the
#   team, initialized using firstIndex and secondIndex as their agent
#   index numbers.  isRed is True if the red team is being created, and
#   will be False if the blue team is being created.

#   As a potentially helpful development aid, this function can take
#   additional string-valued keyword arguments ("first" and "second" are
#   such arguments in the case of this function), which will come from
#   the --redOpts and --blueOpts command-line arguments to capture.py.
#   For the nightly contest, however, your team will be created without
#   any extra arguments, so you should make sure that the default
#   behavior is what you want for the nightly contest.
#   """
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]

def createTeam(firstIndex, secondIndex, isRed,
               first='UCBMCTSAgent', second='DeffensiveMCTSAgent', **kwargs):
  agents = [eval(first)(firstIndex), eval(second)(secondIndex)]
  
  # Save all string-valued opts into each agent's __dict__
  for agent in agents:
      for key, val in kwargs.items():
          if isinstance(val, str) and key not in ['first', 'second']:
              setattr(agent, key, val)

  return agents

##########
# Agents #
#########


class UCBMCTSAgent(CaptureAgent):
    def __init__(self, index):
      super().__init__(index)
      self.root = None
      self.rollout_depth = 5
      self.simulations = 5
      self.visit_counts = defaultdict(int)  # Track visits per node
      self.total_rewards = defaultdict(float)
      self.exploration_constant = 0.1



    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        self.tree = Tree(root = gameState)
        self.tree.relations_dict[gameState] = []
        
        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        if hasattr(self, 'rollout_depth'):
            self.rollout_depth = int(self.rollout_depth)
        if hasattr(self, 'simulations'):
            self.simulations = int(self.simulations)
        if hasattr(self, 'exploration_constant'):
            self.exploration_constant = float(self.exploration_constant)
        

        CaptureAgent.registerInitialState(self, gameState)

    def uct_select(self, node, action):
        if (node, action) not in self.visit_counts:
            return float("inf")  # Encourage unvisited actions

        q_value = self.total_rewards[(node, action)] / self.visit_counts[(node, action)]

        if node not in self.visit_counts:
            self.visit_counts[node] = 1  # Prevent division by zero

        action_visits = max(1, self.visit_counts[(node, action)])

        exploration = self.exploration_constant * math.sqrt(
            math.log(self.visit_counts[node]) / action_visits
        )

        return q_value + exploration

    def select_action(self, node):
       #get the legal actions
       legal_actions = node.getLegalActions(self.index)
       #if legal actions are empty, return Non
       if not legal_actions:
            return None  # No valid actions
       #else return maximum of uct_select 
       best_action = max(legal_actions, key=lambda action: self.uct_select(node, action))
       return best_action
       

    def backpropagate(self, path):
       
        for node, action in path:
            self.visit_counts[(node, action)] += 1
            reward = path.get((node, action), 0)
           
            self.total_rewards[(node, action)] += reward
      

    def simulate(self, node):
        path = [node]
        reward_dict_path = {}
        #print("inside simulate")
        for _ in range(self.rollout_depth):
            legal_actions = node.getLegalActions(self.index)
            if not legal_actions:
                break  # Reached terminal state
            
            action = random.choice(legal_actions)
            child = node.generateSuccessor(self.index, action)
            self.tree.update_relations_dict(node, child)
            path.append(node)
            reward_of_child = self.compute_reward(child) #computes reward of next node
            reward_dict_path[(node, action)] = reward_of_child 
            node = child
            if node is None:
                break
        return reward_dict_path
        
           
    
    def chooseAction(self, root):
        self.tree.root = root 
        root = self.tree.root
        for _ in range(self.simulations):
            print(f"Running simulation {_+1}/{self.simulations}")
            node = root

            if self.tree.isLeaf(node):
                path = self.simulate(node)
                print(f"len(path): {len(path)}")
                self.backpropagate(path)

        
        best_action = max(
            root.getLegalActions(self.index),
            key=lambda action: self.uct_select(root, action),
            default=None
        )
        return best_action
    

    def compute_reward(self, node):
        max_value = 1000
        if node in self.total_rewards:
            initial_reward = self.total_rewards[node]

        else: 
            initial_reward = 0   
        print(f"initial_state_reward: {initial_reward}")  
        parent = self.tree.find_parent(node)
        carrying_food = parent.getAgentState(self.index).numCarrying > 0
        
        # successor = gameState.generateSuccessor(self.index, action)
        myState = node.getAgentState(self.index)
        myPos = myState.getPosition()
        food_reward = self.get_food_reward(myPos, parent, node)
        capsule_reward = self.get_capsule_reward(parent, node)
        ghost_positions = self.get_opponent_distances(myPos, node)
        score = 0

        isPowered = myState.scaredTimer > 0
        enemy_score = self.get_enemy_score(isPowered, ghost_positions)
        carrying_food = parent.getAgentState(self.index).numCarrying > 0

        danger_zone = 6
        ghosts = [node.getAgentState(i) for i in self.getOpponents(node)]
        visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None and g.scaredTimer == 0]
        if visibleGhosts:
            closestGhost = min([self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts])
        else:
            closestGhost = 100
            # features['ghostDanger'] = max(0, danger_zone - closestGhost)**2

        if carrying_food and closestGhost<=danger_zone:
            mid_x = parent.getWalls().width // 2
            if self.red:
                mid_x = mid_x - 2 
            else:
                mid_x = mid_x  
            
            boundary_y = [y for y in range(parent.getWalls().height) 
                        if not parent.hasWall(mid_x, y)]
            
            # Calculate distances to boundary positions
            boundary_distances = [self.getMazeDistance(myPos, (mid_x, y)) 
                                for y in boundary_y]
            # Distance to closest boundary point
            distance_to_boundary = min(boundary_distances) if boundary_distances else 0
            if not myState.isPacman:
                cross_boundry_reward = -100
            else:
                cross_boundry_reward = 0
            print(f'Closest to boundry:{distance_to_boundary} and cross_boundry: {cross_boundry_reward}')
            return distance_to_boundary + cross_boundry_reward

        reward = max_value - (food_reward + capsule_reward + enemy_score + score)
        print(f'This is the reward when not carrying:{reward}')
        return reward
        
        # return reward

    
    def get_food_reward(self, myPos, gameState, successor):
        foodList = self.getFood(successor).asList() 
        current_food_list = self.getFood(gameState).asList() 
        food_eaten = len(current_food_list) > len(foodList)
        if len(foodList) > 0:
            minDist = min([self.getMazeDistance(myPos, food) for food in foodList])
        else:
            minDist = 0 
        if food_eaten:
            food_reward = -100  # Large reward for eating food
        else:
            food_reward = 0

        return minDist + food_reward + len(foodList)
  
    def get_capsule_reward(self, gameState, successor):
        current_capsules = self.getCapsules(gameState)
        successor_capsules = self.getCapsules(successor)
        capsule_eaten = len(current_capsules) > len(successor_capsules)
        score = 0

        if capsule_eaten:
            score -= 200  
        else:
            score = 0
        return score
  
    def get_opponent_distances(self, myPos, successor):
        opponent_indices = self.getOpponents(successor)
        distance_opponents = []
        ghost_positions = []
        for opponent in opponent_indices:
            oppState = successor.getAgentState(opponent)
        oppPos = oppState.getPosition()
        if oppPos: 
            distance = self.getMazeDistance(myPos, oppPos)
            distance_opponents.append(distance)
            if not oppState.isPacman: 
                ghost_positions.append((oppPos, distance, oppState.scaredTimer > 0))
        return ghost_positions
  
    def get_enemy_score(self, isPowered, ghost_positions):
        enemy_score = 0
        if isPowered:
            # Find the closest ghost
            edible_ghosts = [(pos, dist) for pos, dist, scared in ghost_positions if scared]
            if edible_ghosts:
                closest_ghost_dist = min(dist for _, dist in edible_ghosts)
                enemy_score += closest_ghost_dist * 2  

                if closest_ghost_dist == 0:
                    enemy_score -= 300  # Huge reward for eating a ghost
        else:
            # Normal behavior - avoid ghosts
            dangerous_ghosts = [(pos, dist) for pos, dist, scared in ghost_positions if not scared]
            if dangerous_ghosts and min(dist for _, dist in dangerous_ghosts) < 3:
                enemy_score += 100
        return enemy_score


class DeffensiveMCTSAgent(UCBMCTSAgent):
    def compute_reward(self, node):
        max_value = 1000
        if node in self.total_rewards:
            initial_reward = self.total_rewards[node]

        else: 
            initial_reward = 0   
        print(f"initial_state_reward: {initial_reward}")  
        parent = self.tree.find_parent(node)

        # successor = gameState.generateSuccessor(self.index, action)
        myState = node.getAgentState(self.index)
        myPos = node.getAgentState(self.index).getPosition()
        current_enemies = [parent.getAgentState(i) for i in self.getOpponents(parent)]
        current_invaders = [a for a in current_enemies if a.isPacman and a.getPosition() != None]
        
        successor_enemies = [node.getAgentState(i) for i in self.getOpponents(node)]
        successor_invaders = [a for a in successor_enemies if a.isPacman and a.getPosition() != None]

        invader_captured = len(current_invaders) > len(successor_invaders)

        if not myState.isPacman:
            # Find invaders in our territory
            invaders = [a for a in successor_enemies if a.isPacman and a.getPosition() != None]
            
            if invader_captured:
                # Strong reward for eating an invader
                return max_value-(-1000)
            elif len(invaders) > 0:
                # Chase closest invader
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                return max_value - min(dists)
            else:
                # No visible invaders, prioritize defending capsules
                capsules = self.getCapsulesYouAreDefending(node)
                if len(capsules) > 0:
                    capsule_distances = [self.getMazeDistance(myPos, capsule) for capsule in capsules]
                    closest_capsule_dist = min(capsule_distances)
                    return max_value - closest_capsule_dist + 20  
                else:
                    # If no capsules or all capsules are gone, patrol near food
                    food_defending = self.getFoodYouAreDefending(node).asList()
                    if len(food_defending) > 0:
                        food_distances = [self.getMazeDistance(myPos, food) for food in food_defending]
                        closest_food_dist = min(food_distances)
                        return max_value - closest_food_dist + 50  # Lower priority than capsules
                    else:
                        return max_value - len(self.getFoodYouAreDefending(parent).asList())
        else:
            # Penalty for leaving our territory
            return max_value - 500


    
    # def enemy_based_heuristic_reward(self, successor):
    #     features = util.Counter()
    #     # if you are in your home territory, not a pacman then you should run towards invaders 
    #     # if you are in your home territory and there are no invaders run towards the food
    #     # if you are in enemy territory, run away from invaders and towards the food
    #     myState = successor.getAgentState(self.index)
    #     myPos = myState.getPosition()
    #     isPowered = myState.scaredTimer > 0
    #     enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    #     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    #     dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders] 
    #     #print(f"dists: {dists}")
    #     if len(invaders) > 0:
    #         dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    #         enemyDistance = min(dists)
    #         features['enemyDistance'] = enemyDistance
    #         print(f"minimum distance to enemy: {enemyDistance}")
    #         if isPowered or not myState.isPacman:
    #             features['enemyDistance'] = -enemyDistance
    #             if enemyDistance == 0:
    #                 features['enemyDistance'] -= 300 
    #     return features
    

    # def get_weights(self, carrying_food):
    #     if carrying_food:
    #         return {'distanceBorder': -100, 'crossingBorder': 100}
    #         # return {'successorScore': 1000, 'distanceToFood': -100, 'enemyDistance': 200, 'capsuleEaten': -120}
    #     else:
    #         return {'successorScore': 1000, 'distanceToFood': -100, 'enemyDistance': 200, 'capsuleEaten': 120}

    # def food_based_heuristic_reward(self, successor):
    #     # TODO check weights later
    #     features = util.Counter()
    #     foodList = self.getFood(successor).asList()
    #     print(f"len(foodList): {len(foodList)}")    
    #     features['successorScore'] = -len(foodList) # the more food not in our belly => worse

    #     # Compute distance to the nearest food

    #     if len(foodList) > 0: # This should always be True,  but better safe than sorry
    #         myState = successor.getAgentState(self.index)
    #         myPos = successor.getAgentState(self.index).getPosition()
    #         minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    #         if myState.isPacman:

    #             features['distanceToFood'] = minDistance - 40
    #         else: 
    #             features['distanceToFood'] = minDistance 
    #         print(f"minimum distance to food: {minDistance}")
    #     return features
    
    # def get_capsule_heuristic(self, gameState, successor):
    #     features = util.Counter()
    #     current_capsules = self.getCapsules(gameState)
    #     successor_capsules = self.getCapsules(successor)
    #     capsule_eaten = len(current_capsules) > len(successor_capsules)
    #     score = 0

    #     if capsule_eaten:
    #         score += 200  
    #     else:
    #         score = 0
    #     features['capsuleEaten'] = score
    #     return features