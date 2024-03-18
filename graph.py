import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

Graph = nx.DiGraph()

###### do pełnej zmiany, poprawy

Graph.add_nodes_from(['A', 'B', 'C', 'D', 'E']) #węzły
Graph.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E')]) #krawędzie
T = {'A': 1, 'B': 2, 'C': 6, 'D': 0, 'E': 1} #czas trwania

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

#######

#dodawanie wierzchołków do ścieżki krytycznej
critical_path = []
for event in event_list:
    if R[event] == 0: #jeśli rezerwa czasowa = 0 --> należy do CP
        critical_path.append(event)


position = nx.spring_layout(Graph)

node_colors = ['green' if node in critical_path else 'red' for node in Graph.nodes()] #kolorowanie węzłów w zależności od przynależności do CP

plt.figure(figsize=(14, 7))

nx.draw(Graph, position, with_labels=True, node_size=5000, node_color=node_colors, font_size=50, font_weight="bold", node_shape='o')  #rozmiar, wygląd wierzchołków

#wypisywanie wartości na krawędziach
edge_labels = {(u, v): f" ({T[u]} days)" for u, v in Graph.edges()} 
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

