import math 
import random

class Tree:
    def __init__(self, root=None, action=None):
        self.relations = {}
        self.root = root
        self.visited_nodes = []
        self.times_visited = {}
        self.child_to_parent = {}
        self.relations_dict = {}
    

    def update_times_visited(self, node):
        if node not in self.times_visited:
            self.times_visited[node] = 0
        self.times_visited[node] += 1


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
            if (child, action) not in self.relations[parent]:
                self.relations[parent].append((child, action))

        self.child_to_parent[child] = parent
        if self.root:
            self.relations_dict[self.root] = [] 

    def update_relations_dict(self, parent, child):
        if parent in self.relations_dict:
            self.relations_dict[parent].append(child)
        else: 
            self.relations_dict[parent] = [child]

    def find_parent(self, child):
        # print(self.relations_dict)
        for parent, children in self.relations_dict.items():
            if child in children:
                return parent
        return None 


                         
    def print_tree(self):
        print("printing tree\n")
        print(f"root of the tree: {self.root}")
        print(f"tree from root: {self.relations}")

    def update_visited_nodes(self, child):
        self.visited_nodes.append(child)
        self.update_times_visited(child)

    
    # def back_propagate(self, uct_reward, reward, reward_dict, simulation_path):
    #     """
    #     Backpropagate reward along a specific simulation path.

    #     Args:
    #         reward (float): The final reward obtained from the simulation.
    #         reward_dict (dict): The dictionary storing rewards for each node.
    #         simulation_path (list): The ordered list of nodes visited in this simulation.

    #     Returns:
    #         dict: Updated reward dictionary.
    #     """
    #     num_states = len(simulation_path)
    #     print(num_states)
    #     if num_states == 0:
    #         return reward_dict  # No nodes to update

    #     #decay_factor = 0.9  # Controls how much the reward decreases as it moves up the path

    #     # # Process root separately to ensure it's correctly updated
    #     # root_node = simulation_path[0]
    #     # if root_node not in reward_dict:
    #     #   reward_dict[root_node] = 0  # Initialize if not present
    #     # reward_dict[root_node] += reward  # Give full reward to root first

    #     # Backpropagate with a discount/decay factor
    #     for _, node in enumerate(reversed(simulation_path[1:])):  # Exclude root
    #         # if node not in reward_dict:
    #         #     reward_dict[node] = 0

    #         #initial_reward = reward_dict[node]
             
    #         #discounted_reward = reward * (decay_factor ** (i + 1))  # Start decay from 1
    #         # reward_dict[node]  += (1 / num_states) * (discount_reward - initial_reward)
    #         reward_dict[node] += uct_reward + reward

    #     return reward_dict
    
    # def correct_backprop(self, node, reward, global_reward_dict):
    #     while node is not None:
    #         global_reward_dict[node] += reward
    #         node = self.find_parent(node)
    #         if node == self.root:
    #             break
    def correct_backprop(self, node, reward, global_reward_dict):
        visited = set()
        while node is not None and node not in visited:
            visited.add(node)
            if node not in global_reward_dict:
                global_reward_dict[node] = 0
            global_reward_dict[node] += reward
            node = self.find_parent(node)
        

    # def find_parent(self, node):
    #     for key, val in self.relations.items():
    #         for child, _ in val:  
    #             if child == node:
    #                 return key
                
    def find_parent(self, node):
        return self.child_to_parent.get(node, None)

    def value(self, node, simulation_path, global_reward_dict, explore = 0.5):
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to 0.5.

        """
        # parent = self.getPreviousObservation()
        for key, val in self.relations.items():
            for child, _ in val:  # Unpack the tuple
                if child == node:
                    parent = key

        total_reward = 0
        for sim_node in simulation_path:
            total_reward += global_reward_dict[sim_node]

        avg_reward = total_reward / len(simulation_path)

        if node == self.root:
            return avg_reward

        # if self.tree.times_visited[node] == 0:
        #     return 0 if explore == 0 else -1
        # else:
            # return avg_reward / self.tree.times_visited[node] + explore * math.sqrt(2 * math.log(self.tree.times_visited[parent]) / self.tree.times_visited[node])
        return avg_reward + explore * math.sqrt(2 * math.log(self.tree.times_visited[parent]) / self.tree.times_visited[node])

    # def uct_select(self, node, agent_index, C=1.4):
    #     """
    #     Selects the best child node using UCT.
    #     """
    #     if node not in self.relations:
    #         return None  # No children yet

    #     best_score = float('-inf')
    #     best_child = None
    #     parent_visits = self.visits.get(node, 1)

    #     for child in self.relations[node]:
    #         child_visits = self.visits.get(child, 0)
    #         if child_visits == 0:
    #             return child  # Try unvisited node immediately

    #         avg_reward = self.total_reward.get(child, 0) / child_visits
    #         uct_score = avg_reward + C * math.sqrt(math.log(parent_visits) / child_visits)

    #         if uct_score > best_score:
    #             best_score = uct_score
    #             best_child = child

    #     return best_child