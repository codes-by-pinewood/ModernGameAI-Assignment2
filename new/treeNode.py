'''
class TreeNode:
    def __init__(self, gameState):
        self.gameState = gameState
        self.addchild = 
        self.findObjects = gameState.findObjects
        self.children = []

    def find_o_positions(self, gameState):
        positions = []
        for y, row in enumerate(gameState):
            for x, char in enumerate(row):
                if char == 'o':
                    positions.append((x, y))
        return positions
    

    def find_g_positions(self, gameState):
        positions = []
        for y, row in enumerate(gameState):
            for x, char in enumerate(row):
                if char == 'G':
                    positions.append((x, y))
        return positions



    def add_child(self, child):
        if child == "North":
            self.children.append(child)
        elif child == "South":
            self.children.append(child)
        elif child == "East":
            self.children.append(child)
        elif child == "West":
            self.children.append(child)
        else:
            print("Invalid move")

    def print_tree(self, level=0):
        print(" " * (level * 4) + str(self.value))
        for child in self.children:
            child.print_tree(level + 1)

root = TreeNode("Root Game State")
child1 = TreeNode("Child 1 Game State")
child2 = TreeNode("Child 2 Game State")
child1_1 = TreeNode("Child 1.1 Game State")

#root.add_child(child1)
#root.add_child(child2)
#child1.add_child(child1_1)

#root.print_tree()

def find_o_positions(grid):
    positions = []
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char == 'o':
                positions.append((x, y))
    return positions

# The given pattern (represented as a list of strings)
grid = [
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
    "%   %. %.%.%       %     %.%.%G%",
    "% % %%       %%  %   %%%   %.%G%",
    "% % %. % %%%    %%%% .%..% % % %",
    "% % %% % ..% %   %   %%%%% % % %",
    "% %    %%%%% %%%   %%%.% o % % %",
    "% %% % ..%.  %.%%%       %   % %",
    "% %. %%.%%%%        %.%%%%  %% %",
    "% %%  %%%%.%        %%%%.%% .% %",
    "% %   %       %%%.%  .%.. % %% %",
    "% % % o %.%%%   %%% %%%%%    % %",
    "% % % %%%%%   %   % %.. % %% % %",
    "% % % %..%. %%%%    %%% % .% % %",
    "%G%.%   %%%   %  %%       %% % %",
    "%G%.%.%     %       %.%.% .%   %",
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
]

# Find the positions of "o"
positions = find_o_positions(grid)

# Print the positions
print(positions)
'''
'''

class TreeNode:
    def __init__(self, gameState):
        self.gameState = gameState
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def find_o_positions(self):
        positions = []
        for y, row in enumerate(self.gameState):  # Access gameState directly from the instance
            for x, char in enumerate(row):
                if char == 'o':
                    positions.append((x, y))
        return positions

    def print_tree(self, level=0):
        print(" " * (level * 4) + str(self.gameState))  # Assuming you want to print the gameState
        for child in self.children:
            child.print_tree(level + 1)

# Example of usage


root = TreeNode(game_state)
child = TreeNode(game_state)  # In practice, you'd likely have different game states
root.add_child(child)

# Find positions of "o" in root's gameState
o_positions = root.find_o_positions()
print("Positions of 'o':", o_positions)

# Print the tree
root.print_tree()
'''
'''
# x is the number of columns, y is the number of rows
# The top-left corner is (0,0)
class TreeNode:
    def __init__(self, gameState):
        self.gameState = gameState  # Store the entire game state (Pac-Man position, ghosts, etc.)
        self.number_of_moves_made = 0
        self.initial_score = 0 
        self.graph = self.find_graph(gameState)
        #self.food = self.find_f_positions(gameState)

        self.current_o_position = self.find_positions(gameState, "O")  # Store the current position of "o"
        self.current_food_position = self.find_positions(gameState, ".")  # Store the current position of "o"
        self.current_ghost_positions = self.find_positions(gameState, "G")  # Store the positions of "G"
        self.current_pacman_positions = self.find_positions(gameState, "^<>v")  # Store the positions of "^", "<", ">", "v"
        self.children = []  # Store the children of the current node

    def add_child(self, chosen_action):
        self.number_of_moves_made += 1
        #print(f"current object {self.current_object_position}")
        print("object has been moved")
        #print(f"chosen_action is {chosen_action}")
        if chosen_action == "North":
            print("are we here")
            print("curent object position at 00", self.current_object_position[0][0])
            child_position = (self.current_object_position[0][0], self.current_object_position[0][1] - 1)
            #print(f"new position is {new_position}")
        elif chosen_action == "South":
            child_position = (self.current_object_position[0][0], self.current_object_position[0][1] + 1)
        elif chosen_action == "East":
            child_position = (self.current_object_position[0][0] + 1, self.current_object_position[0][1])
        elif chosen_action == "West":
            child_position = (self.current_object_position[0][0] - 1, self.current_object_position[0][1])
        else:
            print("Invalid move")
    

    def find_graph(self, gameState):
        self.current_o_position = self.find_positions(gameState, "o")  # Store the current position of "o
        self.current_food_positions = self.find_positions(gameState, ".")  # Store the positions of "G"
        self.current_ghost_positions = self.find_positions(gameState, "G")  # Store the positions of "G"
        self.current_pacman_positions = self.find_positions(gameState, "^<>v")
        print(self.current_pacman_positions)
        print(self.current_ghost_positions)
        print(self.current_food_positions)
        print(self.current_o_position)


    def find_positions(self, gameState, finding):
        print("am here")
        print(f"type of game state {type(gameState)}")
        gameStateString = str(gameState)
        positions = []
        if len(finding) > 1:
            for y, row in enumerate(gameStateString):
                for x, char in enumerate(row):
                    for i in range(len(finding)):
                        if char == finding[i]:
                            positions.append((x, y))
        else:
             for y, row in enumerate(gameStateString):
                for x, char in enumerate(row):
                        if char == finding:
                            positions.append((x, y))
        print("did this work")
        return positions
    
    

    def find_g_positions(self, gameState):
        positions = []
        for y, row in enumerate(gameState):
            for x, char in enumerate(row):
                if char == 'G':
                    positions.append((x, y))
        return positions

    def print_tree(self, level=0):
        print("printing treex")
        print(" " * (level * 4) + str(self.gameState))
        for child in self.children:
            child.print_tree(level + 1)

game_state = [
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
    "%   %. %.%.%       %     %.%.%G%",
    "% % %%       %%  %   %%%   %.%G%",
    "% % %. % %%%    %%%% .%..% % % %",
    "% % %% % ..% %   %   %%%%% % % %",
    "% %    %%%%% %%%   %%%.% o % % %",
    "% %% % ..%.  %.%%%       %   % %",
    "% %. %%.%%%%        %.%%%%  %% %",
    "% %%  %%%%.%        %%%%.%% .% %",
    "% %   %       %%%.%  .%.. % %% %",
    "% % % o %.%%%   %%% %%%%%    % %",
    "% % % %%%%%   %   % %.. % %% % %",
    "% % % %..%. %%%%    %%% % .% % %",
    "%G%.%   %%%   %  %%       %% % %",
    "%G%.%.%     %       %.%.% .%   %",
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
]
'''
'''
print("does this work")
root = TreeNode(game_state)
print("does this work")
root.find_graph(game_state)
print(root.current_o_position)
print(root.current_ghost_positions)
print(root.current_pacman_positions)
print(root.current_food_positions)
#root.add_child("North", TreeNode(game_state))
#root.print_tree()
#print(root.food)'
'''

