import tkinter as tk
from tkinter import W, Entry, ttk
from tkinter import messagebox
from gui.interactive_table import create_table
import re

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
        create_table(self.root)

    def middleman_button_click(self):
        self.clear_window()
        self.label.config(text="Kliknięto przycisk!")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
                