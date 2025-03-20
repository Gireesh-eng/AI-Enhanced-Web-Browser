from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, 
                           QLineEdit, QToolBar, QAction, QMenu, QLabel, 
                           QStatusBar, QHBoxLayout, QFrame, QMessageBox)
from PyQt5.QtCore import QUrl, QTimer, QDateTime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QFont, QPixmap
import webbrowser
import os
import subprocess
import platform
import time

from ui.history_dialog import HistoryDialog
from ui.coupon_dialog import CouponDialog
from ui.coin_dialog import CoinDialog
from ui.coupon_history_dialog import CouponHistoryDialog
from ui.gemini_dialog import GeminiDialog
from database.db_manager import DatabaseManager
from utils.helpers import format_url
from utils.coin_manager import CoinManager
from utils.gemini_helper import GeminiHelper
from ui.bookmark_dialog import BookmarkDialog

class BrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Web Browser")
        self.setGeometry(100, 100, 1024, 768)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize coin manager
        self.coin_manager = CoinManager()
        self.coin_manager.coin_count_changed.connect(self.update_coin_display)
        self.coin_manager.coupon_generated.connect(self.on_coupon_generated)
        
        # Initialize Gemini helper
        self.gemini_helper = GeminiHelper()
        
        # Store generated coupons history
        self.generated_coupons = []
        
        # Current URL for tracking
        self.current_url = "https://www.google.com"
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Apply stylesheet for better UI
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a86e8, stop:1 #3a76d8);
                spacing: 8px;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #3a76d8;
            }
            QToolBar QLineEdit {
                border-radius: 20px;
                padding: 8px 15px;
                background-color: rgba(255, 255, 255, 0.95);
                min-width: 400px;
                font-size: 14px;
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }
            QToolBar QLineEdit:focus {
                border: 1px solid #4a86e8;
                background-color: white;
                box-shadow: 0 0 5px rgba(74, 134, 232, 0.3);
            }
            QStatusBar {
                background-color: #f8f9fa;
                color: #495057;
                border-top: 1px solid #e9ecef;
            }
            QStatusBar QLabel {
                padding: 5px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: 500;
                font-size: 13px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #3a76d8;
                transform: translateY(-1px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
            QFrame#coinWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e6f0ff, stop:1 #f0f7ff);
                border-radius: 15px;
                padding: 5px 12px;
                border: 1px solid #d1e3ff;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e9ecef;
            }
            QMenuBar::item {
                padding: 8px 12px;
                color: #495057;
            }
            QMenuBar::item:selected {
                background-color: #e9ecef;
                border-radius: 4px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f1f3f5;
                color: #4a86e8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e9ecef;
                margin: 5px 0;
            }
        """)
        
        # Create navigation toolbar
        self.toolbar = QToolBar("Navigation")
        self.addToolBar(self.toolbar)
        
        # Back button
        self.back_button = QAction("←", self)
        self.back_button.setToolTip("Back")
        self.back_button.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_button)
        
        # Forward button
        self.forward_button = QAction("→", self)
        self.forward_button.setToolTip("Forward")
        self.forward_button.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_button)
        
        # Reload button
        self.reload_button = QAction("🔄", self)
        self.reload_button.setToolTip("Reload")
        self.reload_button.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_button)
        
        # Add bookmark button
        self.add_bookmark_button = QAction("⭐", self)
        self.add_bookmark_button.setToolTip("Add Bookmark")
        self.add_bookmark_button.triggered.connect(self.add_current_bookmark)
        self.toolbar.addAction(self.add_bookmark_button)
        
        # Show bookmarks button
        self.show_bookmarks_button = QAction("📚", self)
        self.show_bookmarks_button.setToolTip("Show Bookmarks")
        self.show_bookmarks_button.triggered.connect(self.show_bookmarks)
        self.toolbar.addAction(self.show_bookmarks_button)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)
        
        # Create menu bar
        self.menu_bar = self.menuBar()
        
        # File menu
        file_menu = self.menu_bar.addMenu("File")
        file_menu.setStyleSheet("""
            QMenu::item {
                padding: 10px 25px;
                border-radius: 6px;
                margin: 2px 5px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #e7f0ff;
                color: #4a86e8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e9ecef;
                margin: 8px 5px;
            }
        """)
        
        # History action
        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        file_menu.addAction(history_action)
        
        # Coupon History action
        coupon_history_action = QAction("Coupon History", self)
        coupon_history_action.triggered.connect(self.show_coupon_history)
        file_menu.addAction(coupon_history_action)
        
        # Coin action
        coin_action = QAction("Coins", self)
        coin_action.triggered.connect(self.show_coins)
        file_menu.addAction(coin_action)
        
        # OpenAI GPT-4 action
        openai_action = QAction("AI Assistant", self)
        openai_action.triggered.connect(self.show_ai_assistant)
        file_menu.addAction(openai_action)
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = self.menu_bar.addMenu("Tools")
        
        # AI Assistant submenu
        ai_menu = QMenu("AI Assistant", self)
        
        # AI actions
        summarize_action = QAction("Summarize", self)
        summarize_action.triggered.connect(lambda: self.use_ai_assistant("summarize"))
        ai_menu.addAction(summarize_action)
        
        translate_action = QAction("Translate", self)
        translate_action.triggered.connect(lambda: self.use_ai_assistant("translate"))
        ai_menu.addAction(translate_action)
        
        explain_action = QAction("Explain", self)
        explain_action.triggered.connect(lambda: self.use_ai_assistant("explain"))
        ai_menu.addAction(explain_action)
        
        ask_gemini_action = QAction("Ask Gemini", self)
        ask_gemini_action.triggered.connect(lambda: self.use_ai_assistant("ask gemini"))
        ai_menu.addAction(ask_gemini_action)
        
        tools_menu.addMenu(ai_menu)
        
        # Create status bar with coin display
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Create coin widget for status bar
        self.coin_widget = QFrame()
        self.coin_widget.setObjectName("coinWidget")
        coin_layout = QHBoxLayout(self.coin_widget)
        coin_layout.setContentsMargins(5, 2, 5, 2)
        
        coin_icon_label = QLabel("🪙")
        coin_icon_label.setFont(QFont("Arial", 12))
        
        self.coin_count_label = QLabel("0")
        self.coin_count_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        coin_layout.addWidget(coin_icon_label)
        coin_layout.addWidget(self.coin_count_label)
        
        # Add coin widget to status bar
        self.statusBar.addPermanentWidget(self.coin_widget)
        
        # Web view with enhanced settings
        self.browser = QWebEngineView()
        
        # Configure browser settings
        profile = self.browser.page().profile()
        settings = self.browser.settings()
        
        # Enable persistent cookies
        profile.setPersistentCookiesPolicy(profile.AllowPersistentCookies)
        profile.setPersistentStoragePath(os.path.join(os.path.dirname(__file__), 'browser_data'))
        
        # Enable JavaScript
        settings.setAttribute(settings.JavascriptEnabled, True)
        settings.setAttribute(settings.JavascriptCanOpenWindows, True)
        settings.setAttribute(settings.JavascriptCanAccessClipboard, True)
        
        # Enable form features
        settings.setAttribute(settings.LocalStorageEnabled, True)
        settings.setAttribute(settings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(settings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(settings.AutoLoadImages, True)
        settings.setAttribute(settings.AllowWindowActivationFromJavaScript, True)
        
        # Connect signals
        self.browser.urlChanged.connect(self.update_url)
        self.browser.titleChanged.connect(self.update_title)
        self.browser.loadFinished.connect(self.on_page_load_finished)
        self.browser.page().javaScriptConsoleMessage = self.handle_console_message
        
        self.layout.addWidget(self.browser)
        
        # Inject Gemini content extraction script when a new page is loaded
        self.gemini_helper.inject_script(self.browser.page())
        
        # Load default page - use Google directly
        self.browser.setUrl(QUrl("https://www.google.com"))
        
        # Create progress timer for coin animation
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_coin_progress)
        self.progress_timer.start(500)  # Update every 500ms
        self.progress_value = 0
        
        # Track recently opened URLs in Chrome to prevent duplicates
        self.recently_opened_in_chrome = {}
        
        # Create a single reusable timer for video detection
        self.video_check_timer = QTimer(self)
        self.video_check_timer.setSingleShot(True)
        self.video_check_timer.timeout.connect(self.check_for_video_players)
        
        # Create a single reusable timer for error detection
        self.error_check_timer = QTimer(self)
        self.error_check_timer.timeout.connect(self.check_for_jw_player_error)
        
        # Force initial coin display update
        self.update_coin_display(self.coin_manager.get_coins())
        
        # Start the coin timer after everything is set up
        self.coin_manager.start_timer()
    
    def navigate_back(self):
        self.browser.back()
    
    def navigate_forward(self):
        self.browser.forward()
    
    def reload_page(self):
        self.browser.reload()
    
    def navigate_to_url(self):
        """Navigate to the URL entered in the URL bar."""
        url = self.url_bar.text()
        formatted_url = format_url(url)
        self.current_url = formatted_url
        
        # Only check for video websites if it's in our list
        if self.is_video_website(formatted_url):
            # Open in Chrome for better video playback
            self.open_in_chrome(formatted_url)
            
            # Update the URL bar and title
            self.url_bar.setText(formatted_url)
            self.setWindowTitle(f"External Browser - {formatted_url}")
            
            # Add to history
            self.db_manager.add_history_entry(formatted_url, "External Browser - Video Site")
            
            # Show a message about external browser mode
            self.statusBar.showMessage("Video website opened in Chrome for better compatibility", 5000)
        else:
            # Load all other URLs in the internal browser
            self.browser.setUrl(QUrl(formatted_url))
            self.statusBar.showMessage(f"Navigating to: {formatted_url}", 3000)
    
    def update_url(self, url):
        """Update the URL bar when the URL changes."""
        self.url_bar.setText(url.toString())
        self.current_url = url.toString()
        
        # Add to history
        self.db_manager.add_history_entry(url.toString(), self.browser.title())
    
    def update_title(self, title):
        self.setWindowTitle(f"{title} - Simple Web Browser")
    
    def show_history(self):
        """Show the browsing history dialog."""
        history_dialog = HistoryDialog(self)
        history_dialog.exec_()
    
    def show_coupons(self):
        """Show the coupon manager dialog."""
        coupon_dialog = CouponDialog(self)
        coupon_dialog.exec_()
    
    def show_coupon_history(self):
        """Show the coupon history dialog."""
        try:
            history_dialog = CouponHistoryDialog(self, self.coin_manager)
            
            # Add all coupons from memory history
            for coupon in self.generated_coupons:
                history_dialog.add_coupon_to_history(coupon)
            
            # Also add coupons from database
            db_coupons = self.coin_manager.get_coupon_history()
            for coupon_data in db_coupons:
                coupon_type, cost, created_at = coupon_data
                coupon = {
                    "code": f"{coupon_type}{created_at.strftime('%m%d%H%M%S')}",
                    "description": self.coin_manager.COUPON_REWARDS[coupon_type]["description"],
                    "cost": cost,
                    "generated_time": created_at.isoformat()
                }
                history_dialog.add_coupon_to_history(coupon)
            
            history_dialog.exec_()
        except Exception as e:
            print(f"Error showing coupon history: {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not display coupon history: {str(e)}")
    
    def show_coins(self):
        """Show the coin rewards dialog."""
        coin_dialog = CoinDialog(self, self.coin_manager)
        coin_dialog.exec_()
    
    def update_coin_display(self, count):
        """Update the coin count in the status bar."""
        try:
            self.coin_count_label.setText(str(count))
            # Force immediate update
            self.coin_count_label.repaint()
            self.statusBar.repaint()
        except Exception as e:
            print(f"Error updating coin display: {str(e)}")
    
    def update_coin_progress(self):
        """Update the coin progress animation."""
        self.progress_value = (self.progress_value + 1) % 100
        
        # If we have a coin dialog open, update its progress bar
        for widget in self.findChildren(CoinDialog):
            if hasattr(widget, 'timer_progress'):
                widget.timer_progress.setValue(self.progress_value)
    
    def add_coupon_to_list(self, coupon):
        """Add a coupon to the coupon list (called from CoinDialog)."""
        # Find any open coupon dialogs and add the coupon to them
        for widget in self.findChildren(CouponDialog):
            if hasattr(widget, 'add_coupon_to_list'):
                widget.add_coupon_to_list(coupon)
                return True
        return False
    
    def on_coupon_generated(self, coupon):
        """Handle a newly generated coupon."""
        try:
            print(f"Main window received coupon: {coupon}")
            
            # Add timestamp to coupon
            coupon_with_time = coupon.copy()
            if "generated_time" not in coupon_with_time:
                coupon_with_time["generated_time"] = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            
            # Add to memory list
            self.generated_coupons.append(coupon_with_time)
            
            # Update any open coupon history dialogs
            self.update_coupon_history_dialogs(coupon_with_time)
            
            # Show notification if needed
            print(f"New coupon generated: {coupon['code']}")
        except Exception as e:
            print(f"Error in on_coupon_generated: {str(e)}")
    
    def update_coupon_history_dialogs(self, coupon):
        """Update any open coupon history dialogs with the new coupon."""
        try:
            from ui.coupon_history_dialog import CouponHistoryDialog
            
            # Find any open coupon history dialogs and add the coupon to them
            for widget in self.findChildren(CouponHistoryDialog):
                if hasattr(widget, 'add_coupon_to_history'):
                    print(f"Adding coupon to history dialog: {coupon['code']}")
                    widget.add_coupon_to_history(coupon)
                    widget.update()  # Force UI update
        except Exception as e:
            print(f"Error updating coupon history dialogs: {str(e)}")
    
    def show_ai_assistant(self):
        """Show the AI assistant dialog."""
        try:
            dialog = GeminiDialog(self, self.gemini_helper)
            dialog.show()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error showing AI assistant: {str(e)}\nDetails: {error_details}")
            QMessageBox.warning(self, "AI Error", 
                               f"Error initializing AI: {str(e)}")
    
    def use_ai_assistant(self, action):
        """Use AI assistant with the specified action."""
        try:
            # Show the dialog
            dialog = GeminiDialog(self, self.gemini_helper)
            
            # Set the action in the combo box
            index = -1
            if action == "summarize":
                index = 0
            elif action == "translate":
                index = 1
            elif action == "explain":
                index = 2
            elif action == "ask gemini":
                index = 3
                
            if index >= 0:
                dialog.action_combo.setCurrentIndex(index)
                # Automatically process with the selected action
                dialog.process_content()
                
            dialog.show()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error using AI: {str(e)}\nDetails: {error_details}")
            QMessageBox.warning(self, "AI Error", 
                               f"Error using AI: {str(e)}")
    
    def open_in_chrome(self, url):
        """Open the URL in Chrome browser."""
        try:
            # Only open if it's a video site and not already opened recently
            if self.is_video_website(url):
                # Check if URL was recently opened (within last 5 seconds)
                current_time = time.time()
                if url in self.recently_opened_in_chrome:
                    if current_time - self.recently_opened_in_chrome[url] < 5:
                        return  # Skip if opened too recently
                
                # Update timestamp for this URL
                self.recently_opened_in_chrome[url] = current_time
                
                # Clean up old entries
                self.recently_opened_in_chrome = {
                    k: v for k, v in self.recently_opened_in_chrome.items()
                    if current_time - v < 60  # Remove entries older than 60 seconds
                }
                
                # Open in Chrome based on platform
                if platform.system() == 'Windows':
                    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
                    if not os.path.exists(chrome_path):
                        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
                    if os.path.exists(chrome_path):
                        subprocess.Popen([chrome_path, url])
                    else:
                        webbrowser.get('chrome').open(url)
                elif platform.system() == 'Linux':
                    try:
                        subprocess.Popen(['google-chrome', url])
                    except:
                        subprocess.Popen(['chromium-browser', url])
                else:  # macOS and others
                    webbrowser.get('chrome').open(url)
                
                print(f"Opened in Chrome: {url}")
                
        except Exception as e:
            print(f"Error opening in Chrome: {str(e)}")
            # Fallback to default browser if Chrome fails
            webbrowser.open(url)
    
    def on_page_load_finished(self, success):
        """Handle page load finished event."""
        try:
            if success:
                # Inject Gemini content extraction script when a new page is loaded
                self.gemini_helper.inject_script(self.browser.page())
                
                # Inject video player detection script
                self.inject_video_detection_script()
                
                # Add a specific error listener for JW Player errors
                self.inject_error_listener()
                
                # Stop any existing timers and restart them
                if hasattr(self, 'video_check_timer'):
                    self.video_check_timer.stop()
                    self.video_check_timer.start(2000)  # Check after 2 seconds
                
                if hasattr(self, 'error_check_timer'):
                    self.error_check_timer.stop()
                    self.error_check_timer.start(1500)  # Check every 1.5 seconds
        except Exception as e:
            print(f"Error injecting scripts: {str(e)}")
    
    def check_for_video_players(self):
        """Check for video players on the page."""
        try:
            # Get the current URL
            current_url = self.browser.url().toString()
            
            # Don't check YouTube URLs
            if 'youtube.com' in current_url.lower():
                return
                
            # Inject script to check for video players
            script = """
            (function() {
                var videoElements = document.getElementsByTagName('video');
                var iframeElements = document.getElementsByTagName('iframe');
                var jwplayers = document.querySelectorAll('[id^="jwplayer"]');
                var videoPlayers = document.querySelectorAll('[class*="player"],[class*="Player"],[id*="player"],[id*="Player"]');
                
                return {
                    hasVideo: videoElements.length > 0,
                    hasIframe: iframeElements.length > 0,
                    hasJWPlayer: jwplayers.length > 0,
                    hasVideoPlayer: videoPlayers.length > 0
                };
            })();
            """
            
            self.browser.page().runJavaScript(script, self.handle_video_check_result)
            
        except Exception as e:
            print(f"Error checking for video players: {str(e)}")
    
    def handle_video_check_result(self, result):
        """Handle the result of the video player check."""
        try:
            current_url = self.browser.url().toString()
            
            # Only proceed if it's a known video site
            if self.is_video_website(current_url):
                if result and (result.get('hasJWPlayer') or result.get('hasVideo')):
                    # Don't redirect YouTube
                    if 'youtube.com' in current_url.lower():
                        return
                        
                    print(f"Video player detected on {current_url}")
                    self.open_in_chrome(current_url)
                
        except Exception as e:
            print(f"Error handling video check result: {str(e)}")
    
    def inject_video_detection_script(self):
        """Inject JavaScript to detect video players and redirect to Chrome if needed."""
        try:
            # JavaScript to detect JW Player and other common video players
            js_code = """
            (function() {
                // Function to check for video players
                function checkForVideoPlayers() {
                    console.log("Checking for video players...");
                    
                    // Check for JW Player
                    if (window.jwplayer || document.querySelector('div[id^="jw-player"]') || 
                        document.querySelector('script[src*="jwplayer"]')) {
                        console.log("JW Player detected!");
                        return "JW Player";
                    }
                    
                    // Check for HTML5 video elements
                    if (document.querySelector('video')) {
                        console.log("HTML5 video detected!");
                        return "HTML5 Video";
                    }
                    
                    // Check for iframe embeds (YouTube, Vimeo, etc.)
                    const iframes = document.querySelectorAll('iframe');
                    for (let i = 0; i < iframes.length; i++) {
                        const src = iframes[i].src || '';
                        if (src.includes('youtube.com') || src.includes('vimeo.com') || 
                            src.includes('dailymotion.com') || src.includes('player.')) {
                            console.log("Video iframe detected: " + src);
                            return "Embedded Video";
                        }
                    }
                    
                    // Check for common video player classes and IDs
                    const videoSelectors = [
                        '.video-js', '.plyr', '.mediaelement', '.mejs-container',
                        '#player', '.player', '[class*="player"]', '[id*="player"]',
                        '.video-container', '.video-wrapper'
                    ];
                    
                    for (let i = 0; i < videoSelectors.length; i++) {
                        if (document.querySelector(videoSelectors[i])) {
                            console.log("Video player element detected: " + videoSelectors[i]);
                            return "Generic Video Player";
                        }
                    }
                    
                    // Check for JW Player errors in the DOM
                    if (document.body.innerHTML.includes('Error 102630') || 
                        document.body.innerHTML.includes('JW Player Error')) {
                        console.log("JW Player error text detected in page!");
                        return "JW Player Error";
                    }
                    
                    return null;
                }
                
                return checkForVideoPlayers();
            })();
            """
            
            # Inject the script and get the result directly
            self.browser.page().runJavaScript(js_code, self.handle_video_detection_result)
            
        except Exception as e:
            print(f"Error injecting video detection script: {str(e)}")
    
    def handle_video_detection_result(self, result):
        """Handle the result of the video player detection script."""
        try:
            if result:
                print(f"Video player detected: {result}")
                
                # Get the current URL
                current_url = self.browser.url().toString()
                
                # Show a message
                self.statusBar.showMessage(f"Video player ({result}) detected. Opening in Chrome...", 5000)
                
                # Open the URL in Chrome
                self.open_in_chrome(current_url)
        except Exception as e:
            print(f"Error handling video detection result: {str(e)}")
    
    def inject_error_listener(self):
        """Inject a specific error listener for JW Player errors."""
        try:
            # JavaScript to detect JW Player errors
            js_code = """
            (function() {
                console.log("Setting up JW Player error listener...");
                
                // Global error handler to catch JW Player errors
                window.addEventListener('error', function(event) {
                    console.log("Error event captured:", event.message);
                    
                    // Check if this is a JW Player error
                    if (event.message && (
                        event.message.includes('jwplayer') || 
                        event.message.includes('JW Player') ||
                        event.message.includes('Error 102630')
                    )) {
                        console.log("JW Player error detected:", event.message);
                        
                        // Return true to indicate we found a JW Player error
                        window.jwPlayerErrorDetected = true;
                        
                        // Create a custom element to signal the error
                        var errorSignal = document.createElement('div');
                        errorSignal.id = 'jw-player-error-detected';
                        errorSignal.style.display = 'none';
                        document.body.appendChild(errorSignal);
                        
                        return true;
                    }
                    
                    return false;
                }, true);
                
                // Also check for error elements in the DOM
                setInterval(function() {
                    // Look for error messages in the DOM
                    var errorTexts = ['Error 102630', 'JW Player Error', 'jwplayer.js:'];
                    var foundError = false;
                    
                    for (var i = 0; i < errorTexts.length; i++) {
                        if (document.body.innerHTML.includes(errorTexts[i])) {
                            console.log("Found JW Player error text in DOM:", errorTexts[i]);
                            foundError = true;
                            break;
                        }
                    }
                    
                    if (foundError || window.jwPlayerErrorDetected) {
                        console.log("JW Player error confirmed, signaling to Python...");
                        
                        // Signal to Python that we need to redirect
                        var jwErrorSignal = document.getElementById('jw-player-error-detected');
                        if (!jwErrorSignal) {
                            jwErrorSignal = document.createElement('div');
                            jwErrorSignal.id = 'jw-player-error-detected';
                            jwErrorSignal.style.display = 'none';
                            document.body.appendChild(jwErrorSignal);
                        }
                        
                        // Set a custom attribute that we can check from Python
                        jwErrorSignal.setAttribute('data-error-detected', 'true');
                        
                        return true;
                    }
                    
                    return false;
                }, 1000);
                
                return "Error listener installed";
            })();
            """
            
            # Inject the script
            self.browser.page().runJavaScript(js_code)
            
            # Set up a timer to check for the error signal
            if hasattr(self, 'error_check_timer'):
                self.error_check_timer.stop()
                self.error_check_timer.start(1500)  # Check every 1.5 seconds
            
        except Exception as e:
            print(f"Error injecting error listener: {str(e)}")
    
    def check_for_jw_player_error(self):
        """Check if a JW Player error has been detected."""
        try:
            # JavaScript to check if the error signal element exists
            js_code = """
            (function() {
                var errorSignal = document.getElementById('jw-player-error-detected');
                if (errorSignal && errorSignal.getAttribute('data-error-detected') === 'true') {
                    return true;
                }
                return false;
            })();
            """
            
            # Run the JavaScript and handle the result
            self.browser.page().runJavaScript(js_code, self.handle_jw_player_error_check)
            
        except Exception as e:
            print(f"Error checking for JW Player error: {str(e)}")
    
    def handle_jw_player_error_check(self, result):
        """Handle the result of checking for a JW Player error."""
        try:
            if result:
                print("JW Player error confirmed via DOM check")
                
                # Get the current URL
                current_url = self.browser.url().toString()
                
                # Stop the error check timer
                if hasattr(self, 'error_check_timer'):
                    self.error_check_timer.stop()
                
                # Show a message
                self.statusBar.showMessage("JW Player error detected. Opening in Chrome for better compatibility...", 5000)
                
                # Open the URL in Chrome
                self.open_in_chrome(current_url)
                
        except Exception as e:
            print(f"Error handling JW Player error check: {str(e)}")
    
    def handle_console_message(self, level, message, line, source):
        """Handle JavaScript console messages to detect JW Player errors."""
        try:
            # Print console messages for debugging
            print(f"Console [{level}]: {message} (Line {line}, Source: {source})")
            
            # Get the current URL
            current_url = self.browser.url().toString()
            
            # Only proceed if it's a known video site
            if self.is_video_website(current_url):
                # Check for JW Player errors but ignore YouTube
                if ('jwplayer' in message.lower() or 
                    'jw player' in message.lower() or 
                    'error 102630' in message.lower() or
                    'player error' in message.lower()):
                    
                    # Don't redirect YouTube
                    if 'youtube.com' in current_url.lower():
                        return
                        
                    print(f"JW Player error detected in console: {message}")
                    
                    # Show a message
                    self.statusBar.showMessage("Video website detected. Opening in Chrome...", 5000)
                    
                    # Open the URL in Chrome
                    self.open_in_chrome(current_url)
                
        except Exception as e:
            print(f"Error handling console message: {str(e)}")
    
    def toggle_browser_mode(self):
        """This method is kept for compatibility but doesn't do anything now."""
        # Show a message that we're always using the built-in browser
        QMessageBox.information(
            self,
            "Browser Mode",
            "This application now uses the built-in browser for all URLs.\n\n"
            "This provides the best compatibility with all features."
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the coin timer when closing the app
        if hasattr(self, 'coin_manager'):
            self.coin_manager.stop_timer()
        
        # Stop any running timers
        if hasattr(self, 'video_check_timer'):
            self.video_check_timer.stop()
        if hasattr(self, 'error_check_timer'):
            self.error_check_timer.stop()
        
        event.accept()
    
    def is_video_website(self, url):
        """Check if the URL is a video website that needs external browser."""
        video_sites = [
            'netflix.com',
            'primevideo.com',
            'hotstar.com',
            'hulu.com',
            'vimeo.com',
            'dailymotion.com',
            'twitch.tv',
            'voot.com',
            'sonyliv.com',
            'zee5.com',
            'mxplayer.in',
            # Anime streaming sites
            'hianime.to',
            'aniwatch.to',
            '9anime.to',
            '9anime.pl',
            '9anime.id',
            'zoro.to',
            'gogoanime.gr',
            'animesuge.to',
            'animepahe.com',
            'animixplay.to',
            'huggingface.co',
        ]
        # Exclude youtube.com from the list of sites that open in external browser
        return any(site in url.lower() for site in video_sites)

        # Add bookmark button to toolbar
        self.bookmark_button = QAction(QIcon('icons/bookmark.png'), 'Bookmarks', self)
        self.bookmark_button.setStatusTip('Open Bookmarks')
        self.bookmark_button.triggered.connect(self.show_bookmarks)
        self.toolbar.addAction(self.bookmark_button)

        # Add bookmark current page button
        self.add_bookmark_button = QAction(QIcon('icons/add_bookmark.png'), 'Add Bookmark', self)
        self.add_bookmark_button.setStatusTip('Bookmark Current Page')
        self.add_bookmark_button.triggered.connect(self.add_current_bookmark)
        self.toolbar.addAction(self.add_bookmark_button)

    def show_bookmarks(self):
        """Open the bookmarks dialog"""
        dialog = BookmarkDialog(self)
        dialog.exec_()

    def add_current_bookmark(self):
        """Add current page to bookmarks"""
        current_url = self.browser.url().toString()
        current_title = self.browser.page().title()
        
        if current_url and current_title:
            self.db_manager.add_bookmark(current_url, current_title)
            self.statusBar.showMessage(f"Bookmark added: {current_title}", 3000)

        # Initialize tab widget
        self.tabs = BrowserTabWidget(self)
        self.setCentralWidget(self.tabs)
        
        # Initialize download manager
        self.downloads = []
        self.download_widgets = []
        
        # Connect download signal
        self.browser.page().profile().downloadRequested.connect(self.handle_download)
    
        def handle_download(self, download_item):
            widget = DownloadWidget(download_item)
            self.download_widgets.append(widget)
            self.downloads.append(download_item)
            
            # Show download progress
            download_dialog = QDialog(self)
            download_dialog.setLayout(QVBoxLayout())
            download_dialog.layout().addWidget(widget)
            download_dialog.show()
