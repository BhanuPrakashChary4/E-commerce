# Readme
## to run the application 

```python
python app.py
```

## add a user as admin

To login as an admin in the application, you can follow these steps:

1. Register a user account through the registration page (`/register`).

2. Update the database directly to set the `is_admin` flag for the registered user to `1`, indicating they are an admin. You can use the following code as an example:

```python
import sqlite3

# Connect to the database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Update the user to be an admin
cursor.execute("UPDATE users SET is_admin=1 WHERE username=?", ('your_username',))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("User is now an admin.")
```

Replace `'your_username'` with the username of the registered user that you want to promote to admin.

3. After updating the database, you can log in using the promoted user's credentials on the login page (`/login`).

Once logged in with the admin account, you will have access to the admin panel (`/admin`) and can perform admin-specific actions.
