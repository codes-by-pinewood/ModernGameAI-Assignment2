from captureAgents import CaptureAgent
import random, time, util
from treeNode import Tree
from game import Directions
import game
import json
from collections import defaultdict

import math

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'MCTSAgent', second = 'MCTSAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
#########

class MCTSAgent(CaptureAgent):

  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def __init__(self, index):
      super().__init__(index)
      self.root = None
      self.reward_dict = {}
      
  def initialize_reward_dict(self):
    if self.root not in self.reward_dict:  
      self.reward_dict[self.root] = 0
  
  def update_reward_dict(self, node, reward):
    self.reward_dict[node] = reward

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


    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    # TODO call create graph)
    
    CaptureAgent.registerInitialState(self, gameState)
  
  def compute_reward(self, node):

    #print("selected_action: ", selected_action)
    #stop_penalty = -1000 if selected_action == "STOP" else 0
    food_features = self.food_based_heuristic_reward(node)
    enemy_features = self.enemy_based_heuristic_reward(node)
  
    #stop_features = {'stopPenalty': stop_penalty}
    features = {**food_features, **enemy_features}#, **stop_features}
    
    # Get weights for each feature 
    weights = self.get_weights()
    reward = sum(features[k] * weights[k] for k in features if k in weights)
    return reward


  def chooseAction(self, node):
    """
    Picks the best action using Monte Carlo simulations.
    """
    root = node
    num_simulations = 5
    length_of_one_sim_path = 5

    simulation_rewards = {}
    # Store cumulative rewards per action
    action_rewards = defaultdict(list)
    #actions = ['South', 'North', 'East', 'West', 'Stop']

    for sim_idx in range(num_simulations):
        print(f"Simulation {sim_idx}")
        node = root  # Start from root in each simulation
        simulation_path = []
        action_path = []

        # First action
        selected_action = random.choice(node.getLegalActions(self.index)) 
       
        print(f"selected_action: {selected_action}") 
        action_path.append(selected_action)
        child = node.generateSuccessor(self.index, selected_action)

        if child is None:
            continue  # Skip this simulation if no valid successor

        self.tree.update_visited_nodes(child)
        self.tree.create_relations(node, child, selected_action)

        simulation_path.append(child)
        node = child

        # Simulate the remaining steps
        for i in range(length_of_one_sim_path - 1):  # -1 since action already taken
            legal_actions = node.getLegalActions(self.index)
            if not legal_actions:
                break
            
            next_action = random.choice(legal_actions)
            action_path.append(next_action)
            child = node.generateSuccessor(self.index, next_action)

            if child is None:
                break

            self.tree.update_visited_nodes(child)
            self.tree.create_relations(node, child, next_action)

            simulation_path.append(child)
            node = child

        reward = self.compute_reward(node)
        simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_path, "reward": reward, "action_path": action_path}

        print(f"Simulation {sim_idx} | Action: {selected_action} | Reward: {reward}")

        self.reward_dict = self.tree.new_new_propagate(reward, self.reward_dict, simulation_path)

        # Store reward for the first action taken in this simulation
        action_rewards[selected_action].append(reward)

    max_reward = float('-inf')
    for sim_idx, sim_data in simulation_rewards.items():
      if sim_data["reward"] > max_reward:
          max_reward = sim_data["reward"]
          best_simulation = sim_data  # Get the path and actions for this simulation

    if best_simulation:

        best_action = best_simulation["action_path"][0]

    # Monte Carlo estimation: Compute average reward per action
    #avg_rewards = {action: sum(rewards) / len(rewards) for action, rewards in action_rewards.items()}

    # Select action with highest average reward
    #best_action = max(avg_rewards, key=avg_rewards.get)

    print(f"Chosen Action: {best_action}")

    # Move to the next state in the tree
    self.tree.root = root.generateSuccessor(self.index, best_action)

    return best_action
  



  def food_based_heuristic_reward(self, successor):
    # TODO check weights later
    features = util.Counter()
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList) # the more food not in our belly => worse

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features



  def get_weights(self):
    return {'successorScore': 1, 'distanceToFood': -100, 'enemyDistance': -10}
    #return {'successorScore': 100, 'distanceToFood': -200, 'numInvaders': -100, 'enemyDistance': -100}

  
  def enemy_based_heuristic_reward(self, successor):
    features = util.Counter()
    
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    if (myState.isPacman):
       print("agent is a pacman")
    else:
       print('agent is a agent')

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders] 
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0 and myState.isPacman == False: 
      features['enemyDistance'] = min(dists) * 1000
    elif len(invaders) > 0 and myState.isPacman == True:
      features['enemyDistance'] = min(dists) * -1000
    elif len(invaders) <= 0 and myState.isPacman == True:
       # if there is no invaders then go for the food
       features['enemyDistance'] =   0
    else: 
      #dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['enemyDistance'] =  0# -1 * 1000

    return features
  


  


'''


  def get_weights_enemy_based_heuristic(self, successor):
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    print("myPos: ", myPos)
    if myPos[0] > 14: # if in home territory then run away from enemies 
       return {'enemyDistance': -100}
    else: 
       # if in enemy territory then run towards enemies 
       return {'enemyDistance': -100}
  
'''