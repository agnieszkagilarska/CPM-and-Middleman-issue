import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from util.critical import CPMNetwork

Graph = nx.DiGraph()

###### do pełnej zmiany, poprawy

Graph.add_nodes_from(['A', 'B', 'C', 'D', 'E']) #węzły
Graph.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E')]) #krawędzie
T = {'A': 1, 'B': 2, 'C': 6, 'D': 0, 'E': 1} #czas trwania

# T jest prawdopodobnie niepoprawne -> zdarzenie nie trwa, czynność tak.
#
#
#   T = {('A', 'B'): 1, ('A', 'C'): 1, ('B', 'D'): 2, ('C', 'E'): 6, ('D', 'E'): 0}
#

#prototyp obliczania wartości ES, EF, R
event_list = list(nx.topological_sort(Graph))
ES = {event: 0 for event in event_list}
EF = {}
R = {event: 0 for event in event_list}

for event in event_list:
    max_ES = 0
    for predecessor in Graph.predecessors(event):
        max_ES = max(max_ES, EF[predecessor])
    ES[event] = max_ES
    EF[event] = ES[event] + T[event]

# ES, EF, R są obliczone
# należy odpowiednio dobrać typ natomiast:
# ES = {'A': 0, 'B':1, ...} itd

print(ES, EF, R)

#######

# ------------------------------------------------------------------------------ nowe dane
# N - name
# D - duration
# B - begin node
# E - end node

# case 1:
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

network = CPMNetwork()
for row in Table:
    network.create_action(row[0], row[2][0], row[2][1], row[1])

network.print_actions()
network.create_nodes_from_actions()
# print(network.node_dict)
network.print_nodes()
network.calc_es_ls()
network.print_nodes()
node_id, es, ls, r, node_sequence_ids, action_name, time = network.get_data_for_graph()


Graph = nx.DiGraph()

Graph.add_nodes_from(node_id) #węzły
Graph.add_edges_from(node_sequence_ids, action_name=action_name) #krawędzie
T = time #czas trwania
event_list = list(nx.topological_sort(Graph))

ES = es
EF = ls # wiem, to jest niepoprawne, ale tymczasowo zamiast ef jest ls TODO
R = r

# ------------------------------------------------------------------------------ nowe dane
#dodawanie wierzchołków do ścieżki krytycznej
critical_path = []
for event in event_list:
    if R[event] == 0: #jeśli rezerwa czasowa = 0 --> należy do CP
        critical_path.append(event)

# Kolorowanie krawędzi w zależności od należenia do ścieżki krytycznej
edge_colors = ['green' if (u in critical_path and v in critical_path) else 'black' for u, v in Graph.edges()]

position = nx.spring_layout(Graph)

node_colors = ['green' if node in critical_path else 'red' for node in Graph.nodes()] #kolorowanie węzłów w zależności od przynależności do CP

plt.figure(figsize=(14, 7))

nx.draw(Graph, position, with_labels=True, node_size=5000, node_color=node_colors, font_size=50, font_weight="bold", node_shape='o', edge_color=edge_colors)  #rozmiar, wygląd wierzchołków

#wypisywanie wartości na krawędziach
# poprawa -> T[(u, v)] z T[u]
edge_labels = {(u, v): f" ({T[(u, v)]} days)" for u, v in Graph.edges()}
nx.draw_networkx_edge_labels(Graph, position, edge_labels=edge_labels, font_color="blue")

#wypisywanie wartości na węzłach
for event in event_list:
    plt.text(position[event][0], position[event][1], f"\nES: {ES[event]}\nEF: {EF[event]}\nR: {R[event]}\n", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5, boxstyle='circle'))

#legenda
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Należy do ścieżki krytycznej', markerfacecolor='green', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Nie należy do ścieżki krytycznej', markerfacecolor='red', markersize=15),
    Line2D([0], [0], marker='', color='w', label='ES - Najwcześniejszy czas rozpoczęcia', markerfacecolor='black', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='', color='w', label='EF - Najwcześniejszy czas zakończenia', markerfacecolor='black', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='', color='w', label='R - Rezerwa czasowa', markerfacecolor='black', markersize=15, linestyle='None')]

plt.legend(handles=legend_elements, loc='upper left')
plt.show()
