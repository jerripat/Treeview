import data
import sqlite3

conn = sqlite3.connect("customer.db")
c = conn.cursor()

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
else:
    print("Database already contains customers.")


for record in data.customers:
    c.executemany("""
        INSERT INTO customers
        (name, address, phone, email, city, state, zip)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [record])

    conn.commit()

import sqlite3

def show_customers():
    conn = sqlite3.connect("customer.db")
    c = conn.cursor()

    c.execute("SELECT * FROM customers")
    records = c.fetchall()

    for record in records:
        print(list(record))

    conn.close()
def get_customer(custname):
    conn = sqlite3.connect("customer.db")
    c = conn.cursor()

    c.execute("SELECT * FROM customers WHERE name=?", (custname,))
    record = c.fetchone()

    if record:
        print(list(record))
    else:
        print(f"No customer found with name: {custname}")

    conn.close()

# Call the function
show_customers()
get_customer(input("Enter customer name: "))