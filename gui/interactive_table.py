import tkinter as tk
from tkinter import ttk

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
    tree = ttk.Treeview(root, columns=("Column 1", "Column 2", "Column 3"), show="headings")
    tree.heading("Column 1", text="Czynnosc")
    tree.heading("Column 2", text="Czas trwania (dni)")
    tree.heading("Column 3", text="Następstwo zdarzen")
        
    tree.pack(expand=True, fill="both")
    tree.bind("<Double-1>", lambda event: onDoubleClick(event, tree))

    add_button = tk.Button(root, text="Dodaj wiersz", command=lambda: add_empty_row(tree))
    add_button.pack()

def add_empty_row(tree):
    new_row = ("", "", "")
    tree.insert("", "end", values=new_row)

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