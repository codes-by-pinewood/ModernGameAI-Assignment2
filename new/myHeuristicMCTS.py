from captureAgents import CaptureAgent
import random, time, util
from treeNode import Tree
from game import Directions
import game
import math


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffenseHeuristicMCTSAgent', second = 'DefenseHeuristicMCTSAgent', **kwargs):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  # The following line is an example only; feel free to change it.
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]

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

class myHeuristicMCTSAgent(CaptureAgent):
  def __init__(self, index):
      super().__init__(index)
      self.root = None
      self.global_reward_dict = {}
      self.num_simulations = 10
      self.length = 4
      self.exploration_constant = 0.3
      self.initialize_global_reward_dict()


  def initialize_global_reward_dict(self):
    """
    Sets the reward of the root state to 0.
    """
    if self.root not in self.global_reward_dict:  
      self.global_reward_dict[self.root] = 0
  

  # def update_global_reward_dict(self, node, reward):
  #   self.global_reward_dict[node] = reward


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
    self.visited_gamestates = []

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    if hasattr(self, 'length'):
        self.length = int(self.length)
    if hasattr(self, 'num_simulations'):
        self.num_simulations = int(self.num_simulations)
    if hasattr(self, 'exploration_constant'):
        self.exploration_constant = float(self.exploration_constant)

    CaptureAgent.registerInitialState(self, gameState)
    
  def chooseAction(self, node):
    # Set the root of the tree, add it to visited game states
    root = node
    self.visited_gamestates.append(root)

    # For each simulation, dict: key-simulation path, value-reward; list: all simulations' paths; reverse penalty score for each simulation
    simulation_rewards = {} 
    simulation_paths = []
    reverse_penalties = []


    for sim_idx in range(self.num_simulations):
        # Start each simulation from the original root
        node = root  
          
        # Create simulation_path and action_path to store explored states and action for current simulation
        simulation_path = []
        action_path = []

        prev_action = None
        reverse_penalty = 0

        for _ in range(self.length):
            # Step
            selected_action = self.heuristic_action(node, epsilon=0.1)
            child = node.generateSuccessor(self.index, selected_action)

            # Penalize reverse moves
            if prev_action == Directions.REVERSE[selected_action]:
                reverse_penalty -= 50

            # Update
            self.tree.update_visited_nodes(child)
            self.tree.create_relations(node, child, selected_action)
            self.tree.update_relations_dict(node, child)

            # Append
            simulation_path.append(child)
            action_path.append(selected_action)

            # Move to next state
            node = child  
            prev_action = selected_action

            # Ensure the visited state is in the reward dict
            if node not in self.global_reward_dict:
               self.global_reward_dict[node] = 0
            
        # After the end of a simulation, append the whole path and reverse penalties
        simulation_paths.append(simulation_path)
        reverse_penalties.append(reverse_penalty)
        # print(f"Reverse penalty {reverse_penalties}")


    # After ALL simulation are done, update the reward
    for i in range(len(simulation_paths)):
      # print(f"Reverse penalty {reverse_penalties[i]}")
      leaf_of_simulation = simulation_paths[i][-1]
      parent = simulation_paths[i][-2]
        
      # Compute reward
      reward = self.evaluate_state_reward(parent, leaf_of_simulation)# + self.getScore(leaf_of_simulation)
      reward += reverse_penalties[i]
      
      # Backpropagate along this simulation path
      simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_paths[i], "reward": reward, "action_path": action_path}

    # instead, we want to track the best total reward per first action, then pick the action with the best average (or max) performance.

    # Group rewards by first action
    action_to_rewards = {}

    for sim_data in simulation_rewards.values():
        first_action = sim_data["action_path"][0]
        reward = sim_data["reward"]

        if first_action not in action_to_rewards:
            action_to_rewards[first_action] = []

        action_to_rewards[first_action].append(reward)

    # Choose action with highest average reward
    action_avg_rewards = {
        action: sum(rewards) / len(rewards)
        for action, rewards in action_to_rewards.items()
    }
    best_action = max(action_avg_rewards.items(), key=lambda x: x[1])[0]
    # print("best_action: ", best_action)
    # print("best action's reward: ", action_avg_rewards[best_action])

    # Update the tree root 
    child_node = root.generateSuccessor(self.index, best_action)    
    self.tree.root = child_node
    self.tree.visited_nodes = []

    # Add the child to already visited gamestates
    self.visited_gamestates.append(child_node)
    return best_action
  


  def deadend_no_food(self, successor, action):
    actions = [a for a in successor.getLegalActions(self.index) if a != Directions.STOP]
    if len(actions) == 1 and actions[0] == Directions.REVERSE[action]:
      myPos = successor.getAgentState(self.index).getPosition()
      if self.getFood(successor)[int(myPos[0])][int(myPos[1])] == 'False':
        # print("DEADEND")
        return 1
    return 0


  def heuristic_action(self, gameState, epsilon):
      actions = gameState.getLegalActions(self.index)
      actions = [a for a in actions if a != Directions.STOP]

      if random.random() < epsilon:
         return random.choice(actions)

      best_score = float('-inf')
      best_action = None

      for action in actions:
          successor = gameState.generateSuccessor(self.index, action)
          # print(f"IS DEADEND? {self.deadend_no_food(successor, action)}")
          score = self.evaluate_state_reward(gameState, successor) + self.deadend_no_food(successor, action) * (-500)
          # print(f"Action {action}, Score {score}")

          if score > best_score:
              best_score = score
              best_action = action

      return best_action if best_action else random.choice(actions)



  
