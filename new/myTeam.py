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
               first = 'OffenseMCTSAgent', second = 'DefenseMCTSAgent'):
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
  #print("firstIndex: ", firstIndex)
  #print("secondIndex: ", secondIndex)
  #print("eval(first)(firstIndex): ", eval(first)(firstIndex))
  #print("eval(second)(secondIndex): ", eval(second)(secondIndex))

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
    if self.root not in self.global_reward_dict:  
      self.global_reward_dict[self.root] = 0
  

  def update_global_reward_dict(self, node, reward):
    self.global_reward_dict[node] = reward


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
    print("ROOT: \n")
    self.tree = Tree(root = gameState)
    self.tree.print_tree()
    print("tree: ", self.tree)
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
    # self.tree.update_visited_nodes(root)

    # Choose number of simulations and their length
    num_simulations = 5
    length_of_one_sim_path = 5

    # For each simulation, dict: key-simulation path, vale-reward; list: all simulations' paths
    simulation_rewards = {} 
    simulation_paths = []

    for sim_idx in range(num_simulations):
        print(f"sim number {sim_idx + 1}")
        # Start each simulation from the original root
        node = root  
          
        # Create simulation_path and action_path to store explored states and action for current simulation
        simulation_path = []
        action_path = []

        # Append root NOT NECESSARY FOR LOGIC
        # simulation_path.append(node)

        for _ in range(length_of_one_sim_path):
            # Step
            # selected_action = random.choice(node.getLegalActions(self.index))
            selected_action = self.select_uct_action(node)
            # selected_action = select_uct_action
            child = node.generateSuccessor(self.index, selected_action)

            # Update
            self.tree.update_visited_nodes(child)
            self.tree.create_relations(node, child, selected_action)

            # Append
            simulation_path.append(child)
            action_path.append(selected_action)

            # Move to next state
            node = child  

            if node not in self.global_reward_dict:
               self.global_reward_dict[node] = 0
            
        # Append the whole path
        simulation_paths.append(simulation_path)

    # After ALL simulation are done, update the reward
    for i in range(len(simulation_paths)):
      leaf_of_simulation = simulation_paths[i][-1]
      print(type(leaf_of_simulation))
        
      # Compute reward
      reward = self.getScore(leaf_of_simulation) + self.evaluate_state_reward(leaf_of_simulation)  
      print(f"reward {reward}")
      
      # Backpropagate along this simulation path
      # self.global_reward_dict = self.tree.back_propagate(uct_reward, reward, self.global_reward_dict, simulation_paths[i])
      self.tree.correct_backprop(leaf_of_simulation, reward, self.global_reward_dict)

      simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_paths[i], "reward": reward, "action_path": action_path}

        
    # Store reward dict for later
    max_reward = float('-inf')
    for sim_idx, sim_data in simulation_rewards.items():
      if sim_data["reward"] > max_reward:
          max_reward = sim_data["reward"]
          best_simulation = sim_data  # Get the path and actions for this simulation

    # if best_simulation:
    print(f"Best simulation: Path: {best_simulation['path']} | Reward: {best_simulation['reward']} | Action Path: {best_simulation['action_path']}")
    best_action = best_simulation["action_path"][0]  # Take the first action in the best action path
    # else:
        # best_action = random.choice(root.getLegalActions(self.index))  # Fallback if no good simulation

    print("best_action: ", best_action)

    # Update the tree root 
    child_node = root.generateSuccessor(self.index, best_action)
    self.visited_gamestates.append(child_node)
    
    self.tree.root = child_node
    self.tree.visited_nodes = []

    return best_action
  
  # def uct_select(self, node):
  #   best_score = float('-inf')
  #   best_child = None
  #   for child, action in self.tree.relations[node].items():
  #       if child.visits == 0:
  #           return child
  #       avg_reward = child.total_reward / child.visits
  #       exploration = math.sqrt(math.log(node.visits) / child.visits)
  #       uct_score = avg_reward + self.C * exploration
  #       if uct_score > best_score:
  #           best_score = uct_score
  #           best_child = child
  #   return best_child
  def select_uct_action(self, node, explore=1.4):
      """
      Select the best action from this node using UCT.

      Args:
          node: The current gameState node.
          explore: Exploration constant. Higher values favor less visited nodes.

      Returns:
          action (Direction): The best action based on UCT value.
      """
      if node not in self.tree.relations:
          return random.choice(node.getLegalActions(self.index))  # No children, fallback

      best_score = float('-inf')
      best_action = None

      parent_visits = self.tree.times_visited.get(node, 1)

      for child, action in self.tree.relations[node]:
          child_visits = self.tree.times_visited.get(child, 0)
          total_reward = self.global_reward_dict.get(child, 0)

          if child_visits == 0:
              return action  # Try unvisited node immediately

          avg_reward = total_reward / child_visits
          uct_score = avg_reward + explore * math.sqrt(math.log(parent_visits) / child_visits)

          if uct_score > best_score:
              best_score = uct_score
              best_action = action

      return best_action if best_action is not None else random.choice(node.getLegalActions(self.index))


  
class OffenseMCTSAgent(MCTSAgent):
  """
  An MCTS agent that seeks food.
  """

  def evaluate_state_reward(self, successor):
    print("Offense evaluate state reward")
    features = self.food_based_heuristic_reward(successor)
    weights = self.get_weights_offense()
    reward = features * weights
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
    return features
  

  def get_weights_offense(self):
    '''
    heuristic based on offensive strategy: getting more food. 
    '''
    return {'successorScore': 100, 'distanceToFood': -1}

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
