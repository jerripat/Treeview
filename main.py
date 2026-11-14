from tkinter import *
from tkinter import ttk, messagebox
from pathlib import Path
import sqlite3

# ==================================================
# MAIN WINDOW
# ==================================================

root = Tk()
root.title("Customer Management System")
root.geometry("1200x650")
root.minsize(1050, 550)

# ==================================================
# DATABASE
# ==================================================

DB_FILE = Path(__file__).resolve().parent / "customer.db"
new_database = not DB_FILE.exists()

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("""
          CREATE TABLE IF NOT EXISTS customers
          (
              name
              TEXT
              NOT
              NULL,
              address
              TEXT,
              phone
              TEXT,
              email
              TEXT,
              city
              TEXT,
              state
              TEXT,
              zip
              TEXT,
              sort_order
              INTEGER
          )
""")

# Add sort_order to an older database if necessary.
c.execute("PRAGMA table_info(customers)")
existing_columns = [row[1] for row in c.fetchall()]

if "sort_order" not in existing_columns:
    c.execute(
        "ALTER TABLE customers ADD COLUMN sort_order INTEGER"
    )

# Assign an order to existing records.
c.execute("""
          SELECT rowid
          FROM customers
          WHERE sort_order IS NULL
          ORDER BY rowid
""")

missing_order = c.fetchall()

c.execute(
    "SELECT COALESCE(MAX(sort_order), 0) FROM customers"
)
next_order = c.fetchone()[0]

for (customer_id,) in missing_order:
    next_order += 1
    c.execute(
        "UPDATE customers SET sort_order = ? WHERE rowid = ?",
        (next_order, customer_id)
    )

conn.commit()

# ==================================================
# SAMPLE CUSTOMER DATA
# ==================================================


# Only insert sample data for a newly created database.
if new_database:
    for index, customer in enumerate(customers):
        c.execute("""
                  INSERT INTO customers
                  (name, address, phone, email,
                   city, state, zip, sort_order)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (*customer, index + 1))

    conn.commit()

# ==================================================
# TREEVIEW STYLE
# ==================================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#D3D3D3",
    foreground="black",
    rowheight=27,
    fieldbackground="#D3D3D3",
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#347083")],
    foreground=[("selected", "white")]
)

# ==================================================
# TREEVIEW FRAME
# ==================================================

tree_frame = Frame(root)
tree_frame.pack(
    fill=BOTH,
    expand=True,
    padx=10,
    pady=10
)

tree_scroll = Scrollbar(tree_frame, orient=VERTICAL)
tree_scroll.pack(side=RIGHT, fill=Y)

bottom_scroll = Scrollbar(tree_frame, orient=HORIZONTAL)
bottom_scroll.pack(side=BOTTOM, fill=X)

columns = (
    "Name",
    "Address",
    "Phone Number",
    "Email",
    "City",
    "State",
    "Zip Code"
)

my_tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    selectmode="extended",
    yscrollcommand=tree_scroll.set,
    xscrollcommand=bottom_scroll.set
)

my_tree.pack(side=LEFT, fill=BOTH, expand=True)

tree_scroll.config(command=my_tree.yview)
bottom_scroll.config(command=my_tree.xview)

widths = (150, 200, 130, 220, 130, 80, 100)

for column, width in zip(columns, widths):
    my_tree.column(
        column,
        anchor=W,
        width=width,
        minwidth=70
    )

    my_tree.heading(
        column,
        text=column,
        anchor=W
    )

# ==================================================
# ALTERNATING ROW COLORS
# ==================================================

my_tree.tag_configure(
    "evenrow",
    background="#FFFFFF",
    foreground="black"
)

my_tree.tag_configure(
    "oddrow",
    background="#E6F2FF",
    foreground="black"
)

# ==================================================
# DATA ENTRY FRAME
# ==================================================

data_frame = LabelFrame(
    root,
    text="Customer Record",
    padx=10,
    pady=10
)

data_frame.pack(
    fill=X,
    padx=10,
    pady=10
)

# ---------------- ROW 1 ----------------

name_label = Label(data_frame, text="Name")
name_label.grid(row=0, column=0, padx=5, pady=10, sticky=W)

name_entry = Entry(data_frame, width=20)
name_entry.grid(row=0, column=1, padx=5, pady=10)

address_label = Label(data_frame, text="Address")
address_label.grid(row=0, column=2, padx=5, pady=10, sticky=W)

address_entry = Entry(data_frame, width=25)
address_entry.grid(row=0, column=3, padx=5, pady=10)

phone_label = Label(data_frame, text="Phone")
phone_label.grid(row=0, column=4, padx=5, pady=10, sticky=W)

phone_entry = Entry(data_frame, width=18)
phone_entry.grid(row=0, column=5, padx=5, pady=10)

email_label = Label(data_frame, text="Email")
email_label.grid(row=0, column=6, padx=5, pady=10, sticky=W)

email_entry = Entry(data_frame, width=25)
email_entry.grid(row=0, column=7, padx=5, pady=10)

# ---------------- ROW 2 ----------------

city_label = Label(data_frame, text="City")
city_label.grid(row=1, column=0, padx=5, pady=10, sticky=W)

city_entry = Entry(data_frame, width=20)
city_entry.grid(row=1, column=1, padx=5, pady=10)

state_label = Label(data_frame, text="State")
state_label.grid(row=1, column=2, padx=5, pady=10, sticky=W)

state_entry = Entry(data_frame, width=10)
state_entry.grid(row=1, column=3, padx=5, pady=10, sticky=W)

zip_label = Label(data_frame, text="Zip Code")
zip_label.grid(row=1, column=4, padx=5, pady=10, sticky=W)

zip_entry = Entry(data_frame, width=15)
zip_entry.grid(row=1, column=5, padx=5, pady=10, sticky=W)

# ==================================================
# ENTRY HELPERS
# ==================================================

entries = (
    name_entry,
    address_entry,
    phone_entry,
    email_entry,
    city_entry,
    state_entry,
    zip_entry
)

editing_record = None


def clear_entries():
    global editing_record

    for entry in entries:
        entry.delete(0, END)

    editing_record = None


def get_entry_values():
    return tuple(
        entry.get().strip()
        for entry in entries
    )


def refresh_row_colors():
    for index, item in enumerate(my_tree.get_children()):
        tag = "evenrow" if index % 2 == 0 else "oddrow"

        my_tree.item(
            item,
            tags=(tag,)
        )


def get_selected_record():
    selected = my_tree.selection()

    if not selected:
        return None

    # Use the focused selected row, when possible.
    focused = my_tree.focus()

    if focused in selected:
        return focused

    return selected[0]


# ==================================================
# LOAD CUSTOMER RECORDS FROM DATABASE
# ==================================================

def load_customers():
    for item in my_tree.get_children():
        my_tree.delete(item)

    c.execute("""
              SELECT rowid,
                     name,
                     address,
                     phone,
                     email,
                     city,
                     state,
                     zip
              FROM customers
              ORDER BY sort_order, rowid
    """)

    records = c.fetchall()

    for record in records:
        customer_id = record[0]
        customer_data = record[1:]

        my_tree.insert(
            "",
            END,
            iid=str(customer_id),
            values=customer_data
        )

    refresh_row_colors()


# ==================================================
# SELECT RECORD FOR EDITING
# ==================================================

def select_record():
    global editing_record

    selected = get_selected_record()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a customer first."
        )
        return

    values = my_tree.item(selected, "values")

    for entry, value in zip(entries, values):
        entry.delete(0, END)
        entry.insert(0, value)

    editing_record = selected

    name_entry.focus_set()


# ==================================================
# ADD RECORD
# ==================================================

def add_record():
    values = get_entry_values()

    if not all(values):
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    c.execute("""
              SELECT COALESCE(MAX(sort_order), 0) + 1
              FROM customers
    """)

    sort_order = c.fetchone()[0]

    c.execute("""
              INSERT INTO customers
              (name, address, phone, email,
               city, state, zip, sort_order)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (*values, sort_order))

    customer_id = c.lastrowid
    conn.commit()

    my_tree.insert(
        "",
        END,
        iid=str(customer_id),
        values=values
    )

    refresh_row_colors()
    clear_entries()

    messagebox.showinfo(
        "Success",
        "Customer added successfully."
    )


# ==================================================
# SAVE CHANGES
# ==================================================

def save_changes():
    global editing_record

    if not editing_record or not my_tree.exists(editing_record):
        messagebox.showwarning(
            "No Record",
            "Click Update Record to select a customer first."
        )
        return

    values = get_entry_values()

    if not all(values):
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    customer_id = int(editing_record)

    c.execute("""
              UPDATE customers
              SET name    = ?,
                  address = ?,
                  phone   = ?,
                  email   = ?,
                  city    = ?,
                  state   = ?,
                  zip     = ?
              WHERE rowid = ?
    """, (*values, customer_id))

    conn.commit()

    my_tree.item(
        editing_record,
        values=values
    )

    clear_entries()

    messagebox.showinfo(
        "Success",
        "Customer updated successfully."
    )


# ==================================================
# REMOVE ONE RECORD
# ==================================================

def remove_one():
    selected = get_selected_record()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a customer."
        )
        return

    if not messagebox.askyesno(
            "Confirm Delete",
            "Delete the selected customer?"
    ):
        return

    c.execute(
        "DELETE FROM customers WHERE rowid = ?",
        (int(selected),)
    )

    conn.commit()

    my_tree.delete(selected)
    refresh_row_colors()
    clear_entries()


# ==================================================
# REMOVE MANY RECORDS
# ==================================================

def remove_many():
    selected = my_tree.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select one or more customers."
        )
        return

    if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete {len(selected)} selected customers?"
    ):
        return

    customer_ids = [
        (int(item),)
        for item in selected
    ]

    c.executemany(
        "DELETE FROM customers WHERE rowid = ?",
        customer_ids
    )

    conn.commit()

    for item in selected:
        my_tree.delete(item)

    refresh_row_colors()
    clear_entries()


# ==================================================
# REMOVE ALL RECORDS
# ==================================================

def remove_all():
    if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete ALL customers?"
    ):
        return

    c.execute("DELETE FROM customers")
    conn.commit()

    for item in my_tree.get_children():
        my_tree.delete(item)

    clear_entries()


# ==================================================
# SAVE TREEVIEW ROW ORDER
# ==================================================

def save_row_order():
    items = my_tree.get_children()

    updates = [
        (index, int(item))
        for index, item in enumerate(items, start=1)
    ]

    c.executemany(
        """
        UPDATE customers
        SET sort_order = ?
        WHERE rowid = ?
        """,
        updates
    )

    conn.commit()
    refresh_row_colors()


# ==================================================
# MOVE RECORD UP
# ==================================================

def move_up():
    selected = get_selected_record()

    if not selected:
        return

    index = my_tree.index(selected)

    if index > 0:
        my_tree.move(
            selected,
            "",
            index - 1
        )

        save_row_order()


# ==================================================
# MOVE RECORD DOWN
# ==================================================

def move_down():
    selected = get_selected_record()

    if not selected:
        return

    index = my_tree.index(selected)
    total = len(my_tree.get_children())

    if index < total - 1:
        my_tree.move(
            selected,
            "",
            index + 1
        )

        save_row_order()


# ==================================================
# COMMAND BUTTONS
# ==================================================

button_frame = LabelFrame(
    root,
    text="Commands",
    padx=10,
    pady=10
)

button_frame.pack(
    fill=X,
    padx=10,
    pady=10
)

buttons = [
    ("Update Record", select_record),
    ("Save Changes", save_changes),
    ("Add Record", add_record),
    ("Remove One", remove_one),
    ("Remove Many", remove_many),
    ("Remove All", remove_all),
    ("Move Up", move_up),
    ("Move Down", move_down),
    ("Clear Fields", clear_entries)
]

for index, (text, command) in enumerate(buttons):
    button = Button(
        button_frame,
        text=text,
        command=command,
        padx=8,
        pady=5
    )

    button.grid(
        row=0,
        column=index,
        padx=5,
        pady=5
    )

# ==================================================
# DOUBLE-CLICK TO SELECT
# ==================================================

my_tree.bind(
    "<Double-1>",
    lambda event: select_record()
)


# ==================================================
# CLOSE DATABASE SAFELY
# ==================================================

def close_application():
    conn.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_application)

# ==================================================
# START APPLICATION
# ==================================================

load_customers()
root.mainloop()
