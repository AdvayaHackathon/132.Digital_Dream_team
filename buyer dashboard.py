import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import datetime

# Simulated logged-in buyer name
current_buyer = "buyer1"

# Ensure database tables exist
def init_db():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    # Create purchases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_name TEXT,
            seller_name TEXT,
            product_id INTEGER,
            product_name TEXT,
            price REAL,
            address TEXT,
            payment_method TEXT,
            timestamp TEXT
        )
    ''')

    # Create messages table (optional)
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

# Load approved products
def load_products():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, price, image_path, seller_name FROM products WHERE status='Approved'")
    products = cursor.fetchall()
    conn.close()

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    for pid, name, price, img_path, seller in products:
        frame = tk.Frame(scrollable_frame, bd=1, relief="solid")
        frame.pack(padx=5, pady=5, fill="x")

        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=photo)
                img_label.image = photo
                img_label.grid(row=0, column=0, rowspan=3, padx=5)
            except:
                tk.Label(frame, text="Image Error").grid(row=0, column=0)

        tk.Label(frame, text=f"Product: {name}").grid(row=0, column=1, sticky="w")
        tk.Label(frame, text=f"Price: ₹{price}").grid(row=1, column=1, sticky="w")
        tk.Label(frame, text=f"Seller: {seller}").grid(row=2, column=1, sticky="w")

        tk.Button(frame, text="Buy Now", bg="green", fg="white",
                  command=lambda pid=pid, name=name, price=price, seller=seller: open_buy_window(pid, name, price, seller)
                  ).grid(row=0, column=2, rowspan=2, padx=10)

# Show tracking window after order
def show_tracking_window(pname, price, seller, address, timestamp):
    track_win = tk.Toplevel(root)
    track_win.title("Track Order")
    track_win.geometry("400x300")

    tk.Label(track_win, text="📦 Order Tracking", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(track_win, text=f"Product: {pname}").pack(pady=5)
    tk.Label(track_win, text=f"Price: ₹{price}").pack(pady=5)
    tk.Label(track_win, text=f"Seller: {seller}").pack(pady=5)
    tk.Label(track_win, text=f"Shipping To:\n{address}", wraplength=350, justify="center").pack(pady=10)
    tk.Label(track_win, text=f"Order Placed: {timestamp}").pack(pady=5)
    tk.Label(track_win, text="Status: 🚚 Shipped - Estimated delivery in 3-5 days", fg="green").pack(pady=10)

# Buy product window
def open_buy_window(pid, pname, price, seller):
    buy_win = tk.Toplevel(root)
    buy_win.title("Buy Product")
    buy_win.geometry("400x450")

    tk.Label(buy_win, text=f"Buying: {pname}", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(buy_win, text=f"Price: ₹{price}").pack(pady=5)

    tk.Label(buy_win, text="Enter Shipping Address:").pack(anchor="w", padx=10)
    address_entry = tk.Text(buy_win, height=4, width=40)
    address_entry.pack(pady=5)

    def proceed_to_payment():
        address = address_entry.get("1.0", tk.END).strip()
        if not address:
            messagebox.showwarning("Input Required", "Please enter a shipping address.")
            return

        # Simulate Razorpay Payment
        pay = messagebox.askyesno("Razorpay Payment", f"Proceed to pay ₹{price} using Razorpay?")
        if not pay:
            return

        # Simulated successful payment
        payment_method = "Razorpay"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO purchases (buyer_name, seller_name, product_id, product_name, price, address, payment_method, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_buyer, seller, pid, pname, price, address, payment_method, timestamp))
        conn.commit()
        conn.close()

        messagebox.showinfo("Order Placed", f"Your order for '{pname}' has been placed successfully!")

        buy_win.destroy()

        # Open tracking window
        show_tracking_window(pname, price, seller, address, timestamp)

    tk.Button(buy_win, text="Proceed to Razorpay Payment", command=proceed_to_payment, bg="#4CAF50", fg="white").pack(pady=20)

# Main GUI setup
root = tk.Tk()
root.title("Buyer Dashboard - Buy Products")
root.geometry("800x600")

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Init DB and Load
init_db()
load_products()

root.mainloop()
