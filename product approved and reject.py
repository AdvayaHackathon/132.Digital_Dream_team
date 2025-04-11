import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas, Entry, Label, Button
from PIL import Image, ImageTk
import sqlite3
import os


def init_db():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if "name" not in columns:
            cursor.execute("DROP TABLE IF EXISTS products")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            description TEXT,
            price REAL,
            seller_username TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'Pending',
            bidding_price REAL DEFAULT 0.0
        )
    ''')

    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    if "bidding_price" not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN bidding_price REAL DEFAULT 0.0")

    conn.commit()
    conn.close()


def approve_products_page(filter_status="All", filter_id="", page=1, per_page=10):
    root = tk.Tk()
    root.title("Approve / Reject Products")
    root.geometry("1300x800")
    root.configure(bg="white")

    offset = (page - 1) * per_page

    filter_frame = tk.Frame(root, bg="white")
    filter_frame.pack(fill="x", pady=10)

    Label(filter_frame, text="Status:", bg="white").grid(row=0, column=0)
    status_entry = Entry(filter_frame)
    status_entry.insert(0, filter_status)
    status_entry.grid(row=0, column=1)

    Label(filter_frame, text="Product ID:", bg="white").grid(row=0, column=2)
    id_entry = Entry(filter_frame)
    id_entry.insert(0, filter_id)
    id_entry.grid(row=0, column=3)

    def apply_filters():
        status_val = status_entry.get()
        id_val = id_entry.get()
        root.destroy()
        approve_products_page(status_val, id_val, page=1, per_page=per_page)

    Button(filter_frame, text="Filter", command=apply_filters, bg="#4caf50", fg="white").grid(row=0, column=4, padx=10)

    canvas = Canvas(root, bg="white")
    frame = tk.Frame(canvas, bg="white")
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind("<Configure>", on_configure)

    headers = ["Image", "Product Name", "Category", "Description", "Price", "Bidding Price", "Update Bid", "Status", "Approve", "Reject"]
    for col, text in enumerate(headers):
        Label(frame, text=text, bg="#aed581", fg="black", font=("Arial", 10, "bold"), padx=10, pady=5).grid(row=0, column=col, sticky="nsew")

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    query = "SELECT id, name, category, description, price, bidding_price, image_path, status FROM products"
    count_query = "SELECT COUNT(*) FROM products"
    where_clauses = []
    params = []

    if filter_status != "All":
        where_clauses.append("status = ?")
        params.append(filter_status)
    if filter_id:
        where_clauses.append("id = ?")
        params.append(filter_id)

    if where_clauses:
        clause = " WHERE " + " AND ".join(where_clauses)
        query += clause
        count_query += clause

    query += " LIMIT ? OFFSET ?"
    cursor.execute(query, (*params, per_page, offset))
    products = cursor.fetchall()

    cursor.execute(count_query, params)
    total_products = cursor.fetchone()[0]
    conn.close()

    images = []

    def zoom_image_popup(image_path, product_name):
        if not os.path.exists(image_path):
            messagebox.showerror("Error", "Image not found.")
            return
        zoom_window = tk.Toplevel(root)
        zoom_window.title(product_name)
        img = Image.open(image_path)
        img = img.resize((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        images.append(img_tk)
        Label(zoom_window, image=img_tk).pack()
        Label(zoom_window, text=product_name, font=("Arial", 14, "bold"), pady=10).pack()

    for row_idx, (pid, name, category, desc, price, bidding_price, img_path, status) in enumerate(products, start=1):
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image: {e}")
                img = Image.new("RGB", (100, 100), color="gray")
                img_tk = ImageTk.PhotoImage(img)
        else:
            img = Image.new("RGB", (100, 100), color="gray")
            img_tk = ImageTk.PhotoImage(img)

        images.append(img_tk)
        img_label = Label(frame, image=img_tk, bg="white", cursor="hand2")
        img_label.grid(row=row_idx, column=0, padx=5, pady=5)
        img_label.bind("<Button-1>", lambda e, path=img_path, pname=name: zoom_image_popup(path, pname))

        name = name if name else "Unnamed Product"
        Label(frame, text=name, bg="white").grid(row=row_idx, column=1)
        Label(frame, text=category, bg="white").grid(row=row_idx, column=2)
        Label(frame, text=desc[:60] + "...", bg="white", wraplength=200).grid(row=row_idx, column=3)
        Label(frame, text=f"₹{price}", bg="white").grid(row=row_idx, column=4)
        Label(frame, text=f"₹{bidding_price}", bg="white").grid(row=row_idx, column=5)

        Button(frame, text="Update Bid", bg="#2196f3", fg="white",
               command=lambda pid=pid: update_bidding_price(pid, root)).grid(row=row_idx, column=6)

        color = "#fff9c4" if status == "Pending" else "#c8e6c9" if status == "Approved" else "#ffcdd2"
        Label(frame, text=status, bg=color).grid(row=row_idx, column=7)

        Button(frame, text="Approve", bg="#4caf50", fg="white", command=lambda pid=pid: approve_product(pid, root)).grid(row=row_idx, column=8)
        Button(frame, text="Reject", bg="#f44336", fg="white", command=lambda pid=pid: reject_product(pid, root)).grid(row=row_idx, column=9)

    root.mainloop()


def update_bidding_price(product_id, root):
    def save_price():
        try:
            new_price = float(price_entry.get())
            conn = sqlite3.connect("marketplace.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET bidding_price=? WHERE id=?", (new_price, product_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Bidding price updated.")
            popup.destroy()
            root.destroy()
            approve_products_page()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid price.")

    popup = tk.Toplevel(root)
    popup.title("Update Bidding Price")
    Label(popup, text="Enter new bidding price:").pack(padx=10, pady=10)
    price_entry = Entry(popup)
    price_entry.pack(padx=10, pady=5)
    Button(popup, text="Save", command=save_price, bg="#2196f3", fg="white").pack(pady=10)


def approve_product(product_id, root):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET status='Approved' WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Approved", "Product has been approved.")
    root.destroy()
    approve_products_page()


def reject_product(product_id, root):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET status='Rejected' WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Rejected", "Product has been rejected.")
    root.destroy()
    approve_products_page()


# Run App
init_db()
approve_products_page()
