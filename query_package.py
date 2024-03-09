import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        # Prompt user to select a folder to save the filtered CSV file
        folder_path = filedialog.askdirectory(title="Select Folder to Save CSV and Media Files")

        # Get start and end datetime values from user input
        start_datetime = datetime.combine(self.start_date_entry.get_date(), 
                                           datetime.strptime(self.start_time_entry.get(), "%H:%M:%S").time())
        end_datetime = datetime.combine(self.end_date_entry.get_date(),
                                         datetime.strptime(self.end_time_entry.get(), "%H:%M:%S").time())

        # Read master_database.csv and filter records based on datetime range
        filtered_rows = []
        with open("database/master_database.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row_datetime = datetime.strptime(row["up_time"], "%Y-%m-%d %H:%M:%S")
                if start_datetime <= row_datetime <= end_datetime:
                    filtered_rows.append(row)

        # Write filtered rows to a new CSV file in the selected folder
        output_file_path = os.path.join(folder_path, "filtered_data.csv")
        with open(output_file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=filtered_rows[0].keys())
            writer.writeheader()
            writer.writerows(filtered_rows)

        # Create a 'media' folder within the selected folder
        media_folder_path = os.path.join(folder_path, "media")
        os.makedirs(media_folder_path, exist_ok=True)

        # Copy media files referenced in the 'media' field to the 'media' folder
        for row in filtered_rows:
            media_files = row.get("media")
            if media_files:
                # Split media field by comma, ignoring spaces
                media_files = [filename.strip() for filename in media_files.split(",")]
                for media_file in media_files:
                    if media_file.startswith('"') and media_file.endswith('"'):
                        media_file = media_file[1:-1]  # Remove quotes if present
                    media_file_path = os.path.join("downloads", media_file)
                    if os.path.exists(media_file_path):
                        shutil.copy(media_file_path, media_folder_path)

        # Inform the user that the operation is complete
        messagebox.showinfo("Success", "Filtered data and media files have been saved.")