class OffenseHeuristicMCTSAgent(myHeuristicMCTSAgent):
  """
  An MCTS agent that seeks food.
  """

  def evaluate_state_reward(self, gameState, successor):
      max_value = 1000
      # print(successor)
      # parent = self.tree.find_parent(successor)
      carrying_food = gameState.getAgentState(self.index).numCarrying > 0
      
      # successor = gameState.generateSuccessor(self.index, action)
      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      food_reward = self.get_food_reward(myPos, gameState, successor)
      capsule_reward = self.get_capsule_reward(gameState, successor)
      ghost_positions = self.get_opponent_distances(myPos, successor)
      score = 0

      isPowered = myState.scaredTimer > 0
      enemy_score = self.get_enemy_score(isPowered, ghost_positions)
      carrying_food = gameState.getAgentState(self.index).numCarrying > 0

      danger_zone = 6

      # if myState.isPacman:
      #     ghosts = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      #     visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None and g.scaredTimer == 0]
      #     if visibleGhosts:
      #         closestGhost = min([self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts])
      #         features['ghostDanger'] = max(0, danger_zone - closestGhost)**2
      #     else:
      #         features['ghostDanger'] = 0

      ghosts = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None and g.scaredTimer == 0]
      if visibleGhosts:
          closestGhost = min([self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts])
      else:
          closestGhost = 100
          # features['ghostDanger'] = max(0, danger_zone - closestGhost)**2

      if carrying_food and closestGhost<=danger_zone:
          mid_x = gameState.getWalls().width // 2
          if self.red:
              mid_x = mid_x - 2 
          else:
              mid_x = mid_x  
          
          boundary_y = [y for y in range(gameState.getWalls().height) 
                      if not gameState.hasWall(mid_x, y)]
          
          # Calculate distances to boundary positions
          boundary_distances = [self.getMazeDistance(myPos, (mid_x, y)) 
                              for y in boundary_y]
          # Distance to closest boundary point
          distance_to_boundary = min(boundary_distances) if boundary_distances else 0
          if not myState.isPacman:
              cross_boundry_reward = -100
          else:
              cross_boundry_reward = 0
        #   print(f'Closest to boundry:{distance_to_boundary} and cross_boundry: {cross_boundry_reward}')
          return distance_to_boundary + cross_boundry_reward

      reward = max_value - (food_reward + capsule_reward + enemy_score + score)
    #   print(f'This is the reward when not carrying:{reward}')
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

    # features = self.offense_heuristic_reward(successor)
    # weights = self.get_weights_offense()
    # reward = features * weights
    # # print(f"OFFENSE REWARD {reward}")
    # return reward

  # def offense_heuristic_reward(self, successor):
  #   features = util.Counter()
  #   myPos = successor.getAgentState(self.index).getPosition()
  #   myState = successor.getAgentState(self.index)

  #   foodList = self.getFood(successor).asList()
  #   capsules = self.getCapsules(successor)

  #   # How much food we ate?
  #   prev_food = self.getFood(self.tree.root).asList()
  #   features['foodEaten'] = len(prev_food) - len(foodList)

  #   # The closer to the nearest food => the better 
  #   if foodList:
  #       features['distanceToFood'] = min([self.getMazeDistance(myPos, food) for food in foodList])

  #   # # The closer to the nearest capsule => the better 
  #   # if capsules:
  #   #     features['distanceToCapsule'] = min([self.getMazeDistance(myPos, cap) for cap in capsules])

  #   # Ghosts should be avoided
  #   danger_zone = 6 
  #   if myState.isPacman:
  #       ghosts = [successor.getAgentState(i) for i in self.getOpponents(successor)]
  #       visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None and g.scaredTimer == 0]
  #       if visibleGhosts:
  #           closestGhost = min([self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts])
  #           features['ghostDanger'] = max(0, danger_zone - closestGhost)**2
  #       else:
  #           features['ghostDanger'] = 0
    


  #   # If pacman has more than 5 foods => come home to check it in
  #   carried = myState.numCarrying
  #   if carried >= 2:
  #       mid_x = successor.getWalls().width // 2
  #       if self.red:
  #           mid_x = mid_x - 1
  #       else:
  #           mid_x = mid_x

  #       boundary_y = [y for y in range(successor.getWalls().height)
  #                     if not successor.hasWall(mid_x, y)]
  #       returnDistances = [self.getMazeDistance(myPos, (mid_x, y)) for y in boundary_y]
  #       features['distanceToHome'] = min(returnDistances) if returnDistances else 0
  #   else:
  #      features['distanceToHome'] = 0
  #   features['carrying'] = carried

  #   # print(f"FEATURES: {features}")
  #   return features
  

  
  def get_weights_offense(self):
    # return {'foodEaten': 100, 'closestGhostDist': 10, 'escape': -500}
    return {'foodEaten': 20, 'distanceToFood': -2, 'ghostDanger': -7, 'carrying': 40, 'distanceToHome': -12}
    # return {'foodEaten': 20, 'distanceToFood': -2, 'ghostDanger': -40, 'carrying': 30, 'distanceToHome': -20}, no exp ghostDanger



