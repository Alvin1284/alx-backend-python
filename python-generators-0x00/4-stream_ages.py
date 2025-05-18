import mysql.connector

def stream_user_ages():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")

    for (age,) in cursor:
        yield age

    cursor.close()
    connection.close()

def compute_average_age():
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("Average age of users: 0.00")

# Required by instructions
if __name__ == "__main__":
    compute_average_age()
