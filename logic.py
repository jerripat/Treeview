
import sqlite3
import data

DB_NAME = "customer.db"


# Create database and table if needed
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT,
            city TEXT,
            state TEXT,
            zip TEXT
        )
    """)

    c.execute("SELECT COUNT(*) FROM customers")
    count = c.fetchone()[0]

    if count == 0:
        c.executemany("""
            INSERT INTO customers
            (name, address, phone, email, city, state, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data.customers)

        conn.commit()
        print("20 customers added successfully!")

    conn.close()


# Display all customers
def show_customers():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM customers")
    records = c.fetchall()

    print("\n--- CUSTOMER LIST ---")

    for record in records:
        print(list(record))

    conn.close()


# Find a customer by name
def get_customer(custname):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM customers WHERE name = ?",
        (custname,)
    )

    record = c.fetchone()

    if record:
        print("\nCustomer Found:")
        print(list(record))
    else:
        print(f"No customer found with name: {custname}")

    conn.close()


# Add a customer
def add_customer():
    print("\n--- ADD NEW CUSTOMER ---")

    name = input("Name: ").strip()
    address = input("Address: ")
    phone = input("Phone: ")
    email = input("Email: ")
    city = input("City: ")
    state = input("State: ")
    zip_code = input("ZIP Code: ")

    if not name:
        print("Customer name is required.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO customers
        (name, address, phone, email, city, state, zip)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name, address, phone, email,
        city, state, zip_code
    ))

    conn.commit()
    conn.close()

    print("Customer added successfully!")


# Main menu
def my_menu():
    while True:
        print("\n===== CUSTOMER DATABASE MENU =====")
        print("1. Show All Customers")
        print("2. Find Customer by Name")
        print("3. Add New Customer")
        print("4. Exit")
        print("==================================")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            show_customers()

        elif choice == "2":
            name = input("Enter customer name: ")
            get_customer(name)

        elif choice == "3":
            add_customer()

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

def drop_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS customers")
    conn.commit()
    conn.close()
    print("Table dropped successfully!")
drop_table()
# Start the program
if __name__ == "__main__":
    setup_database()
    #my_menu()
#(input("Enter customer name: "))