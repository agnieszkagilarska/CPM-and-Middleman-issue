import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re
from util.critical import CriticalPath

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
    tree.tag_configure('odd', background='#696969')
    tree.tag_configure('even', background='#3a3a3a')

    add_button = ttk.Button(root, text="Dodaj wiersz", command=lambda: add_empty_row(tree))
    add_button.pack(side="left",padx=10, pady=10)
    
    delete_button = ttk.Button(root, text="Usuń wiersz", command=lambda: delete(tree))
    delete_button.pack(side="left",padx=10, pady=10)
    
    accept_button = ttk.Button(root, text="Generuj graf", command=lambda: calculate_cpath(tree))
    accept_button.pack(side="right", padx=10, pady=10)

    accept_button = ttk.Button(root, text="Generuj wykres Gantta", command=lambda: calculate_cpath(tree))
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

def calculate_cpath(tree):
    names, durations, sequences = get_table_info(tree)
    
    sequence_b = [item[0] for item in sequences]
    sequence_e = [item[1] for item in sequences]
    
    cpath = CriticalPath()
    for i in range(len(names)-1): cpath.add_node(i)
    cpath.add_edges(sequence_b, sequence_e, durations)
    
    l_path = cpath.longest_path()
    path, length = cpath.add_action_names(names, sequences)
    
    messagebox.showinfo("Results", f"path: {path}, length: {length}")