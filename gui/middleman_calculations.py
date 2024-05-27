import tkinter as tk
from tkinter import ttk

def generate_fields_and_calculate(root):
    bg_color = '#494949'
    fg_color = 'white'

    def create_fields():
        try:
            num_consumers = int(consumers_entry.get())
            num_suppliers = int(suppliers_entry.get())
        except ValueError:
            error_label.config(text="Proszę podać prawidłowe liczby.")
            return

        # Clear previous fields
        for widget in fields_frame.winfo_children():
            widget.destroy()

        # Header labels
        tk.Label(fields_frame, text="", bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(fields_frame, text="Supply", bg=bg_color, fg=fg_color).grid(row=1, column=1, padx=10, pady=5)
        for i in range(num_consumers):
            tk.Label(fields_frame, text=f"Customer {i+1}", bg=bg_color, fg=fg_color).grid(row=1, column=i+2, padx=10, pady=5)
        tk.Label(fields_frame, text="Purchase price", bg=bg_color, fg=fg_color).grid(row=1, column=num_consumers+2, padx=10, pady=5)

        # Demand labels and entries
        tk.Label(fields_frame, text="Demand", bg=bg_color, fg=fg_color).grid(row=0, column=1, padx=10, pady=5)
        demand_entries = []
        for i in range(num_consumers):
            demand_entry = tk.Entry(fields_frame)
            demand_entry.grid(row=0, column=i+2, padx=10, pady=5)
            demand_entries.append(demand_entry)
        tk.Label(fields_frame, text="", bg=bg_color, fg=fg_color).grid(row=0, column=num_consumers+2, padx=10, pady=5)

        # Supply, transport cost, and price labels and entries
        supply_entries = []
        transport_cost_entries = []
        buying_price_entries = []
        selling_price_entries = []

        for i in range(num_suppliers):
            tk.Label(fields_frame, text=f"Supplier {i+1}", bg=bg_color, fg=fg_color).grid(row=i+2, column=0, padx=10, pady=5)
            supply_entry = tk.Entry(fields_frame)
            supply_entry.grid(row=i+2, column=1, padx=10, pady=5)
            supply_entries.append(supply_entry)

            row_entries = []
            for j in range(num_consumers):
                transport_cost_entry = tk.Entry(fields_frame, bg='orange')
                transport_cost_entry.grid(row=i+2, column=j+2, padx=10, pady=5)
                row_entries.append(transport_cost_entry)
            transport_cost_entries.append(row_entries)

            buying_price_entry = tk.Entry(fields_frame)
            buying_price_entry.grid(row=i+2, column=num_consumers+2, padx=10, pady=5)
            buying_price_entries.append(buying_price_entry)

        # Selling price labels and entries
        tk.Label(fields_frame, text="Selling price", bg=bg_color, fg=fg_color).grid(row=num_suppliers+2, column=1, padx=10, pady=5)
        for i in range(num_consumers):
            selling_price_entry = tk.Entry(fields_frame)
            selling_price_entry.grid(row=num_suppliers+2, column=i+2, padx=10, pady=5)
            selling_price_entries.append(selling_price_entry)
        tk.Label(fields_frame, text="", bg=bg_color, fg=fg_color).grid(row=num_suppliers+2, column=num_consumers+2, padx=10, pady=5)

        # Calculate button
        calculate_button = ttk.Button(fields_frame, text="Oblicz", command=lambda: calculate(num_suppliers, num_consumers, supply_entries, demand_entries, transport_cost_entries, buying_price_entries, selling_price_entries))
        calculate_button.grid(row=num_suppliers+3, columnspan=num_consumers+3, pady=10)

    def calculate(num_suppliers, num_consumers, supply_entries, demand_entries, transport_cost_entries, buying_price_entries, selling_price_entries):
        # Collecting data from entries
        supplies = [int(entry.get()) for entry in supply_entries]
        demands = [int(entry.get()) for entry in demand_entries]
        transport_costs = [[int(entry.get()) for entry in row] for row in transport_cost_entries]
        buying_prices = [int(entry.get()) for entry in buying_price_entries]
        selling_prices = [int(entry.get()) for entry in selling_price_entries]

        # Placeholder for actual calculation logic
        total_profit = 1000  # Replace with actual calculation logic
        unit_costs = [[20 for _ in range(num_consumers)] for _ in range(num_suppliers)]  # Placeholder
        optimal_quantities = [[5 for _ in range(num_consumers)] for _ in range(num_suppliers)]  # Placeholder

        # Clear previous results
        for widget in result_frame.winfo_children():
            widget.destroy()

        # Display total profit
        tk.Label(result_frame, text=f"Całkowity zysk: {total_profit}", bg=bg_color, fg=fg_color).pack(pady=10)

        # Frame for tables
        tables_frame = tk.Frame(result_frame, bg=bg_color)
        tables_frame.pack(pady=5)

        # Display unit costs table
        unit_costs_label = tk.Label(tables_frame, text="Koszty jednostkowe", bg=bg_color, fg=fg_color)
        unit_costs_label.grid(row=0, column=0, padx=10, pady=5)
        unit_costs_frame = tk.Frame(tables_frame, bg=bg_color)
        unit_costs_frame.grid(row=1, column=0, padx=10, pady=5)
        for i in range(num_suppliers):
            for j in range(num_consumers):
                tk.Label(unit_costs_frame, text=f"{unit_costs[i][j]}", bg=bg_color, fg=fg_color).grid(row=i, column=j, padx=10, pady=5)

        # Display optimal quantities table
        optimal_quantities_label = tk.Label(tables_frame, text="Optymalna ilość produktów", bg=bg_color, fg=fg_color)
        optimal_quantities_label.grid(row=0, column=1, padx=10, pady=5)
        optimal_quantities_frame = tk.Frame(tables_frame, bg=bg_color)
        optimal_quantities_frame.grid(row=1, column=1, padx=10, pady=5)
        for i in range(num_suppliers):
            for j in range(num_consumers):
                tk.Label(optimal_quantities_frame, text=f"{optimal_quantities[i][j]}", bg=bg_color, fg=fg_color).grid(row=i, column=j, padx=10, pady=5)

    # Clear previous widgets in the root, except the back button
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Button) and widget.cget('text') == 'Back':
            continue
        widget.destroy()

    # Creating input fields for suppliers and consumers
    input_frame = tk.Frame(root, bg=bg_color)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Ilość dostawców:", bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=10, pady=5)
    suppliers_entry = tk.Entry(input_frame)
    suppliers_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(input_frame, text="Ilość odbiorców:", bg=bg_color, fg=fg_color).grid(row=1, column=0, padx=10, pady=5)
    consumers_entry = tk.Entry(input_frame)
    consumers_entry.grid(row=1, column=1, padx=10, pady=5)

    generate_button = ttk.Button(input_frame, text="Generuj pola", command=create_fields)
    generate_button.grid(row=2, columnspan=2, pady=10)

    error_label = tk.Label(root, text="", fg="red", bg=bg_color)
    error_label.pack(pady=5)

    fields_frame = tk.Frame(root, bg=bg_color)
    fields_frame.pack(pady=10)

    result_frame = tk.Frame(root, bg=bg_color)
    result_frame.pack(pady=10)
