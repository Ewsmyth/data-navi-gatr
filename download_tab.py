import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import paramiko
import threading
import queue
import os

class DownloadsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Server IP Label and Entry
        server_ip_label = ttk.Label(self, text="Server IP:")
        server_ip_label.pack(pady=5)

        self.server_ip_var = tk.StringVar()
        server_ip_entry = ttk.Entry(self, textvariable=self.server_ip_var)
        server_ip_entry.pack(pady=5)

        # Username Label and Entry
        username_label = ttk.Label(self, text="Username:")
        username_label.pack(pady=5)

        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(self, textvariable=self.username_var)
        username_entry.pack(pady=5)

        # App Name Label and Dropdown
        app_name_label = ttk.Label(self, text="App Name:")
        app_name_label.pack(pady=5)

        self.app_name_var = tk.StringVar()
        app_name_options = ["vendify", "interactify"]
        app_name_dropdown = ttk.Combobox(self, textvariable=self.app_name_var, values=app_name_options)
        app_name_dropdown.pack(pady=5)

        # Example Button
        submit_button = ttk.Button(self, text="Submit", command=self.on_submit)
        submit_button.pack(pady=10)

        # Queue to communicate between threads
        self.result_queue = queue.Queue()

    def on_submit(self):
        server_ip = self.server_ip_var.get()
        username = self.username_var.get()
        app_name = self.app_name_var.get()

        # Prompt for the password using a dialog
        password = self.get_ssh_password()

        if password:
            # Get the path to the "downloads" folder in the current directory
            current_directory = os.getcwd()
            downloads_folder = os.path.join(current_directory, "downloads")

            # Create the "downloads" folder if it doesn't exist
            os.makedirs(downloads_folder, exist_ok=True)

            # Run the file copy operation in a separate thread
            copy_thread = SSHCopyThread(self.result_queue, server_ip, username, app_name, password, downloads_folder)
            copy_thread.start()
        else:
            messagebox.showerror("Error", "Files not copied. Please check your input.")

    def get_ssh_password(self):
        # Prompt for password using a pop-up dialog
        return simpledialog.askstring("Password", "Enter your SSH password:", show="*")

class SSHCopyThread(threading.Thread):
    def __init__(self, queue, ip, username, app_name, password, save_directory):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ip = ip
        self.username = username
        self.app_name = app_name
        self.password = password
        self.save_directory = save_directory

    def run(self):
        try:
            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the server
            ssh.connect(self.ip, port=22, username=self.username, password=self.password)

            # Use paramiko to copy files
            scp_command_1 = f'/var/lib/docker/volumes/{self.app_name}-data/_data/{self.app_name}-data.db'
            scp_command_2 = f'/var/lib/docker/volumes/{self.app_name}-uploads/_data/'  # Path to the directory

            # Open an SFTP session to perform the file transfer
            with ssh.open_sftp() as sftp:
                # Copy the database file
                sftp.get(scp_command_1, os.path.join(self.save_directory, f'{self.app_name}-data.db'))

                # Copy the contents of the remote directory into the local directory
                for remote_file in sftp.listdir(scp_command_2):
                    remote_path = f"{scp_command_2}/{remote_file}"
                    local_path = os.path.join(self.save_directory, remote_file)
                    sftp.get(remote_path, local_path)

            # Close the SSH connection
            ssh.close()

            messagebox.showinfo("Success", "Files successfully copied, continue downloading or proceed to the format tab.")
        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Authentication failed. Please check your username and password.")
        except paramiko.SSHException as e:
            messagebox.showerror("Error", f"SSH connection failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
