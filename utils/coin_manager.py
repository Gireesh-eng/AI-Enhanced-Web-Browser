import random
import sqlite3
import os
from datetime import datetime
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

class CoinManager(QObject):
    """Manages the coin system with a timer that adds coins periodically."""
    
    # Signal emitted when coin count changes
    coin_count_changed = pyqtSignal(int)
    
    # Signal emitted when a new coupon is generated
    coupon_generated = pyqtSignal(dict)
    
    # Dictionary of coupon rewards with their costs
    COUPON_REWARDS = {
        "SWIGGY50": {"cost": 10, "description": "Flat 20% off on your first order on Swiggy"},
        "ZOMATOFREEDEL": {"cost": 15, "description": "Free delivery on Zomato orders above 150"},
        "OLA50": {"cost": 100, "description": "Get 50% off on your first Ola ride"},
        "UBER20": {"cost": 200, "description": "20% off on your next 3 Uber rides"},
        "KFCMEAL": {"cost": 300, "description": "Buy 1 Get 1 Free on KFC Zinger Meal"},
        "BLINKIT10": {"cost": 100, "description": "10% off on groceries from Blinkit"},
        "ZEPTOSAVE": {"cost": 100, "description": "Save 50 on your first Zepto order"},
        "LENSKARTBOGO": {"cost": 150, "description": "Buy one get one free on Lenskart eyewear"},
        "INSTAMART5": {"cost": 150, "description": "Extra 5% off on Instamart orders"},
        "BIRTHDAYUBER": {"cost": 200, "description": "Special birthday discount on Uber rides"}
    }
    
    def __init__(self):
        super().__init__()
        self.coins = 0
        self.last_coin_time = None
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'coins.db')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load coins from database
        self._load_coins()
        
        # Create timer for adding coins (50 seconds interval)
        self.timer = QTimer()
        self.timer.setInterval(50000)  # 50 seconds
        self.timer.timeout.connect(self.add_coin)
    
    def _init_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coins (
                id INTEGER PRIMARY KEY,
                amount INTEGER NOT NULL,
                last_update TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                cost INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_coins(self):
        """Load coins from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT amount, last_update FROM coins WHERE id = 1')
            result = cursor.fetchone()
            
            if result:
                self.coins = result[0]
                self.last_coin_time = datetime.fromisoformat(result[1])
            else:
                # Initialize with 0 coins if no record exists
                self.coins = 0
                self.last_coin_time = datetime.now()
                cursor.execute(
                    'INSERT INTO coins (id, amount, last_update) VALUES (?, ?, ?)',
                    (1, 0, self.last_coin_time.isoformat())
                )
                conn.commit()
            
            # Always emit the current coin count
            self.coin_count_changed.emit(self.coins)
            
            conn.close()
        except Exception as e:
            print(f"Error loading coins: {str(e)}")
            self.coins = 0
            self.coin_count_changed.emit(0)
    
    def _save_coins(self):
        """Save coins to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE coins SET amount = ?, last_update = ? WHERE id = 1',
            (self.coins, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def add_coins(self, amount):
        """Add coins and save to database."""
        self.coins += amount
        self.last_coin_time = datetime.now()
        self._save_coins()
        # Emit signal when coins are added
        self.coin_count_changed.emit(self.coins)
    
    def get_coins(self):
        """Get current coin balance."""
        return self.coins
    
    def use_coins(self, amount):
        """Use coins if available and save to database."""
        if self.coins >= amount:
            self.coins -= amount
            self._save_coins()
            # Emit signal when coins are used
            self.coin_count_changed.emit(self.coins)
            return True
        return False
    
    def get_coupon_history(self):
        """Get history of created coupons."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT type, cost, created_at FROM coupons ORDER BY created_at DESC')
        coupons = cursor.fetchall()
        
        conn.close()
        
        return [(type, cost, datetime.fromisoformat(created_at)) for type, cost, created_at in coupons]
    
    def clear_coupon_history(self):
        """Clear all coupon history from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM coupons')
        
        conn.commit()
        conn.close()
        
        return True
    
    def should_award_coin(self, current_time):
        """Check if enough time has passed to award a new coin."""
        if self.last_coin_time is None:
            return True
        
        time_diff = (current_time - self.last_coin_time).total_seconds()
        return time_diff >= 10  # Award a coin every 10 seconds
    
    def start_timer(self):
        """Start the timer to add coins periodically."""
        if not self.timer.isActive():
            self.timer.start()
            # Add initial coin if needed
            if self.last_coin_time is None or self.should_award_coin(datetime.now()):
                self.add_coin()
    
    def stop_timer(self):
        """Stop the timer."""
        if self.timer.isActive():
            self.timer.stop()
            self._save_coins()  # Save coins when stopping
    
    def add_coin(self, count=1):
        """Add coins to the total count and save to database."""
        self.coins += count
        self.last_coin_time = datetime.now()
        self._save_coins()
        self.coin_count_changed.emit(self.coins)
        print(f"Coin added. Total coins: {self.coins}")
    
    def get_coupon_rewards(self):
        """Get the available coupon rewards."""
        return self.COUPON_REWARDS
    
    def convert_to_coupon(self, coupon_type):
        """Convert coins to a coupon and save to database."""
        try:
            if coupon_type not in self.COUPON_REWARDS:
                return False, "Invalid coupon type"
            
            coupon_info = self.COUPON_REWARDS[coupon_type]
            cost = coupon_info["cost"]
            current_time = datetime.now()
            
            # Save coupon to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO coupons (type, cost, created_at) VALUES (?, ?, ?)',
                (coupon_type, cost, current_time.isoformat())
            )
            
            conn.commit()
            conn.close()
            
            # Generate unique coupon code
            unique_code = f"{coupon_type}{current_time.strftime('%m%d%H%M%S')}"
            coupon_data = {
                "code": unique_code,
                "description": coupon_info["description"],
                "cost": cost,
                "generated_time": current_time.isoformat()
            }
            
            # Emit the signal with coupon data
            self.coupon_generated.emit(coupon_data)
            print(f"Emitting coupon: {coupon_data}")
            return True, f"Successfully created coupon: {unique_code}"
        except Exception as e:
            print(f"Error in convert_to_coupon: {str(e)}")
            return False, str(e)