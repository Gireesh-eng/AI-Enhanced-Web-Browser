import sqlite3

class DatabaseManager:
    def __init__(self, db_path="browser_history.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize the database and create tables if they don't exist."""
        self.connect()
        
        # Create history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create bookmarks table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create coupons table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            description TEXT,
            cost INTEGER,
            redeemed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.connection.commit()
        self.disconnect()

    def get_coupons(self):
        """Get all coupons from the database."""
        self.connect()
        self.cursor.execute(
            "SELECT code, description, cost, redeemed, created_at FROM coupons ORDER BY created_at DESC"
        )
        coupons = self.cursor.fetchall()
        self.disconnect()
        return coupons
    
    def connect(self):
        """Connect to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def add_history_entry(self, url, title=None):
        """Add a new entry to the browsing history."""
        self.connect()
        self.cursor.execute(
            "INSERT INTO history (url, title) VALUES (?, ?)",
            (url, title)
        )
        self.connection.commit()
        self.disconnect()
    
    def get_history(self, limit=100):
        """Retrieve browsing history entries."""
        self.connect()
        self.cursor.execute(
            "SELECT id, url, title, visit_time FROM history ORDER BY visit_time DESC LIMIT ?",
            (limit,)
        )
        history = self.cursor.fetchall()
        self.disconnect()
        return history
    
    def add_bookmark(self, url, title=None):
        """Add a new bookmark."""
        self.connect()
        self.cursor.execute(
            "INSERT INTO bookmarks (url, title) VALUES (?, ?)",
            (url, title)
        )
        self.connection.commit()
        self.disconnect()
    
    def get_bookmarks(self):
        """Retrieve all bookmarks."""
        self.connect()
        self.cursor.execute(
            "SELECT id, title, url FROM bookmarks ORDER BY title"
        )
        bookmarks = self.cursor.fetchall()
        self.disconnect()
        return bookmarks
    
    def update_bookmark(self, old_url, new_title, new_url):
        """Update an existing bookmark."""
        self.connect()
        self.cursor.execute(
            "UPDATE bookmarks SET title = ?, url = ? WHERE url = ?",
            (new_title, new_url, old_url)
        )
        self.connection.commit()
        self.disconnect()
    
    def delete_bookmark(self, url):
        """Delete a bookmark by URL."""
        self.connect()
        self.cursor.execute(
            "DELETE FROM bookmarks WHERE url = ?",
            (url,)
        )
        self.connection.commit()
        self.disconnect()

    def add_coupon(self, code, description, cost):
        """Add a new coupon to the database."""
        self.connect()
        self.cursor.execute(
            "INSERT INTO coupons (code, description, cost) VALUES (?, ?, ?)",
            (code, description, cost)
        )
        self.connection.commit()
        self.disconnect()

    def get_coupons(self):
        """Get all coupons from the database."""
        self.connect()
        self.cursor.execute(
            "SELECT code, description, cost, redeemed, created_at FROM coupons ORDER BY created_at DESC"
        )
        coupons = self.cursor.fetchall()
        self.disconnect()
        return coupons

    def mark_coupon_redeemed(self, code):
        """Mark a coupon as redeemed."""
        self.connect()
        self.cursor.execute(
            "UPDATE coupons SET redeemed = 1 WHERE code = ?",
            (code,)
        )
        self.connection.commit()
        self.disconnect()

    def is_coupon_redeemed(self, code):
        """Check if a coupon has been redeemed."""
        self.connect()
        self.cursor.execute(
            "SELECT redeemed FROM coupons WHERE code = ?",
            (code,)
        )
        result = self.cursor.fetchone()
        self.disconnect()
        return bool(result and result[0])

    def delete_history_entry(self, url):
        """Delete a specific history entry by URL."""
        self.connect()
        self.cursor.execute("DELETE FROM history WHERE url = ?", (url,))
        self.connection.commit()
        self.disconnect()

    def clear_history(self):
        """Clear all browsing history."""
        self.connect()
        self.cursor.execute("DELETE FROM history")
        self.connection.commit()
        self.disconnect()