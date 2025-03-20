from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QHBoxLayout, QLabel,
                            QLineEdit, QMessageBox, QInputDialog)
from database.db_manager import DatabaseManager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
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
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QTableWidget {
                border: 2px solid #e9ecef;
                border-radius: 20px;
                background-color: white;
            }
        """)
        
        self.init_ui()
        self.load_bookmarks()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Bookmarks")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search bookmarks...")
        self.search_box.textChanged.connect(self.filter_bookmarks)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Bookmarks table
        self.bookmark_table = QTableWidget()
        self.bookmark_table.setColumnCount(2)
        self.bookmark_table.setHorizontalHeaderLabels(["Title", "URL"])
        self.bookmark_table.setColumnWidth(0, 300)
        self.bookmark_table.setColumnWidth(1, 450)
        self.bookmark_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.bookmark_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Bookmark")
        self.add_button.clicked.connect(self.add_bookmark)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_bookmark)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_bookmark)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def load_bookmarks(self):
        bookmarks = self.db_manager.get_bookmarks()
        self.bookmark_table.setRowCount(len(bookmarks))
        
        for row, bookmark in enumerate(bookmarks):
            id, title, url = bookmark
            self.bookmark_table.setItem(row, 0, QTableWidgetItem(title))
            self.bookmark_table.setItem(row, 1, QTableWidgetItem(url))
    
    def filter_bookmarks(self):
        search_text = self.search_box.text().lower()
        for row in range(self.bookmark_table.rowCount()):
            match_found = False
            for col in range(self.bookmark_table.columnCount()):
                item = self.bookmark_table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            self.bookmark_table.setRowHidden(row, not match_found)
    
    def add_bookmark(self):
        title, ok = QInputDialog.getText(self, 'Add Bookmark', 'Enter bookmark title:')
        if ok and title:
            url, ok = QInputDialog.getText(self, 'Add Bookmark', 'Enter URL:')
            if ok and url:
                self.db_manager.add_bookmark(title, url)
                self.load_bookmarks()
    
    def edit_bookmark(self):
        current_row = self.bookmark_table.currentRow()
        if current_row >= 0:
            current_title = self.bookmark_table.item(current_row, 0).text()
            current_url = self.bookmark_table.item(current_row, 1).text()
            
            title, ok = QInputDialog.getText(self, 'Edit Bookmark', 
                                           'Edit title:', text=current_title)
            if ok and title:
                url, ok = QInputDialog.getText(self, 'Edit Bookmark', 
                                             'Edit URL:', text=current_url)
                if ok and url:
                    self.db_manager.update_bookmark(current_url, title, url)
                    self.load_bookmarks()
    
    def delete_bookmark(self):
        current_row = self.bookmark_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Delete Confirmation',
                                       'Are you sure you want to delete this bookmark?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                url = self.bookmark_table.item(current_row, 1).text()
                self.db_manager.delete_bookmark(url)
                self.load_bookmarks()