import math 

class TreeNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.legal_actions = state.getLegalActions()
        self.action = action
        self.children = []
        #self.leaf = state.select()
        self.visits = 0
        self.reward = 0
        self.untried_actions = state.getLegalActions()  # All legal actions

    def select(self):
        print(f"self.legal_actions : {self.legal_actions}")
        self.random.choice(self.legal_actions)

    def add_child(self, child_node):
        self.children.append(child_node)

    def best_child(self):
        # Use UCT formula to select the best child (maximize reward and visits)
        best_value = float('-inf')
        best_node = None
        for child in self.children:
            uct_value = child.reward / (child.visits + 1) + 2 * (2 * math.log(self.visits + 1) / (child.visits + 1))**0.5
            if uct_value > best_value:
                best_value = uct_value
                best_node = child
        return best_node

    def update(self, reward):
        # Update the node's statistics after a simulation
        self.visits += 1
        self.reward += reward

    def is_terminal(self):
        return True
        # Check if the node is terminal (game over or no more legal actions)
        #print("self.state: " + str(self.state))
        #return self.state.isGameOver()

    def is_fully_expanded(self):
        if (len(self.untried_actions) == 0):
            return True

    def has_child(self, action):
        return any(child.action == action for child in self.children)

'''

game_state = [
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
    "%   %. %.%.%       %     %.%.%G%",
    "% % %%       %%  %   %%%   %.%G%",
    "% % %. % %%%    %%%% .%..% % % %",
    "% % %% % ..% %   %   %%%%% % % %",
    "% %    %%%%% %%%   %%%.% o % % %",
    "% %% % ..%.  %.%%%       %   % %",
    "% %. %%.%%%%        %.%%%%  %% %",
    "% %%  %%%%.%        %%%%.%% .% %",
    "% %   %       %%%.%  .%.. % %% %",
    "% % % o %.%%%   %%% %%%%%    % %",
    "% % % %%%%%   %   % %.. % %% % %",
    "% % % %..%. %%%%    %%% % .% % %",
    "%G%.%   %%%   %  %%       %% % %",
    "%G%.%.%     %       %.%.% .%   %",
    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
]

print("does this work")
root = TreeNode(game_state)
print("does this work")
root.find_graph(game_state)
print(root.current_o_position)
print(root.current_ghost_positions)
print(root.current_pacman_positions)
print(root.current_food_positions)
#root.add_child("North", TreeNode(game_state))
#root.print_tree()
#print(root.food)'
'''