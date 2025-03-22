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
               first = 'HeuristicAgent', second = 'HeuristicAgent'):
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



class HeuristicAgent(CaptureAgent):
  
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    print(f"self.start: {self.start}")
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    best_score = 1_000_000
    best_action = random.choice(actions)
    for action in actions:
      action_score = self.evaluate_action(gameState, action)
      if action_score < best_score:
        best_score = action_score
        best_action = action
      

    return best_action

  def evaluate_action(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    current_food_list = self.getFood(gameState).asList()
    foodList = self.getFood(successor).asList()  
    myPos = successor.getAgentState(self.index).getPosition()
    # food = self.getFood(successor).asList()
    # distance_to_food = []
    distance_opponents = []
    # self.distancer.getDistance(p1, p2)
    # print(food[0])

    # features = util.Counter()
    food_eaten = len(current_food_list) > len(foodList)

    if len(foodList) > 0:
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    else:
        minDistance = 0 

    if food_eaten:
        food_reward = -100  # Large reward for eating food
    else:
        food_reward = 0

    opponent_indices = self.getOpponents(successor)

    for opponent in opponent_indices:
      oppPos = successor.getAgentPosition(opponent)
      distance_opponents.append(self.getMazeDistance(myPos, oppPos))
    
    minDistanceOpponents = min(distance_opponents)


    score = minDistance + len(foodList) + food_reward
    
    if minDistanceOpponents < 3:
        score += 50 
    # print(minDistanceOpponents)
    # print(minDistance)
    # print(self.getScore(successor))
    # score = minDistance + len(foodList)#+ maxDistance #+ 1/minDistanceOpponents
    # print(score)
    # print(features)
    return score

  