import pandas as pd

class CriticalPath:
    '''
    PROBABLY NOT USEFUL: DEPRICATED
    '''
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

class Node:
    def __init__(self, nid, es=None, ls=None) -> None:
        self.nid = nid
        self.es = es
        self.ls = ls
        self.prev_nodes = set()
        self.next_nodes = set()
        if (es is not None) and (ls is not None):
            self.residuum = self.ls - self.es
        else:
            self.residuum = None
    def __str__(self) -> str:
        return f"Node(nid={self.nid},es={self.es},ls={self.ls},prev_nodes={self.prev_nodes},next_nodes={self.next_nodes},residuum={self.residuum}"
            
class Action:
    def __init__(self, name, start_id, end_id, duration) -> None:
        self.name = name
        self.start_id = start_id
        self.end_id = end_id
        self.duration = duration
    
    def __str__(self) -> str:
        return f"Action(name={self.name},start_id={self.start_id},end_id={self.end_id},duration={self.duration})"
        
class CPMNetwork:
    def __init__(self) -> None:
        self.nodes = []
        self.actions = set()
        self.node_dict = {}
        
    def create_action(self, name, start_id, end_id, duration):
        self.actions.add(Action(name, start_id, end_id, duration))
        
    def create_nodes_from_actions(self):
        node_ids = set()
        self.sequence_b = []
        self.sequence_e = []
        for action in self.actions:
            self.sequence_b.append(action.start_id)
            self.sequence_e.append(action.end_id)
            
        node_ids.update(self.sequence_b)
        node_ids.update(self.sequence_e)
                
        self.actions_dur_dict = {tuple(key): duration for key, duration in 
                                 zip(zip(self.sequence_b, self.sequence_e), [action.duration for action in self.actions])}
        
        # intialize the nodes with given ids and create a dictionary: nid -> node
        for nid in node_ids:
            node = Node(nid)
            self.nodes.append(node)
            self.node_dict[nid] = node
        
        # set previous and next node ids
        for i, n in enumerate(self.sequence_b):
            m = self.sequence_e[i]
            if n==m:
                raise ValueError(f"Node with id {n} is self-connected.")
            self.node_dict[n].next_nodes.add(m)
            self.node_dict[m].prev_nodes.add(n)
        
        # find start node id
        for n in self.sequence_b:
            if n not in self.sequence_e:
                self.start_id = n
        # find end node id
        for m in self.sequence_e:
            if m not in self.sequence_b:
                self.end_id = m
        
    def calc_es_ls(self):
        def _return_next_nodes(nid):
            return self.node_dict[nid].next_nodes
        
        def _return_prev_nodes(nid):
            return self.node_dict[nid].prev_nodes
        
        # calculate ES (Early start - from beginning)
        for node in self.node_dict.values():
            # start from 0:
            if node.nid == self.start_id:
                node.es = 0
                continue
            
            # previous nodes and according actions
            prev_nodes_ids = _return_prev_nodes(node.nid)
            according_actions = []
            
            # need to find according actions
            for action in self.actions:
                for prev_nid in prev_nodes_ids:
                    if (action.start_id == prev_nid and # start is in previous node
                        action.end_id == node.nid): # current node is end of action
                        according_actions.append((action, prev_nid))
            
            # sort them with previous_nodes_ids as key for later
            according_actions = sorted(according_actions, key=lambda x: x[1])
            according_actions = [action for action, _ in according_actions]
            
            # find latest time from previous nodes + duration of action
            max_prev = max(
                zip([action.duration for action in according_actions],
                    # here is the reason why to sort:
                    [self.node_dict[prev_nid].es for prev_nid in prev_nodes_ids]
                ),
                key=lambda p: p[0] + p[1] # use it like: node.es + according_action.duration
            )
            
            node.es = max_prev[1] + max_prev[0]
        
        # calculate LS (Late Start - from end - based on ES)
        for node in self.node_dict.values().__reversed__():
            # start from ES as LS in end node (es == ls):
            if node.nid == self.end_id:
                node.ls = node.es
                node.residuum = node.ls - node.es
                continue
            
            # next (previous from end) nodes and according actions
            next_nodes_ids = _return_next_nodes(node.nid)
            according_actions = []
            
            # need to find according actions
            # Here we are doing it backwards:
            #
            #   start       Action       end
            # |  node  | -----------> | next_node|
            # info flow: <-----------
            for action in self.actions:
                for next_nid in next_nodes_ids:
                    if (action.end_id == next_nid and # start is in previous node
                        action.start_id == node.nid): # current node is end of action
                        according_actions.append((action, next_nid))
            
            # sort them with previous_nodes_ids as key for later
            according_actions = sorted(according_actions, key=lambda x: x[1])
            according_actions = [action for action, _ in according_actions]
            
            print(node.nid, node.es, [(aa.start_id, aa.end_id, aa.duration) for aa in according_actions])
            
            # find earliest time from next nodes - duration of action
            min_next = min(
                zip([action.duration for action in according_actions],
                    [self.node_dict[next_nid].ls for next_nid in next_nodes_ids]
                ),
                key=lambda p: p[1] - p[0] # use it like: node.es + according_action.duration
            )
            
            print(min_next)
            
            node.ls = min_next[1] - min_next[0]
            # we can now calculate the residuum
            node.residuum = node.ls - node.es
            
    def print_actions(self):
        for action in self.actions:
            print(action)
            
    def print_nodes(self):
        for node in self.nodes:
            print(node)
    
    def get_dataframe(self):
        '''
        node_dataframe: pd.DataFrame( # based on nodes
            node_id: str, # NODES
            ES : dict['str']->int,
            LS : dict['str']->int,
            R  : dict['str']->int,
            ...
        )
        action_dataframe: pd.DataFrame)( # based on actions
            node_sequence_ids: List[('str', 'str')], # EDGES
            action_name: List['str'],
            time: dict[('str','str')] -> int # TIME
        )
        '''
        n_df = pd.DataFrame()
        a_df = pd.DataFrame()
        
        n_df['node_id'] = [str(node.nid) for node in self.nodes]
        n_df['ES'] = [node.es for node in self.nodes]
        n_df['LS'] = [node.ls for node in self.nodes]
        n_df['R'] = [node.residuum for node in self.nodes]
        
        a_df['node_sequence_ids'] = [(str(action_dur[0]), str(action_dur[1])) for action_dur in self.actions_dur_dict]
        a_df['action_name'] = [action.name for action in self.actions]
        a_df['time'] = self.actions_dur_dict.values()
        
        return n_df, a_df

    def get_data_for_graph(self):
        '''
        returns:
        (
            node_id          : str,                         # NODES
            ES               : dict['str']->int,
            LS               : dict['str']->int,
            R                : dict['str']->int,
            node_sequence_ids: List[('str', 'str')],        # EDGES
            action_name      : List['str'],
            time             : dict[('str','str')] -> int   # TIME
        )
        '''
        node_id = [str(node.nid) for node in self.nodes]
        es = {str(node.nid): node.es for node in self.nodes}
        ls = {str(node.nid): node.ls for node in self.nodes}
        r  = {str(node.nid): node.residuum for node in self.nodes}
        
        node_sequence_ids = [(str(action_dur[0]), str(action_dur[1])) for action_dur in self.actions_dur_dict]
        action_name = [action.name for action in self.actions]
        time = {tuple((str(action.start_id), str(action.end_id))): action.duration for action in self.actions}
        
        return (node_id, es, ls, r,
                node_sequence_ids, action_name, time)