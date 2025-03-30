import math 

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

    def correct_backprop(self, node, reward, global_reward_dict):
        visited = set()
        while node is not None and node not in visited:
            visited.add(node)
            if node not in global_reward_dict:
                global_reward_dict[node] = 0
            global_reward_dict[node] += reward
            node = self.find_parent(node)
                 
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
        for key, val in self.relations.items():
            for child, _ in val: 
                if child == node:
                    parent = key

        total_reward = 0
        for sim_node in simulation_path:
            total_reward += global_reward_dict[sim_node]

        avg_reward = total_reward / len(simulation_path)

        if node == self.root:
            return avg_reward

        return avg_reward + explore * math.sqrt(2 * math.log(self.tree.times_visited[parent]) / self.tree.times_visited[node])
