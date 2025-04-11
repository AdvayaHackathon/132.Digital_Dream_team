import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import datetime

# Simulate seller login
current_user = "seller1"

# Initialize DB with required tables and columns
def init_db():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            category TEXT,
            description TEXT,
            price REAL,
            image_path TEXT,
            seller_name TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')

    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Clear input form
def clear_form():
    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_description.delete("1.0", tk.END)
    entry_price.delete(0, tk.END)
    image_path_var.set("")

# Browse image
def browse_image():
    filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
    if filename:
        image_path_var.set(filename)

# Save product
def save_product():
    name = entry_name.get()
    category = entry_category.get()
    description = entry_description.get("1.0", tk.END).strip()
    price = entry_price.get()
    image_path = image_path_var.get()

    if not name or not category or not description or not price or not image_path:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Invalid Input", "Price must be a number.")
        return

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (product_name, category, description, price, image_path, seller_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, category, description, price, image_path, current_user))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Product saved!")
    clear_form()
    load_products()

# Delete product
def delete_product(pid):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (pid,))
    cursor.execute("DELETE FROM messages WHERE product_id=?", (pid,))
    conn.commit()
    conn.close()
    load_products()

# Load products
def load_products():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, category, price, image_path, status FROM products WHERE seller_name=?", (current_user,))
    products = cursor.fetchall()
    conn.close()

    for pid, name, category, price, image_path, status in products:
        frame = tk.Frame(scrollable_frame, bd=1, relief=tk.RIDGE)
        frame.pack(padx=5, pady=5, fill="x")

        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((100, 100))
                img = ImageTk.PhotoImage(img)
                label_img = tk.Label(frame, image=img)
                label_img.image = img
                label_img.grid(row=0, column=0, rowspan=4, padx=5)
            except:
                tk.Label(frame, text="Image Error").grid(row=0, column=0)

        tk.Label(frame, text=f"Name: {name}\nCategory: {category}\nPrice: ₹{price}").grid(row=0, column=1, sticky="w")
        tk.Label(frame, text=f"Status: {status}", fg="blue").grid(row=1, column=1, sticky="w")

        tk.Button(frame, text="Message", command=lambda pid=pid: open_messages(pid), bg="#2196f3", fg="white").grid(row=2, column=1, sticky="e")
        tk.Button(frame, text="Delete", command=lambda pid=pid: delete_product(pid), bg="#e53935", fg="white").grid(row=3, column=1, sticky="e")

# Messaging System
def open_messages(product_id):
    msg_win = tk.Toplevel()
    msg_win.title(f"Messages for Product ID {product_id}")
    msg_win.geometry("400x400")

    frame = tk.Frame(msg_win)
    frame.pack(expand=True, fill="both")

    text_area = tk.Text(frame, wrap="word", state="disabled")
    text_area.pack(expand=True, fill="both")

    def load_messages():
        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT sender, message, timestamp FROM messages WHERE product_id=? ORDER BY id ASC", (product_id,))
        messages = cursor.fetchall()
        conn.close()

        text_area.config(state="normal")
        text_area.delete("1.0", tk.END)
        for sender, msg, ts in messages:
            text_area.insert(tk.END, f"{ts} | {sender}: {msg}\n")
        text_area.config(state="disabled")

    def send_message():
        msg = entry_msg.get()
        if msg.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect("marketplace.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (product_id, sender, receiver, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_id, current_user, "buyer", msg, timestamp))
            conn.commit()
            conn.close()
            entry_msg.delete(0, tk.END)
            load_messages()

    entry_msg = tk.Entry(msg_win, width=40)
    entry_msg.pack(padx=10, pady=5, side="left")
    tk.Button(msg_win, text="Send", command=send_message, bg="green", fg="white").pack(padx=5, pady=5, side="left")

    load_messages()

# GUI Setup
root = tk.Tk()
root.title("Seller Dashboard")
root.geometry("800x700")

# Form for product entry
add_frame = tk.LabelFrame(root, text="Add Product", padx=10, pady=10)
add_frame.pack(padx=10, pady=10, fill="x")

image_path_var = tk.StringVar()

tk.Label(add_frame, text="Name:").grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(add_frame, width=40)
entry_name.grid(row=0, column=1)

tk.Label(add_frame, text="Category:").grid(row=1, column=0, sticky="e")
entry_category = tk.Entry(add_frame, width=40)
entry_category.grid(row=1, column=1)

tk.Label(add_frame, text="Description:").grid(row=2, column=0, sticky="ne")
entry_description = tk.Text(add_frame, width=30, height=3)
entry_description.grid(row=2, column=1)

tk.Label(add_frame, text="Price (₹):").grid(row=3, column=0, sticky="e")
entry_price = tk.Entry(add_frame, width=40)
entry_price.grid(row=3, column=1)

tk.Label(add_frame, text="Image:").grid(row=4, column=0, sticky="e")
tk.Entry(add_frame, textvariable=image_path_var, width=30).grid(row=4, column=1, sticky="w")
tk.Button(add_frame, text="Browse", command=browse_image).grid(row=4, column=1, sticky="e")

tk.Button(add_frame, text="Save Product", command=save_product, bg="green", fg="white").grid(row=5, column=1, pady=10)

# Scrollable product area
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_canvas_frame = tk.Frame(canvas)

scroll_canvas_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scroll_canvas_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

scrollable_frame = scroll_canvas_frame

# Launch
init_db()
load_products()
root.mainloop()
