import sqlite3

class ExecuteQuery:
    def __init__(self, db_file, query, params=None):
        self.db_file = db_file
        self.query = query
        self.params = params if params else ()
        self.connection = None
        self.cursor = None
        self.result = None
        
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        print("Database connection opened.")
        self.cursor.execute(self.query, self.params)
        self.result = self.cursor.fetchall()
        return self.result
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.cursor:
            self.cursor.close()
            print("Cursor closed.")
        if self.connection:
            self.connection.commit()
            self.connection.close()
            print("Database connection closed.")
        if exc_type is not None:
            print(f"An error occurred: {exc_value}")
        return False
    
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery("users.db", query, params) as results:
    print("RESULTS", results)