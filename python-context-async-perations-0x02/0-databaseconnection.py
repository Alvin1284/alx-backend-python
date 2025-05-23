import sqlite3

class DatabaseConnection:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
        
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_file)
        print("Database connection opened.")
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        if exc_type is not None:
            print(f"An error occurred: {exc_value}")
        return False
    
with DatabaseConnection("users.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print("RESULTS", results)