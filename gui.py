import tkinter as tk
from tkinter import W, Entry, ttk

class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x500")
        self.create_entrypage()

    def create_entrypage(self):
        self.label = tk.Label(self.root, text="Wybierz metodę:")
        self.label.pack()

        self.cpm_button = tk.Button(self.root, text="CPM", command=self.cpm_button_click)
        self.cpm_button.pack()

        self.middleman_button = tk.Button(self.root, text="Zagadnienie pośrednika", command=self.cpm_button_click)
        self.middleman_button.pack()

    def cpm_button_click(self):
        self.clear_window()
        self.create_table()
        

    def middleman_button_click(self):
        self.clear_window()
        self.label.config(text="Kliknięto przycisk!")

    def create_table(self):
        self.tree = ttk.Treeview(self.root, columns=("Column 1", "Column 2", "Column 3"), show="headings")
        self.tree.heading("Column 1", text="Czynnosc")
        self.tree.heading("Column 2", text="Czas trwania (dni)")
        self.tree.heading("Column 3", text="Następstwo zdarzen")
        
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<Double-1>", self.onDoubleClick)

        add_button = tk.Button(self.root, text="Dodaj wiersz", command=self.add_empty_row)
        add_button.pack()

    def add_empty_row(self):
        new_row = ("", "", "")
        self.tree.insert("", "end", values=new_row)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def onDoubleClick(self, event):
        try:  
            self.entryPopup.destroy()
        except AttributeError:
            pass

        rowid = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not rowid:
            return

        x,y,width,height = self.tree.bbox(rowid, column)

        pady = height // 2

        text = self.tree.item(rowid, 'values')[int(column[1:])-1]
        self.entryPopup = EntryPopup(self.tree, rowid, int(column[1:])-1, text)
        self.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
        self.entryPopup.bind("<FocusOut>", self.on_entry_focus_out)

    def on_entry_focus_out(self, event):
        self.entryPopup.on_return(event)



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


    

        