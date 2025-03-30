from captureAgents import CaptureAgent
import random, time, util
from tree import Tree
from game import Directions
from collections import defaultdict

import math

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='UCTMCTSAgent', second='DeffensiveMCTSAgent', **kwargs):
  agents = [eval(first)(firstIndex), eval(second)(secondIndex)]
  
  for agent in agents:
      for key, val in kwargs.items():
          if isinstance(val, str) and key not in ['first', 'second']:
              setattr(agent, key, val)

  return agents

##########
# Agents #
#########


class UCTMCTSAgent(CaptureAgent):
    def __init__(self, index):
      super().__init__(index)
      self.root = None
      self.rollout_depth = 5
      self.simulations = 5
      self.visit_counts = defaultdict(int)  # Track visits per node
      self.total_rewards = defaultdict(float)
      self.exploration_constant = 0.1
      self.epsilon = 1

    def registerInitialState(self, gameState):
        self.tree = Tree(root = gameState)
        self.tree.relations_dict[gameState] = []
        if hasattr(self, 'rollout_depth'):
            self.rollout_depth = int(self.rollout_depth)
        if hasattr(self, 'simulations'):
            self.simulations = int(self.simulations)
        if hasattr(self, 'exploration_constant'):
            self.exploration_constant = float(self.exploration_constant)
        if hasattr(self, 'epsilon'):
            self.epsilon = float(self.epsilon)
        CaptureAgent.registerInitialState(self, gameState)

    def uct_select(self, node, action):
        if (node, action) not in self.visit_counts:
            return float("inf")  # Encourage unvisited actions
        
        self.exploration_constant = self.exploration_constant * self.epsilon

        q_value = self.total_rewards[(node, action)] / self.visit_counts[(node, action)]

        if node not in self.visit_counts:
            self.visit_counts[node] = 1  # Prevent division by zero

        action_visits = max(1, self.visit_counts[(node, action)])

        exploration = self.exploration_constant * math.sqrt(
            math.log(self.visit_counts[node]) / action_visits
        )

        return q_value + exploration

    def select_action(self, node):
       legal_actions = node.getLegalActions(self.index)
       if not legal_actions:
            return None  
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
        if node in self.total_rewards:
            initial_reward = self.total_rewards[node]
        else: 
            initial_reward = 0   
        parent = self.tree.find_parent(node)
        carrying_food = parent.getAgentState(self.index).numCarrying > 0
        
        if not carrying_food:
            food_features = self.food_based_heuristic_reward(node)
            capsule_features = self.get_capsule_heuristic(parent, node)
            enemy_features = self.enemy_based_heuristic_reward(node)
        
            features = {**food_features, **enemy_features, **capsule_features}
            
            # Get weights for each feature 
            weights = self.get_weights(carrying_food)
            reward = sum(features[k] * weights[k] for k in features if k in weights)
            print(f"calculated_reward: {reward}")
        else:
            features = util.Counter()
            mid_x = parent.getWalls().width // 2
            if self.red:
                mid_x = mid_x - 2 
            else:
                mid_x = mid_x  
            
            boundary_y = [y for y in range(parent.getWalls().height) 
                        if not parent.hasWall(mid_x, y)]
            
            # Calculate distances to boundary positions
            boundary_distances = [self.getMazeDistance(node.getAgentState(self.index).getPosition(), (mid_x, y)) 
                                for y in boundary_y]
            # Distance to closest boundary point
            distance_to_boundary = min(boundary_distances) if boundary_distances else 0
            if not node.getAgentState(self.index).isPacman:
                cross_boundry_reward = 100
            else:
                cross_boundry_reward = 0
            
            features['distanceBorder'] = distance_to_boundary
            features['crossingBorder'] = cross_boundry_reward
            weights = self.get_weights(carrying_food)
            reward = sum(features[k] * weights[k] for k in features if k in weights)
            print(f"calculated_reward: {reward}")
        
        return reward


    
    def enemy_based_heuristic_reward(self, successor):
        features = util.Counter()
        # if you are in your home territory, not a pacman then you should run towards invaders 
        # if you are in your home territory and there are no invaders run towards the food
        # if you are in enemy territory, run away from invaders and towards the food
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        isPowered = myState.scaredTimer > 0
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders] 
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            enemyDistance = min(dists)
            features['enemyDistance'] = enemyDistance
            print(f"minimum distance to enemy: {enemyDistance}")
            if isPowered or not myState.isPacman:
                features['enemyDistance'] = -enemyDistance
                if enemyDistance == 0:
                    features['enemyDistance'] -= 300 
        return features
    

    def get_weights(self, carrying_food):
        if carrying_food:
            return {'distanceBorder': -100, 'crossingBorder': 100}
        else:
            return {'successorScore': 1000, 'distanceToFood': -100, 'enemyDistance': 200, 'capsuleEaten': 120}

    def food_based_heuristic_reward(self, successor):
        features = util.Counter()
        foodList = self.getFood(successor).asList()
        print(f"len(foodList): {len(foodList)}")    
        features['successorScore'] = -len(foodList) # the more food not in our belly => worse

        # Compute distance to the nearest food
        if len(foodList) > 0: 
            myState = successor.getAgentState(self.index)
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            if myState.isPacman:

                features['distanceToFood'] = minDistance - 40
            else: 
                features['distanceToFood'] = minDistance 
            print(f"minimum distance to food: {minDistance}")
        return features
    
    def get_capsule_heuristic(self, gameState, successor):
        features = util.Counter()
        current_capsules = self.getCapsules(gameState)
        successor_capsules = self.getCapsules(successor)
        capsule_eaten = len(current_capsules) > len(successor_capsules)
        score = 0

        if capsule_eaten:
            score += 200  
        else:
            score = 0
        features['capsuleEaten'] = score
        return features
    

class DeffensiveMCTSAgent(UCTMCTSAgent):
    def compute_reward(self, node):
        max_value = 1000
        if node in self.total_rewards:
            initial_reward = self.total_rewards[node]

        else: 
            initial_reward = 0   
        print(f"initial_state_reward: {initial_reward}")  
        parent = self.tree.find_parent(node)

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


