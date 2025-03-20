from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox)
from database.db_manager import DatabaseManager
from PyQt5.QtCore import Qt

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browsing History")
        self.setGeometry(300, 300, 800, 600)
        self.db_manager = DatabaseManager()
        
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
        """)
        
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Browsing History")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search history...")
        self.search_box.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Create table for history items
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Title", "URL", "Visit Time"])
        self.history_table.setColumnWidth(0, 300)
        self.history_table.setColumnWidth(1, 350)
        self.history_table.setColumnWidth(2, 150)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setShowGrid(False)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Delete selected button
        self.delete_selected_button = QPushButton("Delete Selected")
        self.delete_selected_button.clicked.connect(self.delete_selected)
        
        # Clear history button
        self.clear_button = QPushButton("Clear History")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_history)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        # Add buttons to layout
        button_layout.addWidget(self.delete_selected_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        # Add widgets to main layout
        layout.addWidget(self.history_table)
        layout.addLayout(button_layout)

    def filter_history(self):
        search_text = self.search_box.text().lower()
        for row in range(self.history_table.rowCount()):
            match_found = False
            for col in range(self.history_table.columnCount()):
                item = self.history_table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            self.history_table.setRowHidden(row, not match_found)

    def delete_selected(self):
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            return
            
        reply = QMessageBox.question(self, 'Delete Confirmation',
                                   'Are you sure you want to delete the selected entries?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove rows from bottom to top to avoid index shifting
            for row in sorted(selected_rows, reverse=True):
                # Get the URL to delete from database
                url = self.history_table.item(row, 1).text()
                # Delete from database (you'll need to implement this in DatabaseManager)
                self.db_manager.delete_history_entry(url)
                self.history_table.removeRow(row)
    
    def load_history(self):
        """Load browsing history from database and display in table."""
        history_items = self.db_manager.get_history()
        
        self.history_table.setRowCount(len(history_items))
        
        for row, item in enumerate(history_items):
            id, url, title, visit_time = item
            
            # Use URL as title if title is None
            title_text = title if title else url
            
            title_item = QTableWidgetItem(title_text)
            url_item = QTableWidgetItem(url)
            time_item = QTableWidgetItem(visit_time)
            
            self.history_table.setItem(row, 0, title_item)
            self.history_table.setItem(row, 1, url_item)
            self.history_table.setItem(row, 2, time_item)
    
    def clear_history(self):
        """Clear all browsing history."""
        reply = QMessageBox.question(self, 'Clear History',
                                   'Are you sure you want to clear all browsing history?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db_manager.clear_history()
            self.history_table.setRowCount(0)
            QMessageBox.information(self, "Success", "History cleared successfully")
