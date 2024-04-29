import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import re
from util.critical import CPMNetwork
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text, **kw):
        ttk.Style().configure('pad.TEntry', padding='1 1 1 1')
        super().__init__(parent, style='pad.TEntry', **kw)
        self.tv = parent
        self.iid = iid
        self.column = column

        self.insert(0, text) 
        self['exportselection'] = False

        self.focus_force()
        self.select_all()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        
    def on_return(self, event):
        rowid = self.tv.focus()
        vals = self.tv.item(rowid, 'values')
        vals = list(vals)
        vals[self.column] = self.get()
        self.tv.item(rowid, values=vals)
        self.tv.focus(rowid)
        self.destroy()


    def select_all(self, *ignore):
        self.selection_range(0, 'end')
        return 'break'

def create_table(root):
    global n_rows
    tree = ttk.Treeview(root, columns=("Column 1", "Column 2", "Column 3"), show="headings")
    n_rows = 0
    tree.heading("Column 1", text="Czynnosc [str]")
    tree.heading("Column 2", text="Czas trwania (dni) [int]")
    tree.heading("Column 3", text="Następstwo zdarzen [int-int]")
    
    tree.pack(expand=True, fill="both")
    tree.bind("<Double-1>", lambda event: onDoubleClick(event, tree))
    tree.tag_configure('odd', background='#575757')
    tree.tag_configure('even', background='#3a3a3a')

    add_button = ttk.Button(root, text="Dodaj wiersz", command=lambda: add_empty_row(tree))
    add_button.pack(side="left",padx=10, pady=10)
    
    delete_button = ttk.Button(root, text="Usuń wiersz", command=lambda: delete(tree))
    delete_button.pack(side="left",padx=10, pady=10)
    
    import_button = ttk.Button(root, text="Importuj tabelę (csv)", command=lambda: import_table(root, tree))
    import_button.pack(side="left",padx=10, pady=10)
    
    accept_button = ttk.Button(root, text="Generuj graf", command=lambda: critical_path(tree))#calculate_cpath(tree))
    accept_button.pack(side="right", padx=10, pady=10)

    accept_button = ttk.Button(root, text="Generuj wykres Gantta", command=lambda: gantt(tree))
    accept_button.pack(side="right", padx=10, pady=10)

    return tree
    

def add_empty_row(tree):
    global n_rows
    new_row = ("", "", "")
    if n_rows % 2 == 0:
        tag = 'even'
    else:
        tag = 'odd'
    tree.insert("", "end", values=new_row, tags=(tag))
    n_rows += 1
    
    
def delete(tree):
    global n_rows
    try:
        selected_item = tree.selection()[0] ## get selected item
        tree.delete(selected_item)
        n_rows-=1
        
        for i, child in enumerate(tree.get_children()):
            if i % 2 == 0:
                tag = 'even'
            else:
                tag = 'odd'
    except Exception as e:
        print(e)
        messagebox.showerror("Błąd usuwania wiersza", "Zaznacz istniejący wiersz w tabeli.")
        
def import_table(root, tree):
    global n_rows
    if n_rows % 2 == 0:
        tag = 'even'
    else:
        tag = 'odd'
        
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ('All',"*.*")])
    if file_path:
        df = pd.read_csv(file_path, sep=',')
        
        for i, row in df.iterrows():
            name = row[0]
            duration = row[1]
            sequence = row[2]
            
            new_row = (name, duration, sequence)
            
            tree.insert("", "end", values=new_row, tags=(tag))
            n_rows+=1
            
    else:
            messagebox.showerror("Error", "Nieprawidłowe wczytanie pliku csv")
    ...

def onDoubleClick(event, tree):
    try:  
        tree.entryPopup.destroy()
    except AttributeError:
        pass

    rowid = tree.identify_row(event.y)
    column = tree.identify_column(event.x)

    if not rowid:
        return

    x,y,width,height = tree.bbox(rowid, column)

    pady = height // 2

    text = tree.item(rowid, 'values')[int(column[1:])-1]
    tree.entryPopup = EntryPopup(tree, rowid, int(column[1:])-1, text)
    tree.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
    tree.entryPopup.bind("<FocusOut>", lambda event: on_entry_focus_out(event, tree))

def on_entry_focus_out(event, tree):
    tree.entryPopup.on_return(event)
    
def get_table_info(tree):
    def extract_numbers(s):
        return re.findall(r'\d+', s)
    
    names = []
    durations = []
    sequences = []
    for i, row in enumerate(tree.get_children()):
        name, duration, sequence = tuple(tree.item(row)['values'])
        # formatting
        names.append(name)
        
        try:
            durations.append(int(duration))
        except Exception as e:
            print(e)
            messagebox.showerror("Błąd w formatowaniu", "Wpisz tylko liczby całkowite w czasie trwania.")
        
        try:
            numbers = tuple(map(int, extract_numbers(sequence)))
            if len(numbers)!=2: raise Exception("Błąd w formatowaniu. Wpisz tylko dwie liczby")
            sequences.append(numbers)
        except Exception as e:
            print(e)
            messagebox.showerror("Błąd w formatowaniu", "Wpisz tylko dwie liczby")
    return [names, durations, sequences]

def critical_path(tree):
    node_id, es, ls, r, node_sequence_ids, action_name, time = calculate_cpath(tree)
    
    graph_cpath(node_id, es, ls, r, node_sequence_ids, action_name, time)

def gantt(tree):
    node_id, es, ls, r, node_sequence_ids, action_name, time = calculate_cpath(tree)
    
    gantt_chart(node_id, es, ls, r, node_sequence_ids, action_name, time, tree)    

def calculate_cpath(tree):
    names, durations, sequences = get_table_info(tree)
    
    sequence_b = [item[0] for item in sequences]
    sequence_e = [item[1] for item in sequences]
    
    network = CPMNetwork()
    for i in range(len(names)):
        network.create_action(names[i], sequence_b[i], sequence_e[i], durations[i])

    # network.print_actions()
    network.create_nodes_from_actions()

    # network.print_nodes()

    try:
        network.validate_network()
        network.calc_es_ls()
        network.print_nodes()
        return network.get_data_for_graph()
    except Exception as e:
        print(e)
        messagebox.showerror("Error", e)
        return None
        


def gantt_chart(node_id, es, ls, r, node_sequence_ids, action_name, time, tree):

    ES = es
    EF = ls
    R = r
    T = time

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_facecolor('lightgrey')
    

    sorted_zip = sorted(zip(node_sequence_ids, action_name), key=lambda x: x[1])
    for action, action_n in sorted_zip:
        u, v = action
        ax.barh(action_n, width= T[(u, v)] , left=ES[u], color='lightgreen', edgecolor='black', linewidth=2)
        ax.text(ES[u] + T[(u, v)]/2, action_n, f"{action_n} ({T[(u, v)]} day(s))", ha='center', va='center', color='black', fontsize=8)
        ax.barh(action_n, width= T[(u, v)] , left=EF[u], color='lightblue', edgecolor='black', linewidth=2)
        # ax.annotate('', xy=(ES[u] + T[(u, v)], action_n), xytext=(ES[v], action_n),arrowprops=dict(facecolor='black', shrink=0.05, width=0.5)) 
                
    green_patch = mpatches.Patch(color='lightgreen', label='ASAP - Jak najszybciej możliwe.')
    blue_patch = mpatches.Patch(color='lightblue', label='ALAP - Jak najpóźniej możliwe.')
    ax.legend(handles=[green_patch, blue_patch], loc='upper right')

    ax.set_xlabel('Czas trwania')
    ax.set_ylabel('Zadania')
    ax.set_title('Wykres Gantta')
    ax.grid(True)
    ax.invert_yaxis()

    plt.show()
        
    
def graph_cpath(node_id, es, ls, r, node_sequence_ids, action_name, time):
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
        plt.text(position[event][0], position[event][1], f"\nES: {ES[event]}\nLS: {EF[event]}\nR: {R[event]}\n", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5, boxstyle='circle'))

    #legenda
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Należy do ścieżki krytycznej', markerfacecolor='green', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Nie należy do ścieżki krytycznej', markerfacecolor='red', markersize=15),
        Line2D([0], [0], marker='', color='w', label='ES - Najwcześniejszy czas rozpoczęcia', markerfacecolor='black', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='', color='w', label='LS - Najpóźniejszy czas rozpoczęcia', markerfacecolor='black', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='', color='w', label='R - Rezerwa czasowa', markerfacecolor='black', markersize=15, linestyle='None')]

    plt.legend(handles=legend_elements, loc='upper left')
    plt.show()
    
    messagebox.showinfo("Results", f"path {critical_path}, length: {ls[node_id[-1]]}")