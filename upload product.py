import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import os

# Simulated logged-in user
current_user = "seller1"

# Initialize SQLite DB with required columns
def init_db():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')

    expected_columns = {
        "product_name": "TEXT",
        "category": "TEXT",
        "description": "TEXT",
        "price": "REAL",
        "image_path": "TEXT",
        "seller_name": "TEXT",
        "status": "TEXT DEFAULT 'Pending'"
    }

    cursor.execute("PRAGMA table_info(products)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    for column, dtype in expected_columns.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {column} {dtype}")

    conn.commit()
    conn.close()

# Clear input fields
def clear_form():
    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_description.delete("1.0", tk.END)
    entry_price.delete(0, tk.END)
    image_path_var.set("")

# Image browser
def browse_image():
    filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
    if filename:
        image_path_var.set(filename)

# Save product to DB
def save_product():
    name = entry_name.get()
    category = entry_category.get()
    description = entry_description.get("1.0", tk.END).strip()
    price = entry_price.get()
    image_path = image_path_var.get()

    if not name or not category or not description or not price or not image_path:
        messagebox.showerror("Input Error", "Please fill in all fields and choose an image.")
        return

    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Invalid Price", "Price must be a number.")
        return

    try:
        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (product_name, category, description, price, image_path, seller_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, description, price, image_path, current_user, "Pending"))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product saved successfully!")
        clear_form()
        load_products()
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# Load seller products
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

        # Load image
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((100, 100))
                img = ImageTk.PhotoImage(img)
                label_img = tk.Label(frame, image=img)
                label_img.image = img
                label_img.grid(row=0, column=0, rowspan=3, padx=5)
            except:
                tk.Label(frame, text="Image error").grid(row=0, column=0)

        # Product info
        tk.Label(frame, text=f"Name: {name}\nCategory: {category}\nPrice: ₹{price}").grid(row=0, column=1, sticky="w")
        tk.Label(frame, text=f"Status: {status}", fg="blue").grid(row=1, column=1, sticky="w")
        tk.Button(frame, text="Delete", command=lambda pid=pid: delete_product(pid), bg="#e53935", fg="white").grid(row=2, column=1, sticky="e")

# Delete product from DB
def delete_product(pid):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    load_products()

# GUI setup
root = tk.Tk()
root.title("Seller Dashboard")
root.geometry("800x700")

# Add product section
add_frame = tk.LabelFrame(root, text="Add New Product", padx=10, pady=10)
add_frame.pack(padx=10, pady=10, fill="x")

image_path_var = tk.StringVar()

tk.Label(add_frame, text="Product Name:").grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(add_frame, width=40)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(add_frame, text="Category:").grid(row=1, column=0, sticky="e")
entry_category = tk.Entry(add_frame, width=40)
entry_category.grid(row=1, column=1, padx=5, pady=5)

tk.Label(add_frame, text="Description:").grid(row=2, column=0, sticky="ne")
entry_description = tk.Text(add_frame, width=30, height=4)
entry_description.grid(row=2, column=1, padx=5, pady=5)

tk.Label(add_frame, text="Price (₹):").grid(row=3, column=0, sticky="e")
entry_price = tk.Entry(add_frame, width=40)
entry_price.grid(row=3, column=1, padx=5, pady=5)

tk.Label(add_frame, text="Product Image:").grid(row=4, column=0, sticky="e")
tk.Entry(add_frame, textvariable=image_path_var, width=30).grid(row=4, column=1, sticky="w")
tk.Button(add_frame, text="Browse", command=browse_image).grid(row=4, column=1, sticky="e")

tk.Button(add_frame, text="Save Product", command=save_product, bg="#4caf50", fg="white").grid(row=5, column=1, pady=10)

# Product list section with scrollbar
scroll_canvas = tk.Canvas(root)
scroll_canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=scroll_canvas.yview)
scrollbar.pack(side="right", fill="y")

scroll_canvas.configure(yscrollcommand=scrollbar.set)
scroll_canvas.bind('<Configure>', lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))

scrollable_frame = tk.Frame(scroll_canvas)
scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Run the app
init_db()
load_products()
root.mainloop()
