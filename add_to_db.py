import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import hashlib

class AddToDb(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Label indicating the purpose of the tab
        label = tk.Label(self, text="This is the add to database tab")
        label.pack(pady=10)

        # Button to select a file
        self.file_path_label = tk.Label(self, text="Selected File: None")
        self.file_path_label.pack(pady=5)

        self.select_file_button = tk.Button(self, text="Select File", command=self.select_file)
        self.select_file_button.pack(pady=5)

        # Button to add selected file to the database
        self.add_to_db_button = tk.Button(self, text="Add to Database", command=self.add_to_database)
        self.add_to_db_button.pack(pady=5)

    def select_file(self):
        # Default directory path for the formatted folder in the same directory as main.py
        default_dir = os.path.join(os.getcwd(), "formatted")
        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title="Select File",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.file_path_label.config(text="Selected File: " + file_path)
        else:
            messagebox.showwarning("Warning", "No file selected or file is not a CSV.")

    def add_to_database(self):
        # Get the selected file path
        selected_file_path = self.file_path_label.cget("text")[14:].strip()

        # Check if the selected file is a CSV file
        if not selected_file_path.endswith(".csv"):
            messagebox.showwarning("Warning", "Please select a CSV file.")
            return

        # Get the database directory path
        database_dir = os.path.join(os.getcwd(), "database")

        # Create the database directory if it doesn't exist
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)

        # Set the path for the master_database.csv file
        master_database_path = os.path.join(database_dir, "master_database.csv")

        # Check if the master_database.csv file exists
        master_exists = os.path.exists(master_database_path)

        # Predetermined header for the master_database.csv file
        predetermined_header = "tx_id,tx_id2,event,content_id,rx_id,rx_id2,content_txt,media,email,authentication,firstname,lastname,authority,acct_stat,location,phone,finance_cd,up_time,initial_time,trsid\n"  # Modify this as per your column names

        # Write mode: 'w' for first time, 'a' for subsequent times
        with open(selected_file_path, 'r') as selected_file:
            # Read the contents of the selected file
            selected_data = selected_file.readlines()

            # Remove the header from the selected data (assuming the first row is the header)
            header = selected_data[0].strip().split(',')
            selected_data = selected_data[1:]

            # Initialize a list to store rows with the new "trsid" field
            rows_with_trsid = []

            # Iterate over each row and create the "trsid" field
            for row in selected_data:
                row_values = row.strip().split(',')
                # Generate a unique identifier using a hash function
                trsid = hashlib.sha256(','.join(row_values).encode()).hexdigest()
                # Append the generated "trsid" to the row
                row_with_trsid = ','.join(row_values + [trsid])
                rows_with_trsid.append(row_with_trsid)

        # If it's the first time, write the predetermined header
        if not master_exists:
            with open(master_database_path, 'w') as master_database_file:
                master_database_file.write(predetermined_header)

        # Append rows with the new "trsid" field to the master_database.csv file
        with open(master_database_path, 'a') as master_database_file:
            # If it's the first time, write the predetermined header
            if not master_exists:
                master_database_file.write(predetermined_header)
            for row in rows_with_trsid:
                master_database_file.write(row + '\n')

        # Remove duplicate trsid values from the master_database.csv file
        if os.path.exists(master_database_path):
            with open(master_database_path, 'r') as master_database_file:
                lines = master_database_file.readlines()
            # Keep track of unique trsid values
            unique_trsids = set()
            unique_lines = []
            for line in lines:
                trsid = line.strip().split(',')[-1]
                if trsid not in unique_trsids:
                    unique_lines.append(line)
                    unique_trsids.add(trsid)
            # Rewrite the file with unique trsid values
            with open(master_database_path, 'w') as master_database_file:
                for line in unique_lines:
                    master_database_file.write(line)

        messagebox.showinfo("Success", "Data added to master database successfully.")