class DefenseHeuristicMCTSAgent(myHeuristicMCTSAgent):
  """
  This MCTS agent attacks the opponent's pacman.
  Makes sure it is on its own territory when attacking.
  """

  def evaluate_state_reward(self, gameState, successor):
    features = self.enemy_based_heuristic_reward(successor)
    weights = self.get_weights_defense()
    reward = features * weights
    return reward
    
  def enemy_based_heuristic_reward(self, successor):
    """
    Logic: 
    1. Are there visible invaders? If yes, approach the closest of them
    2. If there are none, come as close to the one that have not crossed the boarder yet. The moment it crosses, follow
    """
    features = util.Counter()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

    # there are visible invaders
    if len(invaders) > 0: # This should always be True, but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, enemy.getPosition()) for enemy in invaders])
      features['distanceToInvader'] = minDistance

    # no visible invaders => approach the boarder
    else:
      myPos = successor.getAgentState(self.index).getPosition()
      mid_x = successor.getWalls().width // 2
      if self.red:
          mid_x = mid_x - 1  
      else:
          mid_x = mid_x 

      boundary_y = [y for y in range(successor.getWalls().height)
                    if not successor.hasWall(mid_x, y)]
      
      # Calculate distances to boundary positions
      boundary_distances = [self.getMazeDistance(myPos, (mid_x, y)) 
                            for y in boundary_y]
      # Distance to closest boundary point
      features['distance_to_boundary'] = min(boundary_distances) if boundary_distances else 0

    
    # To motivate ghosts to eat the pacmans!!
    previousState = self.tree.root 
    previousInvaders = [a for a in self.getOpponents(previousState) 
                        if previousState.getAgentState(a).isPacman and previousState.getAgentState(a).getPosition() is not None]
    previousCount = len(previousInvaders)

    currentInvaders = [a for a in self.getOpponents(successor) 
                      if successor.getAgentState(a).isPacman and successor.getAgentState(a).getPosition() is not None]
    currentCount = len(currentInvaders)

    features['invaderEaten'] = previousCount - currentCount

    return features
  

  def get_weights_defense(self):
    '''
    get the distance to invader. 
    '''
    return {'distanceToInvader': -100, 'distance_to_boundary': -50, 'invaderEaten': 1000}

  


  



