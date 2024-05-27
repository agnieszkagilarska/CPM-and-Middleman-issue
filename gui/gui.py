import os
import tkinter as tk
from tkinter import ttk
from gui.interactive_table import create_table
from ttkthemes import ThemedStyle
from gui.middleman_calculations import generate_fields_and_calculate

class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x700")

        self.configure_theme()
        self.create_entrypage()

    def configure_theme(self):
        style = ThemedStyle(self.root)
        style.set_theme("equilux")
        self.root.configure(bg='#494949')

    def create_entrypage(self):
        self.clear_window()
        button_width = 40 
        button_padx = 10  
        button_pady = 20 


        self.label = ttk.Label(self.root, text="Wybierz metodę:")
        self.label.pack(padx=button_padx, pady=button_pady)

        self.cpm_button = ttk.Button(self.root, text="CPM", command=self.cpm_button_click, width=button_width)
        self.cpm_button.pack(padx=button_padx, pady=button_pady)

        self.middleman_button = ttk.Button(self.root, text="Zagadnienie pośrednika", command=self.middleman_button_click, width=button_width)
        self.middleman_button.pack(padx=button_padx, pady=button_pady)


    def cpm_button_click(self):
        self.clear_window()
        self.back_button = ttk.Button(self.root, text="Back", command=self.create_entrypage, width=20)
        self.back_button.pack(side="left", padx=10, pady=10)
        create_table(self.root)
        

    def middleman_button_click(self):
        self.clear_window()
        self.configure_theme()
        self.back_button = ttk.Button(self.root, text="Back", command=self.create_entrypage, width=20)
        self.back_button.pack(side="left", padx=10, pady=10)
        generate_fields_and_calculate(self.root)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        