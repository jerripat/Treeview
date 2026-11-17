"""Customer Management System - Tkinter and SQLite."""

import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

DB_FILE = Path(__file__).resolve().parent / "customer.db"


def setup_database():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("PRAGMA busy_timeout=10000")
    existing_table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='customers'"
    ).fetchone() is not None

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                sort_order INTEGER
            )
        """)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(customers)")}

        # Safely adapt older databases without deleting customer records.
        if "firstname" not in cols:
            conn.execute("ALTER TABLE customers ADD COLUMN firstname TEXT NOT NULL DEFAULT ''")
        if "lastname" not in cols:
            conn.execute("ALTER TABLE customers ADD COLUMN lastname TEXT NOT NULL DEFAULT ''")
        if "zipcode" not in cols:
            conn.execute("ALTER TABLE customers ADD COLUMN zipcode TEXT")
            if "zip" in cols:
                conn.execute("UPDATE customers SET zipcode = zip")
        if "sort_order" not in cols:
            conn.execute("ALTER TABLE customers ADD COLUMN sort_order INTEGER")

        if "name" in cols:
            for rowid, full_name, first, last in conn.execute(
                "SELECT rowid, name, firstname, lastname FROM customers"
            ).fetchall():
                if not first and not last and full_name:
                    first_name, _, last_name = full_name.strip().partition(" ")
                    conn.execute(
                        "UPDATE customers SET firstname=?, lastname=? WHERE rowid=?",
                        (first_name, last_name, rowid),
                    )

        # Old schemas may require the legacy `name` column on INSERT.
        # Rebuild the table so new inserts use only first/last name.
        if "name" in cols:
            conn.execute("""
                CREATE TABLE customers_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    city TEXT,
                    state TEXT,
                    zipcode TEXT,
                    sort_order INTEGER
                )
            """)
            conn.execute("""
                INSERT INTO customers_new
                (id, firstname, lastname, address, phone, email, city, state, zipcode, sort_order)
                SELECT rowid, firstname, lastname, address, phone, email,
                       city, state, zipcode, sort_order
                FROM customers
            """)
            conn.execute("DROP TABLE customers")
            conn.execute("ALTER TABLE customers_new RENAME TO customers")

        rows = conn.execute(
            "SELECT rowid FROM customers WHERE sort_order IS NULL "
            "ORDER BY rowid"
        ).fetchall()
        next_order = conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) FROM customers"
        ).fetchone()[0]
        for (rowid,) in rows:
            next_order += 1
            conn.execute(
                "UPDATE customers SET sort_order=? WHERE rowid=?",
                (next_order, rowid),
            )

        # Seed samples only when the table is first created, not after Delete All.
        if not existing_table:
            try:
                from data import customers
            except ImportError:
                customers = []
            for index, customer in enumerate(customers, start=1):
                values = list(customer)
                if len(values) == 7:  # old format: name, address, phone, ...
                    first, _, last = str(values[0]).strip().partition(" ")
                    values = [first, last, *values[1:]]
                elif len(values) == 9:  # format with a leading numeric ID
                    values = values[1:]
                if len(values) != 8:
                    raise ValueError(
                        f"Sample customer {index} must have 8 values "
                        "(firstname, lastname, address, phone, email, city, state, zipcode)."
                    )
                conn.execute("""
                    INSERT INTO customers
                    (firstname, lastname, address, phone, email, city, state, zipcode, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (*values, index))

    return conn


conn = setup_database()
root = tk.Tk()
root.title("Customer Management System")
root.geometry("1250x650")
root.minsize(950, 550)
root.config(bg="lightblue")
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Custom.Treeview", background="white", foreground="black",
    fieldbackground="white", rowheight=27, font=("Arial", 10)
)
style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))
style.map(
    "Custom.Treeview",
    background=[("selected", "#347083")],
    foreground=[("selected", "white")],
)

# TREEVIEW
frame = ttk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)
y_scroll = ttk.Scrollbar(frame, orient="vertical")
y_scroll.pack(side="right", fill="y")
x_scroll = ttk.Scrollbar(frame, orient="horizontal")
x_scroll.pack(side="bottom", fill="x")

columns = (
    "First Name", "Last Name", "Address", "Phone", "Email",
    "City", "State", "Zip Code",
)
widths = (125, 125, 190, 130, 210, 140, 70, 95)
my_tree = ttk.Treeview(
    frame, columns=columns, show="headings", selectmode="extended",
    style="Custom.Treeview", yscrollcommand=y_scroll.set,
    xscrollcommand=x_scroll.set,
)
my_tree.pack(side="left", fill="both", expand=True)
y_scroll.configure(command=my_tree.yview)
x_scroll.configure(command=my_tree.xview)
for column, width in zip(columns, widths):
    my_tree.heading(column, text=column, anchor="w")
    my_tree.column(column, anchor="w", width=width, minwidth=70)

my_tree.tag_configure("evenrow", background="#FFFFFF", foreground="black")
my_tree.tag_configure("oddrow", background="#E6F2FF", foreground="black")

# DATA ENTRY: two rows, four fields per row
entry_frame = ttk.LabelFrame(root, text="Customer Record", padding=10)
entry_frame.pack(fill="x", padx=10, pady=5)
entries = {}
fields = (
    ("firstname", "First Name"), ("lastname", "Last Name"),
    ("address", "Address"), ("phone", "Phone"),
    ("email", "Email"), ("city", "City"),
    ("state", "State"), ("zipcode", "Zip Code"),
)
for idx, (key, label) in enumerate(fields):
    row, group = divmod(idx, 4)
    ttk.Label(entry_frame, text=label).grid(
        row=row, column=group * 2, padx=(5, 3), pady=8, sticky="w"
    )
    entry = ttk.Entry(entry_frame, width=19)
    entry.grid(row=row, column=group * 2 + 1, padx=(0, 8), pady=8, sticky="ew")
    entries[key] = entry
for col in (1, 3, 5, 7):
    entry_frame.columnconfigure(col, weight=1)

editing_record = None


def get_entry_values():
    return tuple(entry.get().strip() for entry in entries.values())


def clear_entries():
    global editing_record
    for entry in entries.values():
        entry.delete(0, tk.END)
    editing_record = None


def refresh_row_colors():
    for i, item in enumerate(my_tree.get_children()):
        my_tree.item(item, tags=("evenrow" if i % 2 == 0 else "oddrow",))


def get_selected_record():
    selected = my_tree.selection()
    if not selected:
        return None
    focused = my_tree.focus()
    return focused if focused in selected else selected[0]


def load_customers():
    my_tree.delete(*my_tree.get_children())
    rows = conn.execute("""
        SELECT rowid, firstname, lastname, address, phone, email, city, state, zipcode
        FROM customers ORDER BY sort_order, rowid
    """).fetchall()
    for row in rows:
        my_tree.insert(
            "", "end", iid=str(row[0]),
            values=tuple("" if v is None else v for v in row[1:]),
        )
    refresh_row_colors()


def select_record():
    global editing_record
    selected = get_selected_record()
    if selected is None:
        messagebox.showwarning("No Selection", "Please select a customer first.")
        return
    values = my_tree.item(selected, "values")
    for entry, value in zip(entries.values(), values):
        entry.delete(0, tk.END)
        entry.insert(0, value)
    editing_record = selected
    entries["firstname"].focus_set()


def validate_values():
    values = get_entry_values()
    if not all(values):
        messagebox.showwarning("Missing Information", "Please fill in all fields.")
        return None
    return values


