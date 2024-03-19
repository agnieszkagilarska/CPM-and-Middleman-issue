from critical import CriticalPath, CPMNetwork
'''
Algorithm that calculates the critical path given the inputs.
Inputs: 
- Action: List['str']
- Duration: time['int']
- Action sequence: action_numbers['int', 'int']
'''
# N - name
# D - duration
# B - begin node
# E - end node

# case 1
Table = [
    # N | D | B, E |
    ('A', 3, (0, 1)), # 0
    ('B', 4, (1, 2)), # 1
    ('C', 6, (1, 3)), # 2
    ('D', 7, (2, 4)), # 3
    ('E', 1, (4, 6)), # 4
    ('F', 2, (3, 6)), # 5
    ('G', 3, (3, 5)), # 6
    ('H', 4, (5, 6)), # 7
    ('I', 1, (6, 7)), # 8
    ('J', 2, (7, 8)), # 9
]

Action     = [item[0] for item in Table]
Duration   = [item[1] for item in Table]
Sequence   = [item[2] for item in Table]
Sequence_b = [item[2][0] for item in Table]
Sequence_e = [item[2][1] for item in Table]
        
# Driver code
if __name__ == '__main__':
    # cpath = CriticalPath()
    # for i in range(len(Table)-1): cpath.add_node(i)
    
    # cpath.add_edges(Sequence_b, Sequence_e, Duration)
    # cpath._print()
    # print(cpath.longest_path())
    # print(cpath.add_action_names(Action, Sequence))
    
    network = CPMNetwork()
    for row in Table:
        network.create_action(row[0], row[2][0], row[2][1], row[1])
    
    network.print_actions()
    network.create_nodes_from_actions()
    # print(network.node_dict)
    network.print_nodes()
    network.calc_es_ls()
    network.print_nodes()
    # print(network.get_dataframe()[0])
    # print(network.get_dataframe()[1])
    print(network.get_data_for_graph())