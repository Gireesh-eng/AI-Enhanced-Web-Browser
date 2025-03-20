from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QLineEdit,
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class CouponDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Coupon Manager")
        self.setGeometry(300, 300, 550, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: 600;
                font-size: 13px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #3a76d8;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(74, 134, 232, 0.2);
            }
            QPushButton:pressed {
                transform: translateY(1px);
                box-shadow: 0 2px 5px rgba(74, 134, 232, 0.1);
            }
            QLineEdit {
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                font-size: 14px;
                transition: all 0.3s ease;
                background-color: white;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border-color: #4a86e8;
                background-color: white;
                box-shadow: 0 0 10px rgba(74, 134, 232, 0.15);
            }
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 20px;
                background-color: white;
                padding: 15px;
                font-size: 14px;
                margin: 10px 0;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f1f3f5;
                border-radius: 12px;
                margin: 3px 0;
                transition: all 0.3s ease;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
                transform: translateX(5px);
            }
            QListWidget::item:selected {
                background-color: #e7f0ff;
                color: #2c3e50;
                font-weight: 600;
                transform: scale(1.02);
            }
            QFrame#addFrame {
                border: 2px solid #e9ecef;
                border-radius: 25px;
                background-color: white;
                padding: 25px;
                margin: 15px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.05);
            }
        """)
        
        # Sample coupons (in a real app, these would come from a database)
        #self.coupons = [
        #    {"code": "SAVE10", "description": "10% off your purchase"},
        #    {"code": "FREESHIP", "description": "Free shipping on orders over $50"},
         #   {"code": "SUMMER2023", "description": "Summer sale - 20% off selected items"}
        #]
        
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Coupon Manager")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Add coupon frame
        add_frame = QFrame()
        add_frame.setObjectName("addFrame")
        add_layout = QGridLayout(add_frame)
        
        # Labels
        code_label = QLabel("Coupon Code:")
        desc_label = QLabel("Description:")
        
        # Inputs
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter coupon code")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Enter coupon description")
        
        # Add button
        self.add_button = QPushButton("Add Coupon")
        self.add_button.clicked.connect(self.add_coupon)
        
        # Add to grid layout
        add_layout.addWidget(code_label, 0, 0)
        add_layout.addWidget(self.code_input, 0, 1)
        add_layout.addWidget(desc_label, 1, 0)
        add_layout.addWidget(self.desc_input, 1, 1)
        add_layout.addWidget(self.add_button, 2, 1, Qt.AlignRight)
        
        layout.addWidget(add_frame)
        
        # Coupon list label
        list_label = QLabel("Available Coupons:")
        list_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(list_label)
        
        # Coupon list
        self.coupon_list = QListWidget()
        self.load_coupons()
        layout.addWidget(self.coupon_list)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Delete button
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_coupon)
        self.delete_button.setStyleSheet("""
            background-color: #e74c3c;
        """)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def load_coupons(self):
        """Load coupons into the list widget."""
        self.coupon_list.clear()
        
        for coupon in self.coupons:
            item_text = f"{coupon['code']} - {coupon['description']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, coupon['code'])
            self.coupon_list.addItem(item)
    
    def add_coupon(self):
        """Add a new coupon to the list."""
        code = self.code_input.text().strip()
        description = self.desc_input.text().strip()
        
        if code and description:
            new_coupon = {"code": code, "description": description}
            self.add_coupon_to_list(new_coupon)
            
            # Clear input fields
            self.code_input.clear()
            self.desc_input.clear()
    
    def add_coupon_to_list(self, coupon):
        """Add a coupon to the list (can be called from outside)."""
        # Check if coupon already exists
        for existing in self.coupons:
            if existing['code'] == coupon['code']:
                return False
                
        self.coupons.append(coupon)
        self.load_coupons()
        return True
    
    def delete_coupon(self):
        """Delete the selected coupon."""
        current_item = self.coupon_list.currentItem()
        
        if current_item:
            code = current_item.data(Qt.UserRole)
            self.coupons = [c for c in self.coupons if c['code'] != code]
            self.load_coupons()