def add_record():
    values = validate_values()
    if values is None:
        return
    with conn:
        next_order = conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM customers"
        ).fetchone()[0]
        conn.execute("""
            INSERT INTO customers
            (firstname, lastname, address, phone, email, city, state, zipcode, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*values, next_order))
    load_customers()
    clear_entries()
    messagebox.showinfo("Success", "Customer added successfully.")


def save_changes():
    if editing_record is None or not my_tree.exists(editing_record):
        messagebox.showwarning(
            "No Record", "Click Update Record to select a customer first."
        )
        return
    values = validate_values()
    if values is None:
        return
    with conn:
        conn.execute("""
            UPDATE customers SET firstname=?, lastname=?, address=?, phone=?,
                email=?, city=?, state=?, zipcode=? WHERE rowid=?
        """, (*values, int(editing_record)))
    my_tree.item(editing_record, values=values)
    clear_entries()
    messagebox.showinfo("Success", "Customer updated successfully.")


def remove_one():
    selected = get_selected_record()
    if selected is None:
        messagebox.showwarning("No Selection", "Please select a customer.")
        return
    if not messagebox.askyesno("Confirm Delete", "Delete the selected customer?"):
        return
    with conn:
        conn.execute("DELETE FROM customers WHERE rowid=?", (int(selected),))
    my_tree.delete(selected)
    refresh_row_colors()
    clear_entries()


def remove_many():
    selected = my_tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select one or more customers.")
        return
    if not messagebox.askyesno(
        "Confirm Delete", f"Delete {len(selected)} selected customers?"
    ):
        return
    with conn:
        conn.executemany(
            "DELETE FROM customers WHERE rowid=?",
            [(int(item),) for item in selected],
        )
    for item in selected:
        my_tree.delete(item)
    refresh_row_colors()
    clear_entries()


def remove_all():
    if not messagebox.askyesno(
        "Confirm Delete", "Are you sure you want to delete ALL customers?"
    ):
        return
    with conn:
        conn.execute("DELETE FROM customers")
    my_tree.delete(*my_tree.get_children())
    clear_entries()


def save_row_order():
    updates = [(i, int(item)) for i, item in enumerate(my_tree.get_children(), 1)]
    with conn:
        conn.executemany(
            "UPDATE customers SET sort_order=? WHERE rowid=?", updates
        )
    refresh_row_colors()


def move_up():
    selected = get_selected_record()
    if selected is not None:
        index = my_tree.index(selected)
        if index > 0:
            my_tree.move(selected, "", index - 1)
            save_row_order()


def move_down():
    selected = get_selected_record()
    if selected is not None:
        index = my_tree.index(selected)
        if index < len(my_tree.get_children()) - 1:
            my_tree.move(selected, "", index + 1)
            save_row_order()


# OPTIONS MENU
menu = tk.Menu(root)
root.configure(menu=menu)
option_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="Options", menu=option_menu)


def pick_row_color(tag, title):
    color = colorchooser.askcolor(title=title)[1]
    if color:
        my_tree.tag_configure(tag, background=color)


def highlight_color():
    color = colorchooser.askcolor(title="Choose Highlight Color")[1]
    if color:
        style.map(
            "Custom.Treeview", background=[("selected", color)],
            foreground=[("selected", "white")],
        )


def reset_colors():
    my_tree.tag_configure("evenrow", background="#FFFFFF")
    my_tree.tag_configure("oddrow", background="#E6F2FF")
    style.map(
        "Custom.Treeview", background=[("selected", "#347083")],
        foreground=[("selected", "white")],
    )

def show_search_results(matches):
    """Display all matching customers in a scrollable Toplevel form."""
    results_window = tk.Toplevel(root)
    results_window.title("Customer Search Results")
    results_window.geometry("680x550")
    results_window.minsize(520, 360)

    ttk.Label(
        results_window,
        text=f"Found {len(matches)} Customer(s)",
        font=("Arial", 18, "bold"),
    ).pack(pady=(15, 8))

    container = ttk.Frame(results_window)
    container.pack(fill="both", expand=True, padx=15, pady=5)

    canvas = tk.Canvas(container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    results_frame = ttk.Frame(canvas)
    frame_id = canvas.create_window((0, 0), window=results_frame, anchor="nw")

    results_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(frame_id, width=event.width),
    )
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for index, customer in enumerate(matches, start=1):
        customer_frame = ttk.LabelFrame(
            results_frame, text=f"Customer {index}", padding=12
        )
        customer_frame.pack(fill="x", padx=8, pady=8)
        customer_frame.columnconfigure(1, weight=1)

        for row, ((key, label), value) in enumerate(zip(fields, customer)):
            ttk.Label(customer_frame, text=f"{label}:", width=14).grid(
                row=row, column=0, padx=5, pady=4, sticky="w"
            )
            entry = ttk.Entry(customer_frame)
            entry.grid(row=row, column=1, padx=5, pady=4, sticky="ew")
            entry.insert(0, "" if value is None else str(value))
            entry.configure(state="readonly")

    ttk.Button(
        results_window, text="Close", command=results_window.destroy
    ).pack(pady=12)


def perform_search(last_name, search_window):
    """Search by last name, highlight matches, and display matching records."""
    last_name = last_name.strip().casefold()
    if not last_name:
        messagebox.showwarning(
            "Missing Last Name", "Please enter a last name.", parent=search_window
        )
        return

    matching_items = [
        item for item in my_tree.get_children()
        if last_name in str(my_tree.item(item, "values")[1]).casefold()
    ]
    if not matching_items:
        messagebox.showinfo(
            "No Results", "No customers match that last name.", parent=search_window
        )
        return

    my_tree.selection_set(matching_items)
    my_tree.focus(matching_items[0])
    my_tree.see(matching_items[0])
    matches = [my_tree.item(item, "values") for item in matching_items]
    search_window.destroy()
    show_search_results(matches)


def lookup_records():
    search_window = tk.Toplevel(root)
    search_window.title("Search Records")
    search_window.geometry("400x200")
    search_window.resizable(False, False)
    search_frame = ttk.LabelFrame(search_window, text="Last Name", padding=10)
    search_frame.pack(pady=15, padx=20, fill="both", expand=True)
    ttk.Label(search_frame, text="Enter Last Name:").pack(pady=5)
    search_entry = ttk.Entry(search_frame, width=30, font=("Arial", 14))
    search_entry.pack(pady=5)

    def run_search(event=None):
        perform_search(search_entry.get(), search_window)

    ttk.Button(
        search_frame, text="Search Records", command=run_search
    ).pack(pady=10)
    search_entry.bind("<Return>", run_search)
    search_entry.focus_set()


option_menu.add_command(
    label="Primary Color",
    command=lambda: pick_row_color("evenrow", "Choose Primary Row Color"),
)
option_menu.add_command(
    label="Secondary Color",
    command=lambda: pick_row_color("oddrow", "Choose Secondary Row Color"),
)
option_menu.add_command(label="Highlight Color", command=highlight_color)
option_menu.add_separator()
option_menu.add_command(label="Reset Colors", command=reset_colors)
option_menu.add_separator()

"""Search Menu"""
search_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="Search", menu=search_menu)
search_menu.add_command(label="Search", command=lookup_records)
# BUTTONS
button_frame = ttk.LabelFrame(root, text="Commands", padding=10)
button_frame.pack(fill="x", padx=10, pady=10)
buttons = (
    ("Update Record", select_record),
    ("Save Changes", save_changes),
    ("Add Record", add_record),
    ("Remove One", remove_one),
    ("Remove Many", remove_many),
    ("Remove All", remove_all),
    ("Move Up", move_up),
    ("Move Down", move_down),
    ("Clear Fields", clear_entries),
)
for index, (caption, command) in enumerate(buttons):
    ttk.Button(button_frame, text=caption, command=command).grid(
        row=0, column=index, padx=4, pady=5, sticky="ew"
    )
    button_frame.columnconfigure(index, weight=1)

my_tree.bind("<Double-1>", lambda event: select_record())


def close_application():
    conn.close()
    root.destroy()


option_menu.add_command(label="Exit", command=close_application)
root.protocol("WM_DELETE_WINDOW", close_application)
load_customers()
root.mainloop()
