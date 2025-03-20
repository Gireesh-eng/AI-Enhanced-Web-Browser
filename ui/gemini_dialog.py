from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QComboBox,
                              QWidget, QProgressBar, QMessageBox,
                             QDesktopWidget, QStyle, QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QFont

class GeminiDialog(QDialog):
    """Dialog for displaying Gemini AI processing results."""
    
    def __init__(self, parent=None, gemini_helper=None):
        super().__init__(parent)
        self.setWindowTitle("Gemini AI Assistant")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Store reference to Gemini helper
        self.gemini_helper = gemini_helper
        self.parent_window = parent
        
        # Set up UI
        self.setup_ui()
        
        # Connect signals if helper is provided
        if self.gemini_helper:
            self.gemini_helper.result_ready.connect(self.on_result_ready)
        
        # Set up progress animation
        self.progress_dots = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress_text)
        
        # Initialize window state
        self.is_fullscreen = False
        self.center_and_resize()
    
    def center_and_resize(self):
        """Center the dialog and set its initial size."""
        desktop = QDesktopWidget().availableGeometry()
        width = int(desktop.width() * 0.8)
        height = int(desktop.height() * 0.8)
        self.setGeometry((desktop.width() - width) // 2,
                        (desktop.height() - height) // 2,
                        width, height)
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Set modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 150px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Top bar with title and full-screen button
        top_bar = QHBoxLayout()
        
        title_label = QLabel("Gemini AI Assistant")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        top_bar.addWidget(title_label)
        
        top_bar.addStretch()
        
        self.fullscreen_button = QPushButton()
        self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        self.fullscreen_button.setToolTip("Toggle Full Screen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_button.setFixedSize(32, 32)
        top_bar.addWidget(self.fullscreen_button)
        
        main_layout.addLayout(top_bar)
        
        # Information label about API key
        info_label = QLabel("Using Gemini AI for processing")
        info_label.setStyleSheet("color: #3498db; font-style: italic;")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Action selection area
        action_widget = QWidget()
        action_widget.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        action_layout = QHBoxLayout(action_widget)
        
        # Action selection
        action_label = QLabel("Select Action:")
        action_label.setStyleSheet("font-weight: bold;")
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Summarize", "Translate", "Explain", "Ask Gemini"])
        self.action_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.action_combo)
        action_layout.addSpacing(20)
        
        # Ask Gemini button
        self.ask_gemini_button = QPushButton("Ask Gemini")
        self.ask_gemini_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
        """)
        self.ask_gemini_button.clicked.connect(self.show_prompt_dialog)
        action_layout.addWidget(self.ask_gemini_button)
        action_layout.addSpacing(20)
        
        # Target language for translation
        self.target_lang_label = QLabel("Target Language:")
        self.target_lang_label.setStyleSheet("font-weight: bold;")
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            "English", "Spanish", "French", "German", "Chinese", "Japanese",
            "Korean", "Russian", "Arabic", "Hindi", "Portuguese", "Italian",
            "Dutch", "Polish", "Turkish", "Vietnamese", "Thai", "Indonesian"
        ])
        
        action_layout.addWidget(self.target_lang_label)
        action_layout.addWidget(self.target_lang_combo)
        
        # Show/hide target language based on action
        self.action_combo.currentTextChanged.connect(self.on_action_changed)
        self.target_lang_label.setVisible(False)
        self.target_lang_combo.setVisible(False)
        
        action_layout.addStretch()
        
        # Button container for better layout
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # Process button
        self.process_button = QPushButton("Process with Gemini")
        self.process_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }
        """)
        self.process_button.clicked.connect(self.process_content)
        button_layout.addWidget(self.process_button)
        
        # Process Again button
        self.process_again_button = QPushButton("Process Again")
        self.process_again_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.process_again_button.clicked.connect(self.process_again)
        self.process_again_button.setEnabled(False)
        button_layout.addWidget(self.process_again_button)
        
        action_layout.addWidget(button_container)
        
        main_layout.addWidget(action_widget)
        
        # Status and progress
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        
        self.status_label = QLabel("Ready to process content")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(status_widget)
        
        # Result area
        result_widget = QWidget()
        result_widget.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        result_layout = QVBoxLayout(result_widget)
        
        result_header = QHBoxLayout()
        result_label = QLabel("Result:")
        result_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        result_header.addWidget(result_label)
        
        # Add source language label for translations
        self.source_lang_label = QLabel("")
        self.source_lang_label.setStyleSheet("color: #666; font-style: italic;")
        result_header.addWidget(self.source_lang_label)
        result_header.addStretch()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        result_header.addWidget(self.copy_button)
        
        result_layout.addLayout(result_header)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Arial", 11))
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        main_layout.addWidget(result_widget, stretch=1)
        
        # Store the last processed content
        self.last_content = None
        self.last_metadata = None
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and normal window state."""
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        else:
            self.showMaximized()
            self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarNormalButton))
        self.is_fullscreen = not self.is_fullscreen
    
    def on_action_changed(self, action_text):
        """Show/hide target language based on action."""
        is_translate = action_text.lower() == "translate"
        is_ask_gemini = action_text.lower() == "ask gemini"
        
        self.target_lang_label.setVisible(is_translate)
        self.target_lang_combo.setVisible(is_translate)
        
        # Change the process button text based on the action
        if is_ask_gemini:
            self.process_button.setText("Ask Question")
        else:
            self.process_button.setText("Process with Gemini")
    
    def process_again(self):
        """Process the last content again with current settings."""
        if not self.last_content or not self.last_metadata:
            QMessageBox.warning(self, "Error", "No previous content to process.")
            return
        
        # Get the selected action
        action = self.action_combo.currentText().lower()
        
        # Get target language for translation
        target_language = self.target_lang_combo.currentText() if action == "translate" else "English"
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.process_button.setEnabled(False)
        self.process_again_button.setEnabled(False)
        self.status_label.setText(f"Processing with Gemini...")
        self.status_label.setStyleSheet("color: #3498db;")
        
        # Start progress animation
        self.progress_timer.start(500)
        
        # Clear previous result
        self.result_text.clear()
        self.copy_button.setEnabled(False)
        
        try:
            if action == "summarize":
                self.gemini_helper._summarize_with_gemini(self.last_content, self.last_metadata)
            elif action == "translate":
                self.gemini_helper._translate_with_gemini(self.last_content, self.last_metadata, target_language)
            elif action == "explain":
                self.gemini_helper._explain_with_gemini(self.last_content, self.last_metadata)
        except Exception as e:
            self.show_error(f"Error processing content: {str(e)}")
    
    def process_content(self):
        """Process the current page content with Gemini."""
        # Check if Gemini helper has API key
        if not self.gemini_helper:
            QMessageBox.warning(self, "Error", "Gemini helper not initialized.")
            return
        
        # Get the selected action
        action = self.action_combo.currentText().lower()
        
        # If action is "ask gemini", show the prompt dialog
        if action == "ask gemini":
            self.show_prompt_dialog()
            return
        
        # Get target language for translation
        target_language = self.target_lang_combo.currentText() if action == "translate" else "English"
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.process_button.setEnabled(False)
        self.process_again_button.setEnabled(False)
        self.status_label.setText(f"Processing with Gemini...")
        self.status_label.setStyleSheet("color: #3498db;")
        
        # Start progress animation
        self.progress_timer.start(500)
        
        # Clear previous result
        self.result_text.clear()
        self.copy_button.setEnabled(False)
        
        # Process with Gemini
        if self.parent_window and hasattr(self.parent_window, 'browser'):
            try:
                self.gemini_helper.process_with_gemini(
                    self.parent_window.browser.page(), 
                    action,
                    target_language
                )
            except Exception as e:
                self.show_error(f"Error processing content: {str(e)}")
        else:
            self.show_error("Cannot access the browser.")
    
    def update_progress_text(self):
        """Update the progress text animation."""
        self.progress_dots = (self.progress_dots + 1) % 4
        dots = "." * self.progress_dots
        self.status_label.setText(f"Processing with Gemini{dots}")
    
    def show_error(self, message):
        """Show an error message."""
        # Stop progress
        if self.progress_timer.isActive():
            self.progress_timer.stop()
        
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.process_again_button.setEnabled(True)
        
        # Show error
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: #e74c3c;")  # Red color for error
        
        # Show in result area too
        self.result_text.setPlainText(f"Error: {message}\n\nPlease check your API key in the .env file and try again.")
    
    def copy_to_clipboard(self):
        """Copy the result to clipboard."""
        self.result_text.selectAll()
        self.result_text.copy()
        self.status_label.setText("Result copied to clipboard!")
        self.status_label.setStyleSheet("color: #27ae60;")  # Green color for success
    
    @pyqtSlot(str, str)
    def on_result_ready(self, action, result):
        """Handle the result from Gemini."""
        try:
            # Stop the progress animation
            if self.progress_timer.isActive():
                self.progress_timer.stop()
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.process_button.setEnabled(True)
            self.process_again_button.setEnabled(True)
            
            if action == 'error':
                self.show_error(result)
                return
            
            # Display the result
            self.result_text.setPlainText(result)
            
            # Update status
            self.status_label.setText(f"{action.capitalize()} completed successfully!")
            self.status_label.setStyleSheet("color: #27ae60;")  # Green color for success
            
            # Enable copy button
            self.copy_button.setEnabled(True)
            
            # Store the processed content for "Process Again"
            if hasattr(self.parent_window, 'browser'):
                page = self.parent_window.browser.page()
                if page:
                    self.last_content = result
                    self.last_metadata = {"title": self.parent_window.browser.title()}
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in on_result_ready: {str(e)}\nDetails: {error_details}")
            self.show_error(f"Error displaying result: {str(e)}") 
    
    def show_prompt_dialog(self):
        """Show a dialog to input a question for Gemini."""
        question, ok = QInputDialog.getText(
            self, 
            "Ask Gemini", 
            "Enter your question:",
            QLineEdit.Normal, 
            ""
        )
        
        if ok and question:
            self.process_question(question)
    
    def process_question(self, question):
        """Process a user question with Gemini."""
        # Show progress
        self.progress_bar.setVisible(True)
        self.process_button.setEnabled(False)
        self.process_again_button.setEnabled(False)
        self.status_label.setText("Processing question with Gemini...")
        self.status_label.setStyleSheet("color: #3498db;")
        
        # Start progress animation
        self.progress_timer.start(500)
        
        # Clear previous result
        self.result_text.clear()
        self.copy_button.setEnabled(False)
        
        try:
            # First check if we can find the answer in the current page
            current_page_content = ""
            if self.parent_window and hasattr(self.parent_window, 'browser'):
                page = self.parent_window.browser.page()
                if page:
                    # Get the current page content using the Gemini helper
                    self.gemini_helper.process_question(
                        page,
                        question,
                        self.on_question_processed
                    )
                else:
                    self.show_error("Cannot access the browser page.")
            else:
                self.show_error("Cannot access the browser.")
        except Exception as e:
            self.show_error(f"Error processing question: {str(e)}")
    
    def on_question_processed(self, result):
        """Handle the result from processing a question."""
        try:
            # Stop the progress animation
            if self.progress_timer.isActive():
                self.progress_timer.stop()
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.process_button.setEnabled(True)
            self.process_again_button.setEnabled(True)
            
            if result.startswith("Error:"):
                # Check for specific error types and provide more helpful messages
                if "API key" in result or "timed out" in result:
                    # Show a detailed error message box with instructions
                    error_msg = QMessageBox(self)
                    error_msg.setIcon(QMessageBox.Warning)
                    error_msg.setWindowTitle("API Error")
                    
                    if "timed out" in result:
                        error_msg.setText("Request to Gemini API timed out")
                        error_msg.setInformativeText(
                            "This could be due to one of the following reasons:\n\n"
                            "1. Your API key may be invalid or expired\n"
                            "2. Network connectivity issues\n"
                            "3. The content being processed is too large\n\n"
                            "Please check your .env file and ensure your GEMINI_API_KEY is correct."
                        )
                    else:
                        error_msg.setText("API Key Issue")
                        error_msg.setInformativeText(
                            "There appears to be an issue with your Gemini API key.\n\n"
                            "Please check the following:\n"
                            "1. Ensure the .env file exists in the project root directory\n"
                            "2. Verify that GEMINI_API_KEY is set correctly in the .env file\n"
                            "3. Make sure the API key is valid and active\n\n"
                            "You can get a new API key from: https://aistudio.google.com/app/apikey"
                        )
                    
                    error_msg.setDetailedText(result)
                    error_msg.setStandardButtons(QMessageBox.Ok)
                    error_msg.exec_()
                
                # Still show the error in the status label
                self.show_error(result.replace("Error: ", ""))
                return
            
            # Display the result
            self.result_text.setPlainText(result)
            
            # Update status
            self.status_label.setText("Question answered successfully!")
            self.status_label.setStyleSheet("color: #27ae60;")  # Green color for success
            
            # Enable copy button
            self.copy_button.setEnabled(True)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in on_question_processed: {str(e)}\nDetails: {error_details}")
            self.show_error(f"Error displaying result: {str(e)}")