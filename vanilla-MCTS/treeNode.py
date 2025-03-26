

import math 
import random



class Tree:
    def __init__(self, root=None, action=None):
        self.relations = {}
        self.root = root
        self.visit_count = {}
        self.visited_nodes = []
        self.visited_nodes_in_sim_dict = {}
        self.reward_dict = {}
        self.times_visited = {}
     
        self.initialize_reward_dict()
    
    def update_times_visited(self, node):
        if node not in self.times_visited:
            self.times_visited[node] = 0
        self.times_visited[node] += 1

    
    def return_best_action(self, reward_dict, simulation_path):
        #for key, value in reward_dict.items():
            #print(f"Key: {key}, Value type: {type(value)}")

        #print(f"rewards_dict HERE: {reward_dict}")
        parent = simulation_path[0]
        print(f"parent: {parent}")
        
        best_child = simulation_path[1]
        #print(f"best_child: {best_child}")

        #max_state = max(reward_dict, key=reward_dict.get)
        #print(f"max_state: {max_state}")
        #print("State with max reward:", max_state)

        """
        This function:
            - returns best action
            - empties tried action reward dictionary, as the root changes
            - re-initialize tried actions
        """
        """
        CURRENT ISSUE:
        We cannot isolate the best action to take after the simulation. Return illegal actions or None
        """
        '''
        roots_relations = [(child, action) for child, action in self.relations.get(self.root, [])]
        roots_children = [t[0] for t in roots_relations]

        # Get best child based on current reward values in reward_dict
        best_child = max(
            (k for k in roots_children if k in reward_dict),
            key=self.reward_dict.get,
            default=None
        )'
        '''
        roots_relations = [(child, action) for child, action in self.relations.get(self.root, [])]
        #print(f"root_relations: {roots_relations}")
        roots_children = [t[0] for t in roots_relations]


        # Return the action that leads to the best child
        for child, action in roots_relations:
            #print(f"child: {child}")
            #print(f"action: {action}")
            #if (child == max_state):
            #  print(f"best action is: {action}")
            #print(f"str(child): {str(child)}")
            #print(f"str(max_state): {str(max_state)}")
            #print("child here", child)
            #print("max_state", max_state)

            if vars(child) == vars(best_child):
                #print("The two states are identical.")
                print(f"best action: {action}")
                return action 
            else:
                #print("The two states are different.")
              
                return None

            '''

            if str(child).strip() == str(max_state).strip():
                print(f"best action is: {action}")
                return action
            else: 
                print("no best action found")
                print(f"child not matching: {child}")
                print(f"max_state not matching: {max_state}")

                print("Child repr:", repr(str(child)))  
                print("Max State repr:", repr(str(max_state)))

                return None
            '''





    def initialize_reward_dict(self):
        if self.root not in self.reward_dict:  # Only initialize if it's not already in the dictionary
            self.reward_dict[self.root] = 0

    def create_relations(self, parent, child, action):
        """
        Expand the tree by:
            - add a child to the parent from which it was explored
            - remove the taken action from unexplored parent actions
            - add all legal actions to the created child
        """
        if parent not in self.relations:
            #print(f"parent: {parent}")
            #print(f"child: {child}")
            #print(f"type of child: {type(child)}")
            self.relations[parent] = [(child, action)]
            
        else:
            self.relations[parent].append((child, action))

                         
    def print_tree(self):
        print("printing tree\n")
        print(f"root of the tree: {self.root}")
        print(f"tree from root: {self.relations}")

    def update_visited_nodes(self, child):
        self.visited_nodes.append(child)
        self.update_times_visited(child)

    def backpropagate(self, reward, reward_dict):
        #print(f"reward dict before", self.reward_dict)
        num_states = len(self.visited_nodes)
        #print(f"num_states: {num_states}")
        for node in self.visited_nodes:
            
        
            #print("type of reward dict keys", type(self.reward_dict.keys()))
            
            if node not in reward_dict.keys():
                #print("are we getting stuck here?")
                self.reward_dict[node] = 0

            initial_reward = self.reward_dict[node]
            
            self.reward_dict[node] += (1 / num_states) * (reward - initial_reward) 


        #print(f"reward dict after", self.reward_dict)
    
    def new_new_propagate(self, reward, reward_dict, simulation_path):
        """
        Backpropagate reward along a specific simulation path.

        Args:
            reward (float): The final reward obtained from the simulation.
            reward_dict (dict): The dictionary storing rewards for each node.
            simulation_path (list): The ordered list of nodes visited in this simulation.

        Returns:
            dict: Updated reward dictionary.

        """
        
        #print(f"reward before: {reward}")
        num_states = len(simulation_path) - 1
        print(num_states)
        if num_states == 0:
            return reward_dict  # No nodes to update

        decay_factor = 0.1  # Controls how much the reward decreases as it moves up the path

        # Process root separately to ensure it's correctly updated
        root_node = simulation_path[0]
        if root_node not in reward_dict:
            reward_dict[root_node] = 0  # Initialize if not present
        reward_dict[root_node] += reward  # Give full reward to root first

        # Backpropagate with decay
        for i, node in enumerate(reversed(simulation_path[1:])):  # Exclude root
            if node not in reward_dict:
                reward_dict[node] = 0
            if node not in self.visit_count:
                self.visit_count[node] = 0

            self.visit_count[node] += 1 

            initial_reward = reward_dict[node]
            visit_count = self.visit_count[node]
            new_reward = (initial_reward + reward)/visit_count
            #discounted_reward *= discount_factor
            discounted_reward = reward * decay_factor  # Start decay from 1
            reward_dict[node] += (1 / num_states) * (discounted_reward - initial_reward)
            print(f"reward after: {reward_dict[node]}")
        return reward_dict


    


   
    def new_propagate(self, reward, reward_dict):

        num_states = len(self.visited_nodes)
        for node in self.visited_nodes:
            if node not in reward_dict.keys():
                #print("are we getting stuck here?")
                reward_dict[node] = 0

            initial_reward = reward_dict[node]
            
            reward_dict[node] += (1 / num_states) * (reward - initial_reward) 

        return reward_dict


        #print(f"reward dict after", self.reward_dict)


    def empty_visited_nodes(self):
        self.visited_nodes = []


    def value(self, node, explore = 0.5):
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to 0.5.

        """
        # if the node is not visited, set the value as infinity. Nodes with no visits are on priority
        # (lambda: print("a"), lambda: print("b"))[test==true]()
        
        parent = node.getPreviousObservation()
        avg_reward = self.reward_dict[node]
        #print("avg_reward", avg_reward)

        if self.times_visited[node] == 0:
            return 0 if explore == 0 else -1
        else:
            return avg_reward / self.times_visited[node] + explore * math.sqrt(2 * math.log(self.times_visited[parent]) / self.times_visited[node])
