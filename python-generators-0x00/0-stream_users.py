import mysql.connector


def stream_users():
    connection = mysql.connector.connect(
        host="localhost", user="root", password="", database="ALX_prodev"
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user_data")
    for row in cursor:
        yield row

    cursor.close()
    connection.close()


# Main function to demonstrate the generator
if __name__ == "__main__":
    for i, user in enumerate(stream_users()):
        if i >= 6:
            break
        print(user)
