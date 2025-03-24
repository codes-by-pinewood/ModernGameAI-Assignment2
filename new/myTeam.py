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
               first = 'OffenseMCTSAgent', second = 'OffenseMCTSAgent'):
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

class MCTSAgent(CaptureAgent):
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
    num_simulations = 5
    length_of_one_sim_path = 15

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
            # selected_action = self.select_uct_action(node)
            selected_action = self.heuristic_action(node)
            child = node.generateSuccessor(self.index, selected_action)

            # Penalize reverse moves
            if prev_action and prev_action == Directions.REVERSE[selected_action]:
                reverse_penalty += -100

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


    # After ALL simulation are done, update the reward
    for i in range(len(simulation_paths)):
      leaf_of_simulation = simulation_paths[i][-1]
        
      # Compute reward
      reward = self.evaluate_state_reward(leaf_of_simulation) # self.getScore(leaf_of_simulation) + 
      reward += reverse_penalties[i]
      print(f"reward {reward}")
      
      # Backpropagate along this simulation path
      self.tree.correct_backprop(leaf_of_simulation, reward, self.global_reward_dict)
      simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_paths[i], "reward": reward, "action_path": action_path}

    # BEFORE
    # this chooses the first action of the simulation that resulted in the higest reward. that could be random
    # # Store reward dict for later
    # max_reward = float('-inf')
    # for sim_idx, sim_data in simulation_rewards.items():
    #   if sim_data["reward"] > max_reward:
    #       max_reward = sim_data["reward"]
    #       best_simulation = sim_data  

    # # if best_simulation:
    # print(f"Best simulation: Path: {best_simulation['path']} | Reward: {best_simulation['reward']} | Action Path: {best_simulation['action_path']}")
    # best_action = best_simulation["action_path"][0]  # Take the first action in the best action path

    # AFTER
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
    print("best_action: ", best_action)

    # Update the tree root 
    child_node = root.generateSuccessor(self.index, best_action)    
    self.tree.root = child_node
    self.tree.visited_nodes = []

    # Add the child to already visited gamestates
    self.visited_gamestates.append(child_node)

    return best_action
  

  # def select_uct_action(self, node, explore=2.0):
  #     """
  #     Select the best action from this node using UCT.

  #     Args:
  #         node: The current gameState node.
  #         explore: Exploration constant. Higher values favor less visited nodes.

  #     Returns:
  #         action (Direction): The best action based on UCT value.
  #     """
  #     if node not in self.tree.relations:
  #         legal_actions = [a for a in node.getLegalActions(self.index) if a != Directions.STOP]
  #         return random.choice(legal_actions)  

  #     best_score = float('-inf')
  #     best_action = None

  #     parent_visits = self.tree.times_visited.get(node, 1)

  #     for child, action in self.tree.relations[node]:
  #         child_visits = self.tree.times_visited.get(child, 0)
  #         total_reward = self.global_reward_dict.get(child, 0)

  #         if child_visits == 0:
  #             return action  # Try unvisited node immediately

  #         avg_reward = total_reward / child_visits
  #         uct_score = avg_reward + explore * math.sqrt(math.log(parent_visits) / child_visits)

  #         if uct_score > best_score:
  #             best_score = uct_score
  #             best_action = action

  #     return best_action if best_action is not None else random.choice(node.getLegalActions(self.index))

  def heuristic_action(self, gameState):
      actions = gameState.getLegalActions(self.index)
      actions = [a for a in actions if a != Directions.STOP]

      best_score = float('-inf')
      best_action = None

      for action in actions:
          successor = gameState.generateSuccessor(self.index, action)
          score = self.evaluate_state_reward(successor)
          if score > best_score:
              best_score = score
              best_action = action

      return best_action if best_action else random.choice(actions)



  
class OffenseMCTSAgent(MCTSAgent):
  """
  An MCTS agent that seeks food.
  """

  def evaluate_state_reward(self, successor):
    # print("Offense evaluate state reward")
    features = self.food_based_heuristic_reward(successor)
    # print("Features:", features)
    weights = self.get_weights_offense()
    # print("Weights:", weights)
    reward = features * weights
    # print("Heuristic reward:", reward)
    return reward


      
  def food_based_heuristic_reward(self, successor):
    # TODO check weights later
    features = util.Counter()
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList) # the more food not in our belly => worse

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True, but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Only consider ghosts if we are on the opponent’s side (i.e., we are Pacman)
    myState = successor.getAgentState(self.index)
    if myState.isPacman:
        ghosts = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        visibleGhosts = [g for g in ghosts if not g.isPacman and g.getPosition() is not None]
        if visibleGhosts:
            myPos = myState.getPosition()
            ghostDistances = [self.getMazeDistance(myPos, g.getPosition()) for g in visibleGhosts]
            minGhostDist = min(ghostDistances)
            features['distanceToGhost'] = minGhostDist  # Larger = safer

    # Only consider the distance to boundary if we are on our side (i.e., we are ghost)
    else:
      # Feature - distance to boundary. While offense ghost, the closer it is to the boundary, the better
      mid_x = successor.getWalls().width // 2
      if self.red:
          mid_x = mid_x - 1  
      else:
          mid_x = mid_x  
      
      boundary_y = [y for y in range(successor.getWalls().height) 
                  if not successor.hasWall(mid_x, y)]
      
      # Calculate distances to boundary positions
      boundary_distances = [self.getMazeDistance(myState.getPosition(), (mid_x, y)) 
                          for y in boundary_y]
      # Distance to closest boundary point
      distance_to_boundary = min(boundary_distances) if boundary_distances else 0

      features['distance_to_boundary'] = distance_to_boundary
    return features
  

  def get_weights_offense(self):
    '''
    heuristic based on offensive strategy: getting more food. 
    '''
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToGhost': 10, 'distance_to_boundary': -1000}



class DefenseMCTSAgent(MCTSAgent):
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
    features = util.Counter()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    if len(invaders) > 0: # This should always be True, but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, enemy.getPosition) for enemy in invaders])
      features['distanceToInvader'] = minDistance
    return features

  def get_weights_defense(self):
    '''
    get the distance to invader. 
    '''
    return {'distanceToInvader': -1}

  


  




## CURRENTLY NOT USED
  
  # def select(self, node):
  #   #print("are we here?")
  #   while not node.is_fully_expanded():
  #     #print("select a node")
  #     node = node.best_child()
  #   return node
  

  # def simulate(self, node):
  #     """
  #     Simulate a random playthrough from the given node.
  #     """
  #     current_state = node.state
  #     while not current_state.isGameOver():
  #         legal_actions = current_state.getLegalActions(self.index)
  #         action = random.choice(legal_actions)  # Randomly pick an action
  #         current_state = current_state.generateSuccessor(self.index, action)
  #     return self.evaluate_reward(current_state)


  # def evaluate_reward(self, gameState):
  #     return gameState.getScore()  # You can customize this depending on your agent's strategy
