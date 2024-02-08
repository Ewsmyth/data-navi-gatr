import tkinter as tk
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import os
import csv
from datetime import datetime
import shutil

class QueryPackage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Frame for start datetime
        start_frame = ttk.Frame(self)
        start_frame.pack(pady=5)

        # Label for start date
        start_date_label = ttk.Label(start_frame, text="Start Date:")
        start_date_label.pack(side="left", padx=5)

        # DateEntry widget for start date
        self.start_date_entry = DateEntry(start_frame, date_pattern="yyyy-mm-dd")
        self.start_date_entry.pack(side="left", padx=5)

        # Entry widget for start time
        self.start_time_entry = ttk.Entry(start_frame)
        self.start_time_entry.pack(side="left", padx=5)
        self.start_time_entry.insert(0, "00:00:00")  # Default time value

        # Frame for end datetime
        end_frame = ttk.Frame(self)
        end_frame.pack(pady=5)

        # Label for end date
        end_date_label = ttk.Label(end_frame, text="End Date:")
        end_date_label.pack(side="left", padx=5)

        # DateEntry widget for end date
        self.end_date_entry = DateEntry(end_frame, date_pattern="yyyy-mm-dd")
        self.end_date_entry.pack(side="left", padx=5)

        # Entry widget for end time
        self.end_time_entry = ttk.Entry(end_frame)
        self.end_time_entry.pack(side="left", padx=5)
        self.end_time_entry.insert(0, "23:59:59")  # Default time value

        # Button to submit query with the selected time range
        submit_button = ttk.Button(self, text="Submit", command=self.submit_query)
        submit_button.pack(pady=10)

    def submit_query(self):
        # Get the date and time components from the entry widgets
        start_date = self.start_date_entry.get_date()
        start_time = self.start_time_entry.get()
        end_date = self.end_date_entry.get_date()
        end_time = self.end_time_entry.get()

        # Combine date and time components to form datetime strings
        start_datetime_str = f"{start_date} {start_time}"
        end_datetime_str = f"{end_date} {end_time}"

        # Convert start and end date/time strings to datetime objects
        start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

        print("Start Datetime:", start_datetime)
        print("End Datetime:", end_datetime)

        # Open file dialog to select the folder for saving the filtered database file
        save_folder = filedialog.askdirectory()
        if not save_folder:
            return  # User canceled operation

        print("Selected folder:", save_folder)

        # Print current working directory
        print("Current working directory:", os.getcwd())

        # Get path to the master_database.csv file
        database_folder = os.path.join(os.getcwd(), "database")
        master_database_path = os.path.join(database_folder, "master_database.csv")

        print("Master database path:", master_database_path)

        if not os.path.exists(master_database_path):
            print("master_database.csv file not found.")
            return

        # Filter the data based on the datetime range
        filtered_rows = []
        with open(master_database_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header
            for row in reader:
                up_time_str = row[20]  # Assuming "up_time" is at index 20
                if up_time_str:
                    up_time = datetime.strptime(up_time_str, "%Y-%m-%d %H:%M:%S")
                    if start_datetime <= up_time <= end_datetime:
                        filtered_rows.append(row)
                else:
                    continue

        # Save the filtered data to a new master_database_filtered.csv file in the selected folder
        filtered_master_database_path = os.path.join(save_folder, "master_database_filtered.csv")
        with open(filtered_master_database_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write the header
            writer.writerows(filtered_rows)

        print("Filtered data saved successfully.")

        media_column_index = header.index("media")
        media_files = [row[media_column_index] for row in filtered_rows]

        # Get the downloads directory
        
        downloads_directory = os.path.join(os.getcwd(), "downloads")

        # Check if the downloads directory exists
        if not os.path.exists(downloads_directory):
            print("Downloads directory does not exist.")
            return  # Exit the function or display a message in the GUI

        # Iterate through the extracted file names
        for media_file in media_files:
            # Split the media field by comma to extract individual filenames
            file_names = [f.strip() for f in media_file.split(",") if f.strip()]
            for file_name in file_names:
                # Construct the full path of the file in the downloads directory
                file_path = os.path.join(downloads_directory, file_name)

                print("File path:", file_path)  # Debugging statement

                if os.path.exists(file_path):
                    try:
                        # Copy the file to the selected directory
                        shutil.copy(file_path, save_folder)
                        print(f"File '{file_name}' copied successfully.")
                    except PermissionError:
                        print(f"Permission denied to copy file '{file_name}' to '{save_folder}'.")
                else:
                    print(f"File '{file_name}' does not exist at '{file_path}'.")

        print("All files copied successfully.")

# Sample usage
if __name__ == "__main__":
    root = tk.Tk()
    query_package = QueryPackage(root)
    query_package.pack(expand=True, fill="both")
    root.mainloop()
