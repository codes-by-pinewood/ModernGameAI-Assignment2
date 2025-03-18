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
import random

class Tree:
    def __init__(self, root=None, action=None):
        self.relations = {}
        # self.untried_actions_dict = {}  
        self.root = root
        self.visited_nodes = []
        self.reward_dict = {}
        # self.tried_actions_reward_dict = {}

        # self.initialize_untrained_actions()
        self.initialize_reward_dict()
        # self.initialize_tried_actions_reward_dict()
    
    def return_best_action(self):
        """
        This function:
            - returns best action
            - empties tried action reward dictionary, as the root changes
            - re-initializetried actions
        """
        """
        CURRENT ISSUE:
        We cannot isolate the best action to take after the simulation. Return illigal actions or None
        """
        # roots_children = self.relations.get(self.root)
        roots_children = [child for child, action in self.relations[self.root]]

        print(f"roots_children: {roots_children}")

        best_child = max(roots_children, key=lambda roots_children: self.reward_dict.get(roots_children, float('-inf')))

        # best_child = max(self.reward_dict, key=lambda k: roots_children)
        print(f"best child {best_child}")
        for child in roots_children:
            if stored_child == best_child:
                return action 

    # def initialize_tried_actions_reward_dict(self):
    #     keys = self.root.getLegalActions()  
    #     self.tried_actions_reward_dict = dict.fromkeys(keys, 0)

    # def initialize_untrained_actions(self):
    #     self.untried_actions_dict[self.root] = self.root.getLegalActions()   

    def initialize_reward_dict(self):
        self.reward_dict[self.root] = 0
    
    def create_relations(self, parent, child, action):
        """
        Expand the tree by:
            - add a child to the parent from which it was explored
            - remove the taken action from unexplored parent actions
            - add all legal actions to the created child
        """
        if parent not in self.relations:
            self.relations[parent] = [(child, action)]
        else:
            self.relations[parent].append((child, action))
        print("RELATIONS CREATED")
        print(self.relations[parent])
        
        # Remove the just tried action
        # self.untried_actions_dict[parent].remove(action)

        # Fill in the legal actions of the child
        # self.untried_actions_dict[child] = child.getLegalActions()
        
                         
    def print_tree(self):
        print("printing tree\n")
        print(f"root of the tree: {self.root}")
        print(f"tree from root: {self.relations}")
        # print(f"children: {self.children}")
        #print(f"untried_actions: {self.untried_actions}")

    def select(self):
        print(f"self.legal_actions : {self.legal_actions}")
        self.random.choice(self.legal_actions)
        
    def get_random_child(self, node):
        print(f"self.relations[node]: {self.relations[node]}")
        return random.choice([self.relations[node]])
    
            
    def add_child(self, child_node):
        self.children.append(child_node)
        print("updating children")
        print(f"self.children: {self.children}")

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
        #print(f"self.gameState: {self.state}")
        #print(f"self.game.gameOver: {self.game.gameOver}")
        #return self.game.gameOver

    # def is_fully_expanded(self, node):
    #     return (len(self.untried_actions_dict.get(node, [])) == 0)


    def has_child(self, action):
        return any(child.action == action for child in self.children)

    def update_visited_nodes(self, child):
        self.visited_nodes.append(child)

    def backpropagate(self, reward):
        num_states = len(self.visited_nodes)

        for node in self.visited_nodes:
            if node not in self.reward_dict.keys():
                self.reward_dict[node] = 0

            initial_reward = self.reward_dict[node]
            self.reward_dict[node] += (1 / num_states) * (reward - initial_reward) 
        #self.tried_actions_reward_dict = {}

        self.visited_nodes = []

        # self.update_tried_actions_reward_dict()

    # def update_tried_actions_reward_dict(self):
    #     roots_children = self.relations[self.root].items()


