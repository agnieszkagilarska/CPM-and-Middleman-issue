import tkinter as tk
from gui import ApplicationGUI

def main():
    root = tk.Tk()
    root.title("CPM|Middleman-issue")

    app_gui = ApplicationGUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()
