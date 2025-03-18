from captureAgents import CaptureAgent
import random, time, util
from treeNode import TreeNode
from game import Directions
import game

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
    self.root = TreeNode(gameState)
    self.root.print_tree()
    print("root: ", self.root)
    print("root.state: ", self.root.state)

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
    


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    num_simulations = 5
    actions = gameState.getLegalActions(self.index)
    print(f"legal action: {actions}")
  
    '''
    You should change this in your own agent.
    '''
    # print(gameState)
    #self.state.process

    for _ in range(num_simulations):
      leaf = self.select(self.root) # TODO change to something smarter later
      print(f"leaf: {leaf}")
      print("simulating")

      print("leaf.is_terminal(): ", leaf.is_terminal())
    
      if not leaf.is_fully_expanded():
        print("are we here 2? ")
        self.expand(leaf)

      # Simulation
      reward = self.simulate(leaf)

      # Backpropagation
      self.backpropagate(leaf, reward)

    # After the simulations, select the best child (best action)
    best_child = self.root.best_child()
    print(f"Best action chosen: {best_child.action}")
    return best_child.action
    #print(f"chosen_action: {chosen_action}")
    #self.root.add_child(chosen_action) # make sure actions are legal and defined

    #return random.choice(actions)
  
  def select(self, node):
    #print("are we here?")
    while not node.is_terminal() and node.is_fully_expanded():
      #print("select a node")
      node = node.best_child()
    return node


  def expand(self, node):
    """
    Expand the node by choosing an untried action and creating a new child.
    """
    print("expanding tree")
    action = node.untried_actions.pop()
    print(f"action: {action}")
    new_state = node.state.generateSuccessor(self.index, action)  # Generate the next state
    print(f"new_state: {new_state}")
    child_node = TreeNode(new_state, parent=node, action=action)
    child_node.print_tree()
    print(f"child_node: {child_node}")
    node.add_child(child_node)



  def simulate(self, node):
      """
      Simulate a random playthrough from the given node.
      """
      current_state = node.state
      while not current_state.isGameOver():
          legal_actions = current_state.getLegalActions(self.index)
          action = random.choice(legal_actions)  # Randomly pick an action
          current_state = current_state.generateSuccessor(self.index, action)
      return self.evaluate_reward(current_state)

  def backpropagate(self, node, reward):
  
      while node is not None:
          node.update(reward)  # Update the node with the simulation result
          node = node.parent

  def evaluate_reward(self, gameState):
      return gameState.getScore()  # You can customize this depending on your agent's strategy
