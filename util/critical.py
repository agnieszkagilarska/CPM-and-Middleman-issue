class CriticalPath:
    def __init__(self):
        self.nodes = set()  # Set of nodes
        self.edges = {}  # Dictionary of sets dict{ <source_label>: set{<target_label>, ...}, ...}
        self.edge_weights = {}  # Dictionary of edge weights {(<source_label>, <target_label>): <weight>, ...}
        self.rev_edges = {}  # Dictionary of sets
        self.unseen_sources = set()  # Labels of all nodes not processed yet that have no incoming edges
        self.longest_in_weight = {}  # Dictionary {<label>:<weight>, ...}
        self.longest_in_route = {}   # Dictionary {<label>:[<label>, ...], ...}
        self.longest_route = None;   # The longest route (in weights) we have seen
        self.longest_route_weight = None;  # The largest weight we have seen
    
    def add_node(self, label):
        self.nodes.add(label)
        self.edges[label] = set()
        self.rev_edges[label] = set()
        self.unseen_sources.add(label)
        
    def add_edge(self, source, target, weight):
        if weight < 0: raise ValueError("weight cannot be negative")
        if source not in self.nodes: raise ValueError("source {} not a node".format(source))
        if target not in self.nodes: raise ValueError("target {} not a node".format(target))
        self.edges[source].add(target)
        self.rev_edges[target].add(source)
        self.edge_weights[(source, target)] = weight
        self.unseen_sources.discard(target)
        
    def add_edges(self, sources, targets, weights):
        if len(sources) != len(targets) != len(weights):
            raise ValueError(
                f"given data does not have the same length: {len(sources)}, {len(targets)}, {len(weights)}")
        else:
            l = len(sources)
        
        for i in range(l):
            self.add_edge(sources[i], targets[i], weights[i])
    
    def _convert_nodes_to_paths(self, nodes):
        """Support function to convert nodes to list of tuples"""
        return [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
    
    def add_action_names(self, names, seq):
        """
        Need to have computed longest path beforehand.  
        Given names and according sequences convert nodes into path names.  
        
        # Example
        
        ```python
        >>> names = ['A', 'B', 'C']
        >>> seq   = [(1, 2), (2, 3), (3, 4)]
        >>> seq_b = [1, 2, 3]
        >>> seq_e = [2, 3, 4]
        >>> durs  = [1, 1, 2]
        >>> cpath = CriticalPath()
        >>> cpath.add_edges()
        >>> cpath.longest_path()
        [[1, 2, 3, 4], 4]
        >>> cpath.add_action_names(names, seq)
        [['A', 'B', 'C'], 4]
        ```
        """
        if any([self.longest_route==None, self.longest_route_weight==None]):
            raise ValueError("You need to calculate longest_path first.")
        
        actions = self._convert_nodes_to_paths(self.longest_route)
        seq_names_dict = dict(zip(seq, names))
        self.longest_route = []
        for action in actions:
            try:
                self.longest_route.append(seq_names_dict[action])
            except:
                raise ValueError("Value is not present in given names and/or sequence")
        
        return (self.longest_route, self.longest_route_weight)
        
        
    def longest_path(self):
        while len(self.unseen_sources) > 0:
            sourcenode = self.unseen_sources.pop()
            
            new_weight = self.longest_in_weight.get(sourcenode, 0)
            new_route = self.longest_in_route.get(sourcenode, []) + [sourcenode]

            if len(self.edges[sourcenode]) == 0: # no outgoing edges; isolated node
                if self.longest_route is None or self.longest_route_weight < new_weight:
                    self.longest_route = new_route
                    self.longest_route_weight = new_weight
                continue
            
            # There are outgoing edges            
            for target in self.edges[sourcenode]:
                edge_weight = self.edge_weights[(sourcenode, target)]
                if self.longest_in_weight.get(target, 0) < new_weight + edge_weight:
                    self.longest_in_weight[target] = new_weight + edge_weight
                    self.longest_in_route[target] = new_route
                
            self.__del_edges_from(sourcenode)
                
        return (self.longest_route, self.longest_route_weight)
    
    def __del_edges_from(self, source):
        """Private method to delete all outgoing edges from a node."""
        targets = self.edges[source]
        self.edges[source] = set()
        for target in targets:
            self.rev_edges[target].discard(source)
            if len(self.rev_edges[target]) == 0: # no incoming edges
                self.unseen_sources.add(target)
                
    def _print(self):
        """Private method to print information about the graph."""
        print("Nodes, Edges")
        for id, w in enumerate(self.nodes):
            print("  {}{} = {} -> {}".format(
                's' if id in self.unseen_sources else ' ', 
                id, 
                w,
                ",".join([str(x) for x in self.edges[id]])
            ))
        print("Rev-Edges")
        for id, source in self.rev_edges.items():
            print("  {} <- {}".format(id, ",".join([str(x) for x in source])))      
        print("")
