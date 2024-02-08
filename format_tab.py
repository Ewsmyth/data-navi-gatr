import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sqlite3
import datetime
import csv

class FormatTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create GUI elements for the Format Tab
        self.app_name_label = tk.Label(self, text="Select App Name:")
        self.app_name_label.pack(pady=5)

        self.app_name_var = tk.StringVar()
        self.app_name_combobox = ttk.Combobox(self, textvariable=self.app_name_var, values=["interactify", "vendify"])
        self.app_name_combobox.pack(pady=5)

        # Other GUI elements
        self.file_path_label = tk.Label(self, text="Selected File: None")
        self.file_path_label.pack(pady=10)

        self.select_file_button = tk.Button(self, text="Select .db File", command=self.select_file)
        self.select_file_button.pack(pady=10)

        self.export_button = tk.Button(self, text="Format and Export", command=self.export_data)
        self.export_button.pack(pady=10)

        self.db_file_path = None  # Variable to store the selected .db file path

    def select_file(self):
        app_name = self.app_name_var.get()
        if not app_name:
            tk.messagebox.showerror("Error", "Please select an App Name.")
            return

        downloads_folder = os.path.join(os.getcwd(), "downloads")
        db_file_path = os.path.join(downloads_folder, f"{app_name}-data.db")

        if os.path.exists(db_file_path):
            self.file_path_label.config(text="Selected File: " + db_file_path)
            self.db_file_path = db_file_path  # Store the selected file path
        else:
            tk.messagebox.showerror("Error", f"No {app_name}-data.db file found in the downloads folder.")

    def export_data(self):
        try:
            app_name = self.app_name_var.get()

            if not app_name:
                tk.messagebox.showerror("Error", "Please select an App Name.")
                return

            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()

            # Execute SQL query based on selected App Name
            if app_name == "vendify":
                cursor.execute("""
                    SELECT
                        user.id || '<vendifyID>' AS tx_id,
                        user.username || '<vendifyUsr>' AS tx_id2,
                        'post' AS event,
                        post.id || '<vendifyObj>' AS content_id,
                        NULL AS rx_id,
                        NULL AS rx_id2,
                        post.title AS content_txt,
                        GROUP_CONCAT(media.media_url || ', ' || post.cover_photo_url, ', ') AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', post.created_at) AS up_time,
                        post.created_at AS initial_time
                    FROM post
                    JOIN user ON post.author_id = user.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY post.id

                    UNION ALL

                    SELECT
                        order_table.purchaser_id || '<vendifyID>' AS tx_id,
                        (SELECT username FROM user WHERE id = order_table.purchaser_id) || '<vendifyUsr>' AS tx_id2,
                        'order' AS event,
                        order_item.post_id || '<vendifyObj>' AS content_id,
                        order_item.vendor_id || '<vendifyID>' AS rx_id,
                        (SELECT username FROM user WHERE id = order_item.vendor_id) || '<vendifyUsr>' AS rx_id2,
                        order_table.order_status AS content_txt,
                        NULL AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        order_table.shipping_address || ' ' || order_table.shipping_city || ' ' || order_table.shipping_state || ' ' || order_table.shipping_country || ' ' || CAST(order_table.shipping_zipcode AS TEXT) AS location,
                        order_table.phone_number AS phone,
                        order_table.card_number AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', order_table.updated_at) AS up_time,
                        order_table.created_at AS initial_time
                    FROM "order" AS order_table
                    JOIN order_item ON order_table.id = order_item.order_id
                    GROUP BY order_table.id, order_item.post_id, order_item.vendor_id

                    UNION ALL

                    SELECT
                        user.id || '<vendifyID>' AS tx_id,
                        user.username || '<vendifyUsr>' AS tx_id2,
                        'user_acct' AS event,
                        NULL AS content_id,
                        NULL AS rx_id,
                        NULL AS rx_id2,
                        NULL AS content_txt,
                        NULL AS media,
                        NULL email,
                        user.password AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        user.authority AS authority,
                        user.is_active AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', user.updated_at) AS up_time,
                        user.created_at AS initial_time
                    FROM user
                    ORDER BY up_time DESC;
                """)
            elif app_name == "interactify":
                cursor.execute("""
                    SELECT
                        user.id || '<interactifyID>' AS tx_id,
                        user.username || '<interactifyUsr>' AS tx_id2,
                        'post' AS event,
                        post.id || '<interactifyObj>' AS content_id,
                        NULL AS rx_id,
                        NULL AS rx_id2,
                        post.content AS content_txt,
                        GROUP_CONCAT(media.media_url, ', ') AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', post.updated_at) AS up_time,
                        NULL AS initial_time
                    FROM post
                    JOIN user ON post.author_id = user.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY post.id

                    UNION ALL

                    SELECT
                        likes.liked_by || '<interactifyID>' AS tx_id,
                        user_like.username || '<interactifyUsr>' AS tx_id2,
                        'like' AS event,
                        likes.liked_post || '<interactifyObj>' AS content_id,
                        post.author_id || '<interactifyID>' AS rx_id,
                        user_post.username || '<interactifyUsr>' AS rx_id2,
                        NULL AS content_txt,
                        NULL AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', likes.updated_at) AS up_time,
                        NULL AS initial_time
                    FROM likes
                    JOIN post ON likes.liked_post = post.id
                    JOIN user AS user_like ON likes.liked_by = user_like.id
                    JOIN user AS user_post ON post.author_id = user_post.id

                    UNION ALL

                    SELECT
                        comment.user_id || '<interactifyID>' AS tx_id,
                        user_comment.username || '<interactifyUsr>' AS tx_id2,
                        'comment' AS event,
                        comment.post_id || '<interactifyObj>' AS content_id,
                        post.author_id || '<interactifyID>' AS rx_id,
                        user_post.username || '<interactifyUsr>' AS rx_id2,
                        comment.content AS content_txt,
                        GROUP_CONCAT(media.media_url, ', ') AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', comment.updated_at) AS up_time,
                        NULL AS initial_time
                    FROM comment
                    JOIN post ON comment.post_id = post.id
                    JOIN user AS user_comment ON comment.user_id = user_comment.id
                    JOIN user AS user_post ON post.author_id = user_post.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY comment.id

                    UNION ALL

                    SELECT
                        follower.follower_id || '<interactifyID>' AS tx_id,
                        user_follower.username || '<interactifyUsr>' AS tx_id2,
                        'follow' AS event,
                        NULL AS content_id,
                        follower.following_id || '<interactifyID>' AS rx_id,
                        user_following.username || '<interactifyUsr>' AS rx_id2,
                        NULL AS content_txt,
                        NULL AS media,
                        NULL AS email,
                        NULL AS authentication,
                        NULL AS firstname,
                        NULL AS lastname,
                        NULL AS authority,
                        NULL AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', follower.created_at) AS up_time,
                        NULL AS initial_time
                    FROM follower
                    JOIN user AS user_follower ON follower.follower_id = user_follower.id
                    JOIN user AS user_following ON follower.following_id = user_following.id

                    UNION ALL

                    SELECT
                        user.id || '<interactifyID>' AS tx_id,
                        user.username || '<interactifyUsr>' AS tx_id2,
                        'user_acct' AS event,
                        NULL AS content_id,
                        NULL AS rx_id,
                        NULL AS rx_id2,
                        user.bio AS content_txt,
                        user.profile_picture AS media,
                        user.email AS email,
                        user.password AS authentication,
                        user.first_name AS firstname,
                        user.last_name AS lastname,
                        user.authority AS authority,
                        user.acct_stat AS acct_stat,
                        NULL AS location,
                        NULL AS phone,
                        NULL AS finance_cd,
                        strftime('%Y-%m-%d %H:%M:%S', user.updated_at) AS up_time,
                        user.created_at AS initial_time
                    FROM user
                    ORDER BY up_time DESC;
                """)
            else:
                tk.messagebox.showerror("Error", "Invalid App Name selected.")
                return

            # Fetch all results
            results = cursor.fetchall()

            # Specify the CSV output file name
            formatted_dir = os.path.join(os.getcwd(), "formatted")
            if not os.path.exists(formatted_dir):
                os.makedirs(formatted_dir)

            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_filename = f"{app_name}_{current_datetime}.csv"
            output_file = os.path.join(formatted_dir, csv_filename)

            # Write data to CSV file
            with open(output_file, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                csv_writer.writerow([i[0] for i in cursor.description])
                # Write data
                csv_writer.writerows(results)

            tk.messagebox.showinfo("Export Successful", f"Data exported successfully to {csv_filename} in the 'formatted' directory!")
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FormatTab(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
