from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QWidget)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush

class CouponHistoryDialog(QDialog):
    def __init__(self, parent=None, coin_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Coupon History")
        self.setGeometry(300, 300, 750, 550)
        
        # Enhanced styling
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
            QLabel#titleLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                margin-bottom: 0;
            }
            QLabel#subtitleLabel {
                color: #7f8c8d;
                font-size: 15px;
                padding-bottom: 20px;
                font-weight: 400;
            }
            QLabel#emptyLabel {
                color: #95a5a6;
                font-size: 16px;
                font-style: italic;
                padding: 40px;
                line-height: 1.5;
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
            QPushButton#clearButton {
                background-color: #e74c3c;
            }
            QPushButton#clearButton:hover {
                background-color: #c0392b;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.2);
            }
            QTableWidget {
                border: 2px solid #e9ecef;
                border-radius: 20px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #f1f3f5;
                selection-background-color: #e7f0ff;
                selection-color: #2c3e50;
                margin: 10px 0;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f5;
                transition: all 0.2s ease;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #4a86e8;
                color: white;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QFrame#headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a86e8, stop:1 #3a76d8);
                border-radius: 25px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 5px 20px rgba(74, 134, 232, 0.15);
            }
        """)
        
        # Store reference to coin manager
        self.coin_manager = coin_manager
        
        # Initialize empty coupon history
        self.coupon_history = []
        
        # Create basic layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Create header frame
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        # Add title
        self.title_label = QLabel("Coupon Generation History")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # Add subtitle
        self.subtitle_label = QLabel("Track all coupons generated from your coins")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.subtitle_label)
        
        self.layout.addWidget(header_frame)
        
        # Create table with enhanced styling
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Coupon Code", "Description", "Generated Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        self.table.setShowGrid(False)  # Hide grid lines for cleaner look
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)
        
        # Empty state label with icon
        empty_container = QWidget()
        empty_layout = QVBoxLayout(empty_container)
        
        self.empty_label = QLabel("No coupons have been generated yet.\nConvert coins to coupons to see them here.")
        self.empty_label.setObjectName("emptyLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_label)
        
        self.layout.addWidget(empty_container)
        
        # Button layout with enhanced styling
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # Clear button with icon
        self.clear_button = QPushButton(" Clear History")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear", QIcon()))
        self.clear_button.clicked.connect(self.clear_history)
        
        # Close button with icon
        self.close_button = QPushButton(" Close")
        self.close_button.setIcon(QIcon.fromTheme("window-close", QIcon()))
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(button_layout)
        
        # Update display
        self.update_display()
    
    def update_display(self):
        """Update the table display based on current history."""
        try:
            print(f"Updating display with {len(self.coupon_history)} coupons")
            # Update empty label visibility
            has_items = len(self.coupon_history) > 0
            self.empty_label.parentWidget().setVisible(not has_items)
            self.table.setVisible(has_items)
            self.clear_button.setEnabled(has_items)
            
            if has_items:
                # Clear existing rows
                self.table.setRowCount(0)
                
                # Add rows in reverse order (newest first)
                for coupon in self.coupon_history:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    # Code - with bold font and blue color
                    code_item = QTableWidgetItem(coupon.get("code", ""))
                    code_item.setFont(QFont("Arial", 10, QFont.Bold))
                    code_item.setForeground(QBrush(QColor("#3498db")))
                    
                    # Description - with regular font
                    desc_item = QTableWidgetItem(coupon.get("description", ""))
                    desc_item.setFont(QFont("Arial", 10))
                    
                    # Time - with gray color and smaller font
                    time_item = QTableWidgetItem(coupon.get("generated_time", ""))
                    time_item.setForeground(QBrush(QColor("#7f8c8d")))
                    time_item.setFont(QFont("Arial", 9))
                    
                    self.table.setItem(row, 0, code_item)
                    self.table.setItem(row, 1, desc_item)
                    self.table.setItem(row, 2, time_item)
                    self.table.setRowHeight(row, 40)
                
                # Force the table to update
                self.table.update()
                self.table.repaint()
                print(f"Display updated with {self.table.rowCount()} rows")
        except Exception as e:
            print(f"Error updating coupon history display: {str(e)}")
    
    def add_coupon_to_history(self, coupon):
        """Add a coupon to the history."""
        try:
            print(f"Adding coupon to history: {coupon}")
            
            if not isinstance(coupon, dict):
                print("Error: Coupon is not a dictionary")
                return
                
            # Ensure coupon has required fields
            if "code" not in coupon or "description" not in coupon:
                print("Error: Coupon missing required fields")
                return
                
            # Add timestamp if not present
            if "generated_time" not in coupon:
                coupon["generated_time"] = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            
            # Check if coupon already exists (avoid duplicates)
            for existing in self.coupon_history:
                if existing.get("code") == coupon.get("code"):
                    print(f"Coupon already exists in history: {coupon['code']}")
                    return
            
            # Add to history at the beginning (newest first)
            self.coupon_history.insert(0, coupon.copy())
            
            # Update the entire display
            self.update_display()
            
            # Ensure the newest coupon is visible
            self.table.scrollToTop()
            
            print(f"Coupon added to history. Total coupons: {len(self.coupon_history)}")
        except Exception as e:
            print(f"Error adding coupon to history: {str(e)}")
    
    def clear_history(self):
        """Clear the coupon history."""
        # Clear from database if coin manager is available
        if self.coin_manager:
            try:
                self.coin_manager.clear_coupon_history()
                print("Coupon history cleared from database")
            except Exception as e:
                print(f"Error clearing coupon history from database: {str(e)}")
        
        # Clear from memory
        self.coupon_history = []
        self.update_display()