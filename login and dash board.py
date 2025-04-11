import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
# Toggle password visibility
def toggle_password(entry, toggle_btn):
    if entry.cget('show') == '':
        entry.config(show='*')
        toggle_btn.config(text='Show')
    else:
        entry.config(show='')
        toggle_btn.config(text='Hide')

# Show dashboard after login
def show_dashboard(username):
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("400x200")
    dashboard.configure(bg="#e8f5e9")

    tk.Label(dashboard, text=f"Welcome to your dashboard, {username}!",
             font=("Arial", 14, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(pady=40)
    tk.Button(dashboard, text="Logout", command=dashboard.destroy, bg="#c62828", fg="white").pack()

# Login window
def login_window():
    login = tk.Tk()
    login.title("Login")
    login.geometry("400x350")
    login.configure(bg="#e3f2fd")

    def login_user():
        username = entry_username.get()
        password = entry_password.get()

        if not (username and password):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            login.destroy()
            show_dashboard(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_register():
        login.destroy()
        register_window()

    tk.Label(login, text="Login", font=("Arial", 18, "bold"), bg="#e3f2fd").pack(pady=10)

    tk.Label(login, text="Username:", bg="#e3f2fd").pack()
    entry_username = tk.Entry(login, width=30)
    entry_username.pack(pady=5)

    tk.Label(login, text="Password:", bg="#e3f2fd").pack()
    entry_password = tk.Entry(login, show='*', width=30)
    entry_password.pack(pady=5)

    toggle_btn = tk.Button(login, text="Show", bg="#90caf9")
    toggle_btn.pack(pady=2)
    toggle_btn.config(command=lambda: toggle_password(entry_password, toggle_btn))

    # ENTER key behavior for login
    entry_username.bind("<Return>", lambda e: entry_password.focus())
    entry_password.bind("<Return>", lambda e: login_user())

    tk.Button(login, text="Login", command=login_user, bg="#1976d2", fg="white", width=20).pack(pady=15)

    tk.Label(login, text="Don't have an account?", bg="#e3f2fd").pack()
    tk.Button(login, text="Register Here", command=open_register, bg="#4caf50", fg="white").pack()

    login.mainloop()

# Registration window
def register_window():
    register = tk.Tk()
    register.title("Register")
    register.geometry("400x500")
    register.configure(bg="#f3e5f5")

    def register_user():
        name = entry_name.get()
        email = entry_email.get()
        username = entry_username.get()
        password = entry_password.get()
        confirm = entry_confirm.get()

        if not (name and email and username and password and confirm):
            messagebox.showerror("Error", "All fields are required.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)",
                           (name, email, username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            register.destroy()
            login_window()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email already exists.")

    tk.Label(register, text="Register", font=("Arial", 18, "bold"), bg="#f3e5f5").pack(pady=10)

    tk.Label(register, text="Full Name:", bg="#f3e5f5").pack()
    entry_name = tk.Entry(register, width=30)
    entry_name.pack(pady=5)

    tk.Label(register, text="Email:", bg="#f3e5f5").pack()
    entry_email = tk.Entry(register, width=30)
    entry_email.pack(pady=5)

    tk.Label(register, text="Username:", bg="#f3e5f5").pack()
    entry_username = tk.Entry(register, width=30)
    entry_username.pack(pady=5)

    tk.Label(register, text="Password:", bg="#f3e5f5").pack()
    entry_password = tk.Entry(register, show='*', width=30)
    entry_password.pack(pady=5)

    tk.Label(register, text="Confirm Password:", bg="#f3e5f5").pack()
    entry_confirm = tk.Entry(register, show='*', width=30)
    entry_confirm.pack(pady=5)

    toggle_btn1 = tk.Button(register, text="Show", bg="#ce93d8")
    toggle_btn1.pack(pady=2)
    toggle_btn1.config(command=lambda: toggle_password(entry_password, toggle_btn1))

    # ENTER key behavior for registration
    entry_name.bind("<Return>", lambda e: entry_email.focus())
    entry_email.bind("<Return>", lambda e: entry_username.focus())
    entry_username.bind("<Return>", lambda e: entry_password.focus())
    entry_password.bind("<Return>", lambda e: entry_confirm.focus())
    entry_confirm.bind("<Return>", lambda e: register_user())

    tk.Button(register, text="Register", command=register_user, bg="#8e24aa", fg="white", width=20).pack(pady=20)

    tk.Label(register, text="Already have an account?", bg="#f3e5f5").pack()
    tk.Button(register, text="Login Here", command=lambda: [register.destroy(), login_window()], bg="#4caf50", fg="white").pack()

    register.mainloop()

# Initialize and start the app
init_db()
login_window()
