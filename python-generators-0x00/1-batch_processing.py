import mysql.connector

# Generator: fetch rows in batches from user_data
def stream_users_in_batches(batch_size):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password= "",
        database="ALX_prodev"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    connection.close()

# Function: process each batch and filter users over age 25
def batch_processing(batch_size):
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if user['age'] > 25]
        yield filtered 
        
if __name__ == "__main__":
    for filtered_batch in batch_processing(batch_size=3):  # Loop 3
        for user in filtered_batch:
            print(user)

