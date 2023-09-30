import sqlite3

# Connect to the database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Update the user to be an admin
cursor.execute("UPDATE users SET is_admin=1 WHERE username=?", ('admin',))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("User is now an admin.")
