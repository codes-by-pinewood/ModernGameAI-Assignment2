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
               first = 'OffenseVanillaMCTSAgent', second = 'DefenseVanillaMCTSAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
#########

class myVanillaMCTSAgent(CaptureAgent):
  def __init__(self, index):
      super().__init__(index)
      self.root = None
      self.global_reward_dict = {}
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
    CaptureAgent.registerInitialState(self, gameState)
    
  def chooseAction(self, node):
    # Set the root of the tree, add it to visited game states
    root = node
    self.visited_gamestates.append(root)

    # Choose number of simulations and their length
    num_simulations = 50
    length_of_one_sim_path = 4

    # For each simulation, dict: key-simulation path, value-reward; list: all simulations' paths; reverse penalty score for each simulation
    simulation_rewards = {} 
    simulation_paths = []
    reverse_penalties = []


    for sim_idx in range(num_simulations):
        # Start each simulation from the original root
        node = root  
          
        # Create simulation_path and action_path to store explored states and action for current simulation
        simulation_path = []
        action_path = []

        prev_action = None
        reverse_penalty = 0

        for _ in range(length_of_one_sim_path):
            # Step
            actions = [a for a in node.getLegalActions(self.index) if a != Directions.STOP]
            selected_action = random.choice(actions)
            child = node.generateSuccessor(self.index, selected_action)

            # Penalize reverse moves
            if prev_action == Directions.REVERSE[selected_action]:
                reverse_penalty -= 50

            # Update
            self.tree.update_visited_nodes(child)
            self.tree.create_relations(node, child, selected_action)

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
      # parent = simulation_paths[i][-2]
        
      # Compute reward
      reward = self.evaluate_state_reward(leaf_of_simulation)# + self.getScore(leaf_of_simulation)
      reward += reverse_penalties[i]
      
      # Backpropagate along this simulation path
      # self.tree.correct_backprop(leaf_of_simulation, reward, self.global_reward_dict)
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
          score = self.evaluate_state_reward(successor) + self.deadend_no_food(successor, action) * (-500)
          # print(f"Action {action}, Score {score}")

          if score > best_score:
              best_score = score
              best_action = action

      return best_action if best_action else random.choice(actions)



  
class OffenseVanillaMCTSAgent(myVanillaMCTSAgent):
  """
  An MCTS agent that seeks food.
  """

  def evaluate_state_reward(self, successor):
    features = self.offense_heuristic_reward(successor)
    weights = self.get_weights_offense()
    reward = features * weights
    # print(f"OFFENSE REWARD {reward}")
    return reward

  def offense_heuristic_reward(self, successor):
    features = util.Counter()
    myPos = successor.getAgentState(self.index).getPosition()
    myState = successor.getAgentState(self.index)

    foodList = self.getFood(successor).asList()
    capsules = self.getCapsules(successor)

    # How much food we ate?
    prev_food = self.getFood(self.tree.root).asList()
    features['foodEaten'] = len(prev_food) - len(foodList)

    # The closer to the nearest food => the better 
    if foodList:
        features['distanceToFood'] = min([self.getMazeDistance(myPos, food) for food in foodList])

    # # The closer to the nearest capsule => the better 
    # if capsules:
    #     features['distanceToCapsule'] = min([self.getMazeDistance(myPos, cap) for cap in capsules])

    # Ghosts should be avoided
    danger_zone = 6 
    if myState.isPacman:
        ghosts = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None and g.scaredTimer == 0]
        if visibleGhosts:
            closestGhost = min([self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts])
            features['ghostDanger'] = max(0, danger_zone - closestGhost)**2
        else:
            features['ghostDanger'] = 0
    


    # If pacman has more than 5 foods => come home to check it in
    carried = myState.numCarrying
    if carried >= 2:
        mid_x = successor.getWalls().width // 2
        if self.red:
            mid_x = mid_x - 1
        else:
            mid_x = mid_x

        boundary_y = [y for y in range(successor.getWalls().height)
                      if not successor.hasWall(mid_x, y)]
        returnDistances = [self.getMazeDistance(myPos, (mid_x, y)) for y in boundary_y]
        features['distanceToHome'] = min(returnDistances) if returnDistances else 0
    else:
       features['distanceToHome'] = 0
    features['carrying'] = carried

    # print(f"FEATURES: {features}")

    return features
  
  def get_weights_offense(self):
    # return {'foodEaten': 100, 'closestGhostDist': 10, 'escape': -500}
    return {'foodEaten': 20, 'distanceToFood': -2, 'ghostDanger': -7, 'carrying': 40, 'distanceToHome': -12}
    # return {'foodEaten': 20, 'distanceToFood': -2, 'ghostDanger': -40, 'carrying': 30, 'distanceToHome': -20}, no exp ghostDanger



class DefenseVanillaMCTSAgent(myVanillaMCTSAgent):
  """
  This MCTS agent attacks the opponent's pacman.
  Makes sure it is on its own territory when attacking.
  """

  def evaluate_state_reward(self, successor):
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

