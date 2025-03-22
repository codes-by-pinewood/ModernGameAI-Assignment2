from captureAgents import CaptureAgent
import random, time, util
from treeNode import Tree
from game import Directions
import game
import json

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
    #print("ROOT: \n")
    self.tree = Tree(root = gameState)
    #self.tree.print_tree()
    #print("tree: ", self.tree)


    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    # TODO call create graph
    #print(f"game_State:\n {gameState}")
    

    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
  '''
    def chooseAction(self, node):
      """
      Picks among actions randomly.
      """
      num_simulations = 5
      
      You should change this in your own agent.
      
      self.tree = Tree(root = node)
      self.tree.update_times_visited(node)
      root = node
      length_of_one_sim_path = 5 

      for _ in range(num_simulations):
        for _ in range(length_of_one_sim_path):
        #print(f"step {i} ")
          selected_action = random.choice(node.getLegalActions(self.index))
          child = node.generateSuccessor(self.index, selected_action)
          self.tree.update_visited_nodes(child)
          self.tree.create_relations(node, child, selected_action)
          #previous_node = node
          node = child
          root = node

      # HERE the simulation stops and the updates start
      #self.tree.update_visited_nodes(node)
      # Simulation
      food_heuristic = self.food_based_heuristic_reward(node)
      weight_heuristic = self.get_weights_food_based_heuristic()
      food_weighted = food_heuristic * weight_heuristic


      reward = self.getScore(node) + food_weighted 
      #print(f"reward {reward}")

      # Backpropagation
      #self.tree.backpropagate(reward)
      #print("self.reward_dict here: ", self.tree.reward_dict)
      updated_reward_dict = self.tree.new_propagate(reward, self.reward_dict)
      self.reward_dict = updated_reward_dict
      # After the simulations, select the best child (best action)
      best_action = self.tree.return_best_action(self.reward_dict)
      #print(f"best_action: {best_action}")

      child_node = root.generateSuccessor(self.index, best_action)

      # Store reward dict for later
      prev_reward_dict = self.tree.reward_dict

      # Update the tree root 
      self.tree.root = child_node
      self.tree.reward_dict = prev_reward_dict

      #print(f"Best action chosen: {best_action}")
      return best_action
    '''

  def chooseAction(self, node):
      """
      Picks among actions randomly.
      """
      root = node
      print("root at start of the chooseAction function: ", root)
      num_simulations = 5
      length_of_one_sim_path = 5
      simulation_rewards = {}  # Store rewards for root state of each simulation
      action_dict = {}

      best_root_reward = float('-inf')  # Track best root reward
      best_simulation_path = None       # Track best path

      
      for sim_idx in range(num_simulations):
          node = root  # Start each simulation from the original root
          simulation_path = []
          action_path = []
          simulation_path.append(node)

          for _ in range(length_of_one_sim_path):
              #simulation_path.append(node)
              selected_action = random.choice(node.getLegalActions(self.index))
              action_path.append(selected_action)
              child = node.generateSuccessor(self.index, selected_action)

              if child is None:
                  break

              self.tree.update_visited_nodes(child)
              self.tree.create_relations(node, child, selected_action)

              simulation_path.append(child)  # Track nodes in the path
              node = child  # Move to next state


          # Compute reward
          food_heuristic = self.food_based_heuristic_reward(node)
          weight_heuristic = self.get_weights_food_based_heuristic()
          food_weighted = food_heuristic * weight_heuristic
          reward = self.getScore(node) + food_weighted  

          # Backpropagate along this simulation path
          self.reward_dict = self.tree.new_new_propagate(reward, self.reward_dict, simulation_path)
          simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_path, "reward": reward, "action_path": action_path}
          #simulation_rewards[f"simulation_{sim_idx+1}"] = {"path": simulation_path, "reward": reward}

          #print(f"simulation_rewards after simulation {sim_idx+1}: ", simulation_rewards)


          #root_reward = self.reward_dict.get(root, float('-inf'))  # Default to -inf if not found
          #print(f"root_reward for simulation {sim_idx+1}: ", root_reward)


          #print(f"root: {root}")
          # Store reward for the root state of this simulation
          
      # Store reward dict for later
      max_reward = float('-inf')
      for sim_idx, sim_data in simulation_rewards.items():
        if sim_data["reward"] > max_reward:
            max_reward = sim_data["reward"]
            best_simulation = sim_data  # Get the path and actions for this simulation

      if best_simulation:
          print(f"Best simulation: Path: {best_simulation['path']} | Reward: {best_simulation['reward']} | Action Path: {best_simulation['action_path']}")
          best_action = best_simulation["action_path"][0]  # Take the first action in the best action path
      else:
          best_action = random.choice(root.getLegalActions(self.index))  # Fallback if no good simulation

      print("best_action: ", best_action)
      prev_reward_dict = self.tree.reward_dict

      # Update the tree root 
      child_node = root.generateSuccessor(self.index, best_action)

      prev_reward_dict = self.tree.reward_dict
 
      self.tree.root = child_node
      self.tree.reward_dict = prev_reward_dict

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
  

  def get_weights_food_based_heuristic(self):
    return {'successorScore': 100, 'distanceToFood': -1}
  


  



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
