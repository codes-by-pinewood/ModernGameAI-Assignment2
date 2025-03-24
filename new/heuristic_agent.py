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
               first = 'HeuristicAgent', second = 'DefenceHeuristiAgent'):
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
    

  def evaluate_action(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    food_reward = self.get_food_reward(myPos, gameState, successor)
    capsule_reward = self.get_capsule_reward(gameState, successor)
    ghost_positions = self.get_opponent_distances(myPos, successor)
    score = 0

    isPowered = myState.scaredTimer > 0
    enemy_score = self.get_enemy_score(isPowered, ghost_positions)
    carrying_food = myState.numCarrying > 0


    current_is_pacman = gameState.getAgentState(self.index).isPacman
    successor_is_pacman = myState.isPacman
    crossing_home = current_is_pacman and not successor_is_pacman

    if successor_is_pacman:
        mid_x = gameState.getWalls().width // 2
        if self.red:
            mid_x = mid_x - 1  
        else:
            mid_x = mid_x  
        
        boundary_y = [y for y in range(gameState.getWalls().height) 
                    if not gameState.hasWall(mid_x, y)]
        
        # Calculate distances to boundary positions
        boundary_distances = [self.getMazeDistance(myPos, (mid_x, y)) 
                            for y in boundary_y]
        # Distance to closest boundary point
        distance_to_boundary = min(boundary_distances) if boundary_distances else 0
    else:
        distance_to_boundary = 0

    if carrying_food:
        # HUGE reward for actually crossing the boundary
        if crossing_home:
            return -5000 
        
        # Check if opponents are close and we should return
        dangerous_ghost_nearby = any(dist < 10 and not scared 
                                 for _, dist, scared in ghost_positions)
        
        if dangerous_ghost_nearby or myState.numCarrying > 3:  # Lowered threshold to return sooner
            # Strongly prioritize returning to our side
            score = -distance_to_boundary * 10  # Increased weight
            
            # If close to our side, make it even more appealing
            if distance_to_boundary <= 2:
                score -= 500  # Much higher reward for being very close to boundary

    reward = food_reward + capsule_reward + enemy_score + score
    return reward
  

  

class DefenceHeuristiAgent(HeuristicAgent):

  def chooseAction(self, gameState):
     return super().chooseAction(gameState)
  
  def evaluate_action(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    current_enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    current_invaders = [a for a in current_enemies if a.isPacman and a.getPosition() != None]
    
    successor_enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    successor_invaders = [a for a in successor_enemies if a.isPacman and a.getPosition() != None]

    invader_captured = len(current_invaders) > len(successor_invaders)

    if not myState.isPacman:
        # Find invaders in our territory
        invaders = [a for a in successor_enemies if a.isPacman and a.getPosition() != None]
        
        if invader_captured:
            # Strong reward for eating an invader
            return -1000
        elif len(invaders) > 0:
            # Chase closest invader
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            return min(dists)
        else:
            # No visible invaders, prioritize defending capsules
            capsules = self.getCapsulesYouAreDefending(successor)
            if len(capsules) > 0:
                capsule_distances = [self.getMazeDistance(myPos, capsule) for capsule in capsules]
                closest_capsule_dist = min(capsule_distances)
                return closest_capsule_dist + 20  
            else:
                # If no capsules or all capsules are gone, patrol near food
                food_defending = self.getFoodYouAreDefending(successor).asList()
                if len(food_defending) > 0:
                    food_distances = [self.getMazeDistance(myPos, food) for food in food_defending]
                    closest_food_dist = min(food_distances)
                    return closest_food_dist + 50  # Lower priority than capsules
                else:
                    return len(self.getFoodYouAreDefending(gameState).asList())
    else:
        # Penalty for leaving our territory
        return 500
    
    return 100
  
  def evaluate_opponents_action(self, opponent):
     pass
     

  