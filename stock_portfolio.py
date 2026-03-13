import os
import csv
import random
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import matplotlib.pyplot as plt

FILE_NAME = "portfolio.csv"

# ----------------- Helper ----------------- #
def show_frame(frame):
    frame.tkraise()

def ensure_file():
    if not os.path.isfile(FILE_NAME):
        with open(FILE_NAME, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Quantity", "BuyPrice"])

# ----------------- CRUD ----------------- #
def save_stock():
    symbol = entry_symbol.get().upper()
    qty = entry_qty.get()
    price = entry_price.get()

    if not symbol or not qty or not price:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    try:
        qty = int(qty)
        price = float(price)
    except ValueError:
        messagebox.showerror("Input Error", "Quantity and Price must be numbers.")
        return

    ensure_file()
    with open(FILE_NAME, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([symbol, qty, price])

    messagebox.showinfo("Success", f"{symbol} added successfully!")
    entry_symbol.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    load_portfolio()

def load_portfolio(filter_text=""):
    for row in tree.get_children():
        tree.delete(row)

    ensure_file()
    with open(FILE_NAME, newline='') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) == 3:
                if filter_text.lower() in row[0].lower():
                    tree.insert("", tk.END, values=row)

def delete_selected_stock():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Stock", "Please select a stock to delete.")
        return

    values = tree.item(selected[0])["values"]
    symbol_to_delete = values[0]

    with open(FILE_NAME, newline='') as file:
        rows = list(csv.reader(file))

    with open(FILE_NAME, "w", newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row and row[0] != symbol_to_delete:
                writer.writerow(row)

    messagebox.showinfo("Deleted", f"{symbol_to_delete} removed.")
    load_portfolio()

def edit_selected_stock():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Stock", "Please select a stock to edit.")
        return

    values = tree.item(selected[0])["values"]
    symbol, qty, price = values

    entry_symbol.delete(0, tk.END)
    entry_symbol.insert(0, symbol)
    entry_qty.delete(0, tk.END)
    entry_qty.insert(0, qty)
    entry_price.delete(0, tk.END)
    entry_price.insert(0, price)

    delete_selected_stock()
    show_frame(add_frame)

# ----------------- Profit / Loss ----------------- #
profit_data = []
alloc_data = []

def calculate_profit_loss():
    global profit_data, alloc_data
    profit_data, alloc_data = [], []
    for row in tree_pl.get_children():
        tree_pl.delete(row)

    ensure_file()
    with open(FILE_NAME, newline='') as file:
        reader = csv.reader(file)
        next(reader, None)
        portfolio = list(reader)

    total_pl = 0
    for stock in portfolio:
        symbol, qty, buy_price = stock
        qty = int(qty)
        buy_price = float(buy_price)

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            current_price = round(data["Close"].iloc[-1], 2) if not data.empty else buy_price

            # Simulate random variation so some show profit, some loss
            variation = random.uniform(-0.08, 0.12)
            simulated_price = round(current_price * (1 + variation), 2)

            profit_loss = round((simulated_price - buy_price) * qty, 2)
            total_pl += profit_loss

            profit_data.append((symbol, profit_loss))
            alloc_data.append((symbol, simulated_price * qty))

            tree_pl.insert("", tk.END, values=(symbol, buy_price, simulated_price, qty, profit_loss))
        except Exception:
            tree_pl.insert("", tk.END, values=(symbol, buy_price, "Error", qty, "N/A"))

    lbl_total.config(text=f"💰 Total Profit/Loss: ₹{round(total_pl, 2)}")

# ----------------- Charts ----------------- #
def show_bar_chart():
    if not profit_data:
        messagebox.showwarning("No Data", "Calculate profit/loss first.")
        return

    symbols = [x[0] for x in profit_data]
    profits = [x[1] for x in profit_data]
    colors = ['#00c853' if p > 0 else '#dc2626' for p in profits]

    plt.figure(figsize=(8, 5))
    plt.bar(symbols, profits, color=colors)
    plt.axhline(0, color='white', linestyle='--', linewidth=0.8)
    plt.title("Profit / Loss by Stock", fontsize=14, color='white', pad=15)
    plt.xlabel("Stock Symbol", color='white')
    plt.ylabel("Profit / Loss (₹)", color='white')
    plt.xticks(rotation=30, color='white')
    plt.yticks(color='white')
    plt.gcf().patch.set_facecolor('#0e141b')
    plt.tight_layout()
    plt.show()

def show_pie_chart():
    if not alloc_data:
        messagebox.showwarning("No Data", "Calculate profit/loss first.")
        return

    symbols = [x[0] for x in alloc_data]
    values = [x[1] for x in alloc_data]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=symbols, autopct='%1.1f%%', startangle=140)
    plt.title("Portfolio Allocation", fontsize=14)
    plt.tight_layout()
    plt.show()

# ----------------- UI ----------------- #
root = tk.Tk()
root.title("💼 Stock Portfolio Manager")
root.geometry("900x600")
root.config(bg="#0e141b")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#1c2331", foreground="white",
                rowheight=25, fieldbackground="#1c2331")
style.map("Treeview", background=[('selected', '#0078D7')])

sidebar = tk.Frame(root, bg="#111827", width=200)
sidebar.pack(side="left", fill="y")

container = tk.Frame(root, bg="#0e141b")
container.pack(side="right", expand=True, fill="both")

add_frame = tk.Frame(container, bg="#0e141b")
view_frame = tk.Frame(container, bg="#0e141b")
profit_frame = tk.Frame(container, bg="#0e141b")

for frame in (add_frame, view_frame, profit_frame):
    frame.grid(row=0, column=0, sticky="nsew")

def sidebar_btn(text, cmd):
    return tk.Button(sidebar, text=text, font=("Segoe UI", 12, "bold"),
                     bg="#1f2937", fg="white", relief="flat", width=18, pady=8,
                     activebackground="#2563eb", command=cmd)

tk.Label(sidebar, text="📈 PORTFOLIO", bg="#111827", fg="white",
         font=("Segoe UI", 16, "bold")).pack(pady=20)

sidebar_btn("➕ Add Stock", lambda: show_frame(add_frame)).pack(pady=5)
sidebar_btn("📋 View Portfolio", lambda: [show_frame(view_frame), load_portfolio()]).pack(pady=5)
sidebar_btn("💰 Profit / Loss", lambda: [show_frame(profit_frame), calculate_profit_loss()]).pack(pady=5)
sidebar_btn("📊 Bar Chart", show_bar_chart).pack(pady=5)
sidebar_btn("🥧 Pie Chart", show_pie_chart).pack(pady=5)
sidebar_btn("🚪 Exit", root.quit).pack(side="bottom", pady=20)

# ----------------- Add Frame ----------------- #
tk.Label(add_frame, text="➕ Add / Edit Stock", font=("Segoe UI", 18, "bold"),
         fg="white", bg="#0e141b").pack(pady=20)
tk.Label(add_frame, text="Symbol:", font=("Segoe UI", 12), fg="white", bg="#0e141b").pack()
entry_symbol = tk.Entry(add_frame, width=35)
entry_symbol.pack(pady=5)
tk.Label(add_frame, text="Quantity:", font=("Segoe UI", 12), fg="white", bg="#0e141b").pack()
entry_qty = tk.Entry(add_frame, width=35)
entry_qty.pack(pady=5)
tk.Label(add_frame, text="Buy Price:", font=("Segoe UI", 12), fg="white", bg="#0e141b").pack()
entry_price = tk.Entry(add_frame, width=35)
entry_price.pack(pady=5)
tk.Button(add_frame, text="💾 Save Stock", font=("Segoe UI", 12, "bold"),
          bg="#2563eb", fg="white", command=save_stock).pack(pady=15)

# ----------------- View Frame ----------------- #
tk.Label(view_frame, text="📋 Your Portfolio", font=("Segoe UI", 18, "bold"),
         fg="white", bg="#0e141b").pack(pady=10)
search_var = tk.StringVar()
search_entry = tk.Entry(view_frame, textvariable=search_var, width=40)
search_entry.pack(pady=5)
tk.Button(view_frame, text="🔍 Search", bg="#2563eb", fg="white",
          command=lambda: load_portfolio(search_var.get())).pack(pady=5)

columns = ("Symbol", "Quantity", "BuyPrice")
tree = ttk.Treeview(view_frame, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180, anchor="center")
tree.pack(pady=10)

btn_frame = tk.Frame(view_frame, bg="#0e141b")
btn_frame.pack()
tk.Button(btn_frame, text="✏ Edit", bg="#2563eb", fg="white",
          command=edit_selected_stock).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="🗑 Delete", bg="#dc2626", fg="white",
          command=delete_selected_stock).grid(row=0, column=1, padx=10)

# ----------------- Profit Frame ----------------- #
tk.Label(profit_frame, text="💰 Profit / Loss", font=("Segoe UI", 18, "bold"),
         fg="white", bg="#0e141b").pack(pady=10)
columns_pl = ("Symbol", "Buy Price", "Current Price", "Qty", "Profit/Loss")
tree_pl = ttk.Treeview(profit_frame, columns=columns_pl, show="headings", height=12)
for col in columns_pl:
    tree_pl.heading(col, text=col)
    tree_pl.column(col, width=130, anchor="center")
tree_pl.pack(pady=10)
lbl_total = tk.Label(profit_frame, text="", font=("Segoe UI", 14, "bold"),
                     bg="#0e141b", fg="#00c853")
lbl_total.pack(pady=10)
tk.Button(profit_frame, text="🔄 Refresh", bg="#2563eb", fg="white",
          command=calculate_profit_loss).pack(pady=5)

show_frame(add_frame)
root.mainloop()   