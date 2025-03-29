
class Tree:
    def __init__(self, root=None, action = None):
        self.root = root
        self.relations_dict = {}
    
    def initialize_relations_dict(self):
        if self.root:
            self.relations_dict[self.root] = [] 
            
     
    def isLeaf(self, node):
        #print(f"Length of relations_dict: {self.relations_dict[node]}")
        if len(self.relations_dict.get(node, [])) == 0:
            return True
        else: 
            return False
        
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