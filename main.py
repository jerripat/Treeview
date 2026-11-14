
from tkinter import *
from tkinter import ttk, messagebox

# ---------------- MAIN WINDOW ----------------

root = Tk()
root.title("Customer Management System")
root.geometry("1200x600")

# ---------------- TREEVIEW STYLE ----------------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#D3D3D3",
    foreground="black",
    rowheight=25,
    fieldbackground="#D3D3D3"
)

style.map(
    "Treeview",
    background=[("selected", "#347083")],
    foreground=[("selected", "white")]
)

# ---------------- TREEVIEW FRAME ----------------

tree_frame = Frame(root)
tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

my_tree = ttk.Treeview(
    tree_frame,
    yscrollcommand=tree_scroll.set,
    selectmode="extended",
    show="headings"
)
my_tree.pack(side=LEFT, fill=BOTH, expand=True)

tree_scroll.config(command=my_tree.yview)

columns = (
    "Name", "Address", "Phone Number", "Email",
    "City", "State", "Zip Code"
)

my_tree["columns"] = columns

widths = (150, 200, 130, 220, 130, 80, 100)

for column, width in zip(columns, widths):
    my_tree.column(column, anchor=W, width=width)
    my_tree.heading(column, text=column, anchor=W)

# ---------------- ALTERNATING ROW COLORS ----------------

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

# ---------------- SAMPLE DATA ----------------

customers = [
    ("John Smith", "123 Main St", "479-555-1234",
     "john@example.com", "Fort Smith", "AR", "72901"),

    ("Mary Jones", "456 Oak St", "479-555-5678",
     "mary@example.com", "Van Buren", "AR", "72956"),

    ("Bob Wilson", "789 Pine St", "479-555-9012",
     "bob@example.com", "Alma", "AR", "72921"),

    ("Susan Brown", "321 Elm St", "479-555-3456",
     "susan@example.com", "Fort Smith", "AR", "72903"),

    ("Tom Johnson", "654 Maple St", "479-555-7890",
     "tom@example.com", "Fort Smith", "AR", "72904"),

    ("Lisa Davis", "987 Cedar St", "479-555-2345",
     "lisa@example.com", "Fort Smith", "AR", "72905")
]

for index, customer in enumerate(customers):
    tag = "evenrow" if index % 2 == 0 else "oddrow"

    my_tree.insert(
        "",
        END,
        values=customer,
        tags=(tag,)
    )

# ---------------- DATA ENTRY FRAME ----------------

data_frame = LabelFrame(
    root,
    text="Customer Record",
    padx=10,
    pady=10
)
data_frame.pack(fill=X, padx=10, pady=10)

# ROW 1

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

# ROW 2

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

# ---------------- ENTRY HELPERS ----------------

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
    return tuple(entry.get().strip() for entry in entries)


def refresh_row_colors():
    for index, item in enumerate(my_tree.get_children()):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        my_tree.item(item, tags=(tag,))


# ---------------- SELECT RECORD ----------------

def select_record():
    global editing_record

    selected = my_tree.focus()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a record first."
        )
        return

    values = my_tree.item(selected, "values")

    # Fill the entry fields with selected row data
    for entry, value in zip(entries, values):
        entry.delete(0, END)
        entry.insert(0, value)

    editing_record = selected


# ---------------- ADD RECORD ----------------

def add_record():
    values = get_entry_values()

    if not all(values):
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    my_tree.insert("", END, values=values)

    refresh_row_colors()
    clear_entries()


# ---------------- SAVE CHANGES ----------------

def save_changes():
    global editing_record

    if not editing_record or not my_tree.exists(editing_record):
        messagebox.showwarning(
            "No Record",
            "Select a record using Update Record first."
        )
        return

    values = get_entry_values()

    if not all(values):
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    my_tree.item(editing_record, values=values)

    clear_entries()

    messagebox.showinfo(
        "Success",
        "Record updated successfully."
    )


# ---------------- REMOVE RECORDS ----------------

def remove_one():
    selected = my_tree.focus()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a record."
        )
        return

    my_tree.delete(selected)

    refresh_row_colors()
    clear_entries()


def remove_many():
    selected = my_tree.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select one or more records."
        )
        return

    for item in selected:
        my_tree.delete(item)

    refresh_row_colors()
    clear_entries()


def remove_all():
    if messagebox.askyesno(
        "Confirm Delete",
        "Remove all customer records?"
    ):
        for item in my_tree.get_children():
            my_tree.delete(item)

        clear_entries()


# ---------------- MOVE RECORDS ----------------

def move_up():
    selected = my_tree.focus()

    if not selected:
        return

    index = my_tree.index(selected)

    if index > 0:
        my_tree.move(selected, "", index - 1)
        refresh_row_colors()


def move_down():
    selected = my_tree.focus()

    if not selected:
        return

    index = my_tree.index(selected)
    total = len(my_tree.get_children())

    if index < total - 1:
        my_tree.move(selected, "", index + 1)
        refresh_row_colors()


# ---------------- COMMAND BUTTONS ----------------

button_frame = LabelFrame(
    root,
    text="Commands",
    padx=10,
    pady=10
)
button_frame.pack(fill=X, padx=10, pady=10)

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
    button.grid(row=0, column=index, padx=5, pady=5)


# Double-click a Treeview row to load its information
my_tree.bind("<Double-1>", lambda event: select_record())

root.mainloop()
