# Insert sample products
cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", ('Product 1', 10.99))
cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", ('Product 2', 19.99))
cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", ('Product 3', 14.99))


INSERT INTO products (name, price) VALUES ("Product 1", 10.99); ('Product 1', 10.99)





# updating the reviews table 
CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            review TEXT,
            rating INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )



def create_tables():
    # ... existing code ...

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            review TEXT,
            rating INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
