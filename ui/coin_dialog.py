from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QFrame, QMessageBox, QListWidget, QListWidgetItem, QWidget)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
import random

class CoinDialog(QDialog):
    def __init__(self, parent=None, coin_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Coin Rewards")
        self.setGeometry(300, 300, 400, 300)
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
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #adb5bd;
                transform: none;
                box-shadow: none;
            }
            QProgressBar {
                border: 2px solid #4a86e8;
                border-radius: 12px;
                text-align: center;
                height: 30px;
                background-color: white;
                margin: 10px 0;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a86e8, stop:1 #3a76d8);
                border-radius: 10px;
            }
            QFrame#coinFrame {
                border: 2px solid #e9ecef;
                border-radius: 25px;
                background-color: white;
                padding: 25px;
                margin: 15px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.05);
            }
        """)
        
        self.coin_manager = coin_manager
        self.parent_window = parent
        
        self.init_ui()
        
        # Connect signals
        if self.coin_manager:
            # Disconnect any existing connections to avoid duplicates
            try:
                self.coin_manager.coin_count_changed.disconnect(self.update_coin_count)
            except:
                pass
            try:
                self.coin_manager.coupon_generated.disconnect(self.coupon_generated)
            except:
                pass
            
            # Connect signals
            self.coin_manager.coin_count_changed.connect(self.update_coin_count)
            self.coin_manager.coupon_generated.connect(self.coupon_generated)
            
            print("Signals connected in CoinDialog")
    
    def init_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Coin Rewards System")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Coin frame
        coin_frame = QFrame()
        coin_frame.setObjectName("coinFrame")
        coin_layout = QVBoxLayout(coin_frame)
        
        # Coin count
        coin_count_layout = QHBoxLayout()
        coin_label = QLabel("Current Coins:")
        coin_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.coin_count = QLabel("0")
        self.coin_count.setFont(QFont("Arial", 14, QFont.Bold))
        self.coin_count.setStyleSheet("color: #4a86e8;")
        
        coin_count_layout.addWidget(coin_label)
        coin_count_layout.addWidget(self.coin_count)
        coin_layout.addLayout(coin_count_layout)
        
        # Next coin timer
        timer_label = QLabel("Next coin in:")
        self.timer_progress = QProgressBar()
        self.timer_progress.setRange(0, 100)
        self.timer_progress.setValue(0)
        
        coin_layout.addWidget(timer_label)
        coin_layout.addWidget(self.timer_progress)
        
        layout.addWidget(coin_frame)
        
        # Convert button
        self.convert_button = QPushButton("Convert 1 Coin to Random Coupon")
        self.convert_button.clicked.connect(self.convert_coin)
        if self.coin_manager and self.coin_manager.coins < 1:
            self.convert_button.setEnabled(False)
        
        layout.addWidget(self.convert_button)
        
        # Button layout for additional options
        options_layout = QHBoxLayout()
        
        # View coupons button
        self.view_coupons_button = QPushButton("View My Coupons")
        self.view_coupons_button.clicked.connect(self.view_coupons)
        self.view_coupons_button.setIcon(QIcon.fromTheme("document-open"))
        
        # View coupon history button
        self.view_history_button = QPushButton("View Coupon History")
        self.view_history_button.clicked.connect(self.view_coupon_history)
        self.view_history_button.setIcon(QIcon.fromTheme("document-properties"))
        
        options_layout.addWidget(self.view_coupons_button)
        options_layout.addWidget(self.view_history_button)
        
        layout.addLayout(options_layout)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        layout.addWidget(self.close_button)
        
        # Update coin count display
        if self.coin_manager:
            self.update_coin_count(self.coin_manager.coins)
    
    @pyqtSlot(int)
    def update_coin_count(self, count):
        """Update the displayed coin count."""
        self.coin_count.setText(str(count))
        self.convert_button.setEnabled(count >= 1)
    
    def convert_coin(self):
        """Convert coins to a selected coupon."""
        try:
            if self.coin_manager:
                # Get available coupon rewards
                coupon_rewards = self.coin_manager.get_coupon_rewards()
                if not coupon_rewards:
                    QMessageBox.warning(self, "No Coupons Available", "No coupon types are available.")
                    return
                
                # Create coupon selection dialog
                selection_dialog = QDialog(self)
                selection_dialog.setWindowTitle("Select Coupon")
                selection_dialog.setMinimumWidth(500)
                selection_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #f5f5f5;
                    }
                    QLabel {
                        color: #333;
                    }
                    QListWidget {
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        padding: 15px;
                        border-bottom: 1px solid #eee;
                    }
                    QListWidget::item:selected {
                        background-color: #e6f0ff;
                        color: #333;
                    }
                    QPushButton {
                        padding: 8px 16px;
                        border-radius: 4px;
                    }
                    .cost-label {
                        color: #e74c3c;
                        font-weight: bold;
                    }
                """)
                
                layout = QVBoxLayout(selection_dialog)
                
                # Add instruction and current coins label
                header_layout = QHBoxLayout()
                label = QLabel("Choose a coupon to generate:")
                label.setStyleSheet("font-size: 14px; font-weight: bold;")
                coins_label = QLabel(f"Your coins: {self.coin_manager.coins}")
                coins_label.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
                header_layout.addWidget(label)
                header_layout.addStretch()
                header_layout.addWidget(coins_label)
                layout.addLayout(header_layout)
                
                # Create list widget for coupon selection
                list_widget = QListWidget()
                
                # Add coupon options to list with custom widgets
                for code, info in coupon_rewards.items():
                    item = QListWidgetItem()
                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)
                    
                    # Title and cost layout
                    title_layout = QHBoxLayout()
                    title_label = QLabel(f"<b>{code}</b>")
                    cost_label = QLabel(f"Cost: {info['cost']} coins")
                    cost_label.setStyleSheet("""
                        color: #e74c3c;
                        font-weight: bold;
                        padding: 2px 8px;
                        background: #ffeaea;
                        border-radius: 10px;
                    """)
                    
                    title_layout.addWidget(title_label)
                    title_layout.addStretch()
                    title_layout.addWidget(cost_label)
                    
                    # Description
                    desc_label = QLabel(info['description'])
                    desc_label.setStyleSheet("color: #666; padding-top: 5px;")
                    
                    item_layout.addLayout(title_layout)
                    item_layout.addWidget(desc_label)
                    
                    # Set fixed height for the item
                    item_widget.setFixedHeight(80)
                    
                    item.setSizeHint(item_widget.sizeHint())
                    list_widget.addItem(item)
                    list_widget.setItemWidget(item, item_widget)
                    
                    # Store the coupon code
                    item.setData(Qt.UserRole, code)
                    
                    # Disable item if not enough coins
                    if self.coin_manager.coins < info['cost']:
                        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                        item_widget.setStyleSheet("color: #999; background-color: #f9f9f9;")
                
                layout.addWidget(list_widget)
                
                # Add buttons
                button_layout = QHBoxLayout()
                cancel_button = QPushButton("Cancel")
                cancel_button.setStyleSheet("background-color: #e74c3c; color: white;")
                select_button = QPushButton("Generate Coupon")
                select_button.setStyleSheet("background-color: #2ecc71; color: white;")
                select_button.setDefault(True)
                
                button_layout.addWidget(cancel_button)
                button_layout.addWidget(select_button)
                layout.addLayout(button_layout)
                
                # Connect buttons
                cancel_button.clicked.connect(selection_dialog.reject)
                select_button.clicked.connect(selection_dialog.accept)
                
                # Show dialog and get result
                if selection_dialog.exec_() == QDialog.Accepted:
                    selected_item = list_widget.currentItem()
                    if selected_item:
                        selected_code = selected_item.data(Qt.UserRole)
                        selected_cost = coupon_rewards[selected_code]['cost']
                        
                        if self.coin_manager.coins < selected_cost:
                            QMessageBox.warning(self, "Error", f"Not enough coins. You need {selected_cost} coins.")
                            return
                        
                        # Deduct coins immediately
                        if not self.coin_manager.use_coins(selected_cost):
                            QMessageBox.warning(self, "Error", "Failed to deduct coins")
                            return
                        
                        # Update display immediately
                        self.update_coin_count(self.coin_manager.coins)
                        
                        # Convert to selected coupon
                        success, message = self.coin_manager.convert_to_coupon(selected_code)
                        if not success:
                            # Refund coins if conversion failed
                            self.coin_manager.add_coins(selected_cost)
                            self.update_coin_count(self.coin_manager.coins)
                            QMessageBox.warning(self, "Coupon Generation Failed", message)
                    else:
                        QMessageBox.warning(self, "Error", "Please select a coupon")
                    
        except Exception as e:
            print(f"Error converting coin to coupon: {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not convert coin to coupon: {str(e)}")
    
    def view_coupon_history(self):
        """Open the coupon history dialog."""
        try:
            if self.parent_window and hasattr(self.parent_window, 'show_coupon_history'):
                self.parent_window.show_coupon_history()
                self.close()  # Close the coin dialog when opening history
        except Exception as e:
            print(f"Error viewing coupon history: {str(e)}")
    
    @pyqtSlot(dict)
    def coupon_generated(self, coupon):
        """Handle a newly generated coupon."""
        try:
            print(f"Coupon generated in CoinDialog: {coupon}")
            
            # Create a custom message box for better appearance
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("New Coupon Generated!")
            msg_box.setIcon(QMessageBox.Information)
            
            # Set custom text with HTML formatting for better appearance
            html_message = f"""
            <style>
                .coupon-container {{ 
                    background-color: #e8f4fc; 
                    border-radius: 8px; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border: 2px dashed #3498db;
                }}
                .coupon-code {{ 
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #2980b9; 
                    margin-bottom: 5px;
                }}
                .coupon-desc {{ 
                    font-size: 14px; 
                    color: #34495e;
                }}
                .success-msg {{
                    color: #27ae60;
                    font-weight: bold;
                    margin-top: 10px;
                }}
            </style>
            <p>You've successfully converted 1 coin to a coupon!</p>
            <div class="coupon-container">
                <div class="coupon-code">{coupon['code']}</div>
                <div class="coupon-desc">{coupon['description']}</div>
            </div>
            <p class="success-msg">✓ This coupon has been added to your history</p>
            """
            
            msg_box.setText(html_message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.button(QMessageBox.Ok).setText("Great!")
            
            # Show the message box
            msg_box.exec_()
            
            # Add the coupon to the parent window's coupon list if available
            if self.parent_window:
                if hasattr(self.parent_window, 'add_coupon_to_list'):
                    self.parent_window.add_coupon_to_list(coupon)
                
        except Exception as e:
            print(f"Error in coupon_generated: {str(e)}")
            # Fallback to simple message box if custom one fails
            QMessageBox.information(
                self,
                "New Coupon Generated!",
                f"You've received a new coupon:\n\nCode: {coupon['code']}\nDescription: {coupon['description']}\n\nThis coupon has been added to your history.",
                QMessageBox.Ok
            )
    
    def view_coupons(self):
        """Open the coupon manager dialog."""
        if self.parent_window and hasattr(self.parent_window, 'show_coupons'):
            self.parent_window.show_coupons()
            self.close()  # Close the coin dialog when opening coupons

    def convert_coins_to_coupon(self):
        """Convert coins to a random coupon."""
        try:
            # Get coupon from coin manager
            coupon = self.coin_manager.convert_coins_to_coupon()
            
            if coupon:
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully generated coupon: {coupon['code']}\n{coupon['description']}"
                )
                
                # Update coin display
                self.update_coin_display()
                
                # Don't open coupon history dialog automatically
                # Remove or comment out any line that opens the history dialog
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate coupon: {str(e)}")