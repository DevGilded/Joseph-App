import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("users.db")
cursor = connection.cursor()

# Create table
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
"""
cursor.execute(create_table_query)

# Commit changes and close connection
connection.commit()
connection.close()

print("Table created successfully!")