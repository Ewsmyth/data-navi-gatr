import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import paramiko

class InitializeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Server IP Label and Entry
        server_ip_label = ttk.Label(self, text="Server IP:")
        server_ip_label.pack(pady=5)

        self.server_ip_entry = ttk.Entry(self)
        self.server_ip_entry.pack(pady=5)

        # Username Label and Entry
        username_label = ttk.Label(self, text="Username:")
        username_label.pack(pady=5)

        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        # Example Button
        submit_button = ttk.Button(self, text="Submit", command=self.on_submit)
        submit_button.pack(pady=10)

    def on_submit(self):
        server_ip = self.server_ip_entry.get()
        username = self.username_entry.get()

        # Prompt for the password using a dialog
        password = self.get_ssh_password()

        if password:
            try:
                # Open SSH connection
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server_ip, username=username, password=password)

                # Execute chown commands
                chown_commands = [
                    "sudo chown {0}:{0} /var/lib/docker".format(username),
                    "sudo chown -R {0}:{0} /var/lib/docker/volumes".format(username)
                ]

                for chown_command in chown_commands:
                    stdin, stdout, stderr = ssh.exec_command(chown_command)
                    output = stdout.read().decode("utf-8")
                    error = stderr.read().decode("utf-8")

                    if error:
                        messagebox.showerror("Error", f"Error executing command '{chown_command}': {error}")
                        break

                # Close the SSH connection
                ssh.close()

                messagebox.showinfo("Success", f"{username} now has access to the necessary directories, proceed to the download tab.")
            except paramiko.AuthenticationException:
                messagebox.showerror("Error", "Authentication failed. Please check your username and password.")
            except paramiko.SSHException as e:
                messagebox.showerror("Error", f"SSH connection failed: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def get_ssh_password(self):
        # Prompt for password using a pop-up dialog
        return simpledialog.askstring("Password", "Enter your SSH password:", show="*")
