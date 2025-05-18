import mysql.connector
import csv
import uuid

# Prototype: Connect to MySQL server (without DB)
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )

# Prototype: Create the ALX_prodev database if it doesn't exist
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

# Prototype: Connect specifically to the ALX_prodev database
def connect_to_prodev():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )

# Prototype: Create the user_data table
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3, 0) NOT NULL,
            INDEX(email)
        )
    """)
    cursor.close()

# Prototype: Insert data into the user_data table
def insert_data(connection, data):
    cursor = connection.cursor()
    for row in data:
        name, email, age = row
        # Check if email already exists
        cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"Skipping duplicate email: {email}")
            continue
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
        """, (user_id, name, email, age))
    connection.commit()
    cursor.close()

# Load data from CSV
def load_csv_data(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        return [row for row in reader]

# Main logic
if __name__ == "__main__":
    try:
        # Step 1: Connect to server and create DB
        server_conn = connect_db()
        create_database(server_conn)
        server_conn.close()

        # Step 2: Connect to ALX_prodev and setup table
        db_conn = connect_to_prodev()
        create_table(db_conn)

        # Step 3: Load data and insert
        data = load_csv_data("user_data.csv")
        insert_data(db_conn, data)

        print("Database seeded successfully.")

    except mysql.connector.Error as err:
        print("MySQL Error:", err)

    finally:
        if 'db_conn' in locals() and db_conn.is_connected():
            db_conn.close()
