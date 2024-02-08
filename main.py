import tkinter as tk
from tkinter import ttk
from initialize_tab import InitializeTab
from download_tab import DownloadsTab
from format_tab import FormatTab
from add_to_db import AddToDb
from query_package import QueryPackage

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Data Navi Gatr")
        self.geometry("600x400")

        # Create the tab control
        self.tabControl = ttk.Notebook(self)

        # Create individual tabs
        initialize_tab = InitializeTab(self.tabControl)
        download_tab = DownloadsTab(self.tabControl)
        format_tab = FormatTab(self.tabControl)  # Pass self.tabControl as parent
        add_to_db = AddToDb(self.tabControl)
        query_package = QueryPackage(self.tabControl)

        # Add tabs to the tab control
        self.tabControl.add(initialize_tab, text="Initialize")
        self.tabControl.add(download_tab, text="Download")
        self.tabControl.add(format_tab, text="Format")
        self.tabControl.add(add_to_db, text="Add to DB") 
        self.tabControl.add(query_package, text="Q & P")

        # Pack the tab control
        self.tabControl.pack(expand=1, fill="both")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
