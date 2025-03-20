import json
import os
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineScript
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiHelper(QObject):
    """Helper class for integrating Google Gemini 1.5 Flash API."""
    
    # Signal emitted when AI has processed content
    result_ready = pyqtSignal(str, str)  # action, result
    
    def __init__(self):
        super().__init__()
        # Load environment variables from .env file
        load_dotenv(override=True)  # Force reload of .env file
        
        # Get API key from environment variable
        self.api_key = os.getenv("GEMINI_API_KEY")  # Using getenv instead of get
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in .env file")
        else:
            print("API key loaded successfully from .env file")
            
        self.content_script = self._create_content_script()
        self.processing_timer = None
        self.current_action = None
        
        # Configure Gemini API if key is available
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def _create_content_script(self):
        """Create a JavaScript script to extract content from web pages."""
        script = QWebEngineScript()
        
        # JavaScript code to extract content
        js_code = """
        // Function to get the page content
        function getPageContent() {
            // Get selected text if any
            const selection = window.getSelection().toString().trim();
            
            // If there's a selection, use it
            if (selection) {
                return selection;
            }
            
            // Otherwise, get the main content
            // Try to find the main content area
            const possibleContentElements = [
                document.querySelector('article'),
                document.querySelector('main'),
                document.querySelector('.content'),
                document.querySelector('#content'),
                document.querySelector('.article'),
                document.querySelector('#article')
            ].filter(el => el !== null);
            
            if (possibleContentElements.length > 0) {
                // Use the first found content element
                return possibleContentElements[0].innerText;
            }
            
            // Fallback to body text, but try to exclude navigation, footer, etc.
            const bodyText = document.body.innerText;
            
            // If the text is too long, try to be smarter about what we extract
            if (bodyText.length > 15000) {
                // Get all paragraphs
                const paragraphs = Array.from(document.querySelectorAll('p')).map(p => p.innerText).join('\\n\\n');
                if (paragraphs.length > 1000) {
                    return paragraphs;
                }
                
                // Get all divs with substantial text
                const textDivs = Array.from(document.querySelectorAll('div'))
                    .filter(div => div.innerText.length > 100)
                    .map(div => div.innerText)
                    .join('\\n\\n');
                
                if (textDivs.length > 1000) {
                    return textDivs;
                }
                
                // Fallback to first 15000 chars of body
                return bodyText.substring(0, 15000) + "...";
            }
            
            return bodyText;
        }
        
        // Function to get page metadata
        function getPageMetadata() {
            return {
                title: document.title,
                url: window.location.href,
                language: document.documentElement.lang || navigator.language || 'en'
            };
        }
        
        // Function to be called from Python
        function extractPageContent() {
            const content = getPageContent();
            const metadata = getPageMetadata();
            
            return JSON.stringify({
                content: content,
                metadata: metadata
            });
        }
        
        // Make the function available to the page
        window.extractPageContent = extractPageContent;
        """
        
        script.setSourceCode(js_code)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(True)
        
        return script
    
    def inject_script(self, web_page):
        """Inject the content extraction script into the web page."""
        web_page.scripts().insert(self.content_script)
    
    def set_api_key(self, api_key):
        """Set the Gemini API key."""
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def _validate_api_key(self):
        """Validate that the API key is set and configured."""
        if not self.api_key:
            self.result_ready.emit('error', "API key not found in .env file. Please check your .env file configuration.")
            return False
            
        # Check if the API key is valid (not empty or placeholder)
        if self.api_key.strip() == "" or "your-api-key" in self.api_key.lower():
            self.result_ready.emit('error', "API key appears to be invalid. Please set a valid API key in your .env file.")
            return False
            
        # Reload the API key configuration just to be sure
        genai.configure(api_key=self.api_key)
        return True
    
    def process_with_gemini(self, web_page, action, target_language="English"):
        """Process the current page content with Gemini 1.5 Flash."""
        # Validate API key before processing
        if not self._validate_api_key():
            return
            
        # Store the current action
        self.current_action = action
        
        # Set up a timeout timer
        if self.processing_timer is not None:
            self.processing_timer.stop()
        
        self.processing_timer = QTimer()
        self.processing_timer.setSingleShot(True)
        self.processing_timer.timeout.connect(self._handle_timeout)
        self.processing_timer.start(30000)  # 30 second timeout
        
        # JavaScript to call our injected function
        js_code = """
        (function() {
            try {
                const result = extractPageContent();
                return result;
            } catch (e) {
                return JSON.stringify({
                    error: true,
                    message: "JavaScript error: " + e.message
                });
            }
        })();
        """
        
        # Execute the JavaScript and get the result
        web_page.runJavaScript(js_code, lambda result: self._handle_content(result, action, target_language))
    
    def _handle_content(self, result, action, target_language):
        """Handle the extracted content and send to Gemini."""
        try:
            # Parse the JSON result
            data = json.loads(result)
            
            if data.get('error', False):
                self.result_ready.emit('error', data.get('message', 'Unknown error'))
                return
            
            content = data.get('content', '')
            metadata = data.get('metadata', {})
            
            # Limit content length to avoid token limits
            if len(content) > 10000:
                content = content[:10000] + "..."
            
            # Check if API key is set
            if not self.api_key:
                self.result_ready.emit('error', "Gemini API key is not set. Please set your API key in the settings.")
                return
            
            # Process with Gemini based on action
            if action == 'summarize':
                self._summarize_with_gemini(content, metadata)
            elif action == 'translate':
                self._translate_with_gemini(content, metadata, target_language)
            elif action == 'explain':
                self._explain_with_gemini(content, metadata)
            else:
                self.result_ready.emit('error', f"Unknown action: {action}")
                
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error handling content: {str(e)}\nDetails: {error_details}")
            self.result_ready.emit('error', f"Error processing content: {str(e)}")
    
    def _summarize_with_gemini(self, content, metadata):
        """Summarize content using Gemini 1.5 Flash."""
        try:
            title = metadata.get('title', 'Web Page')
            
            # Prepare the prompt
            prompt = f"""Summarize the following web page content from "{title}":

{content}

Provide a concise summary that captures the main points and key information.
"""
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            if response:
                self.result_ready.emit('summarize', response)
            else:
                self.result_ready.emit('error', "Failed to get a response from Gemini.")
                
        except Exception as e:
            self.result_ready.emit('error', f"Error summarizing with Gemini: {str(e)}")
    
    def _translate_with_gemini(self, content, metadata, target_language):
        """Translate content using Gemini 1.5 Flash."""
        try:
            source_language = metadata.get('language', 'auto')
            
            # Language code mapping
            language_codes = {
                "English": "en",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                "Chinese": "zh",
                "Japanese": "ja",
                "Korean": "ko",
                "Russian": "ru",
                "Arabic": "ar",
                "Hindi": "hi",
                "Portuguese": "pt",
                "Italian": "it",
                "Dutch": "nl",
                "Polish": "pl",
                "Turkish": "tr",
                "Vietnamese": "vi",
                "Thai": "th",
                "Indonesian": "id"
            }
            
            target_code = language_codes.get(target_language, "en")
            
            # Prepare the prompt with specific translation instructions
            prompt = f"""Translate the following content to {target_language} ({target_code}):

{content}

Important translation instructions:
1. Maintain the original formatting and structure
2. Keep proper nouns unchanged unless they have standard translations
3. Preserve any technical terms in their correct form
4. Ensure the translation is natural and fluent in {target_language}
5. If there are idiomatic expressions, translate them to equivalent expressions in {target_language}

Please provide only the translation without any explanations or notes."""
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            if response:
                # Add a header to indicate the translation
                final_response = f"Translation to {target_language}:\n\n{response}"
                self.result_ready.emit('translate', final_response)
            else:
                self.result_ready.emit('error', f"Failed to translate to {target_language}")
                
        except Exception as e:
            self.result_ready.emit('error', f"Error translating with Gemini: {str(e)}")
    
    def _explain_with_gemini(self, content, metadata):
        """Explain content using Gemini 1.5 Flash."""
        try:
            title = metadata.get('title', 'Web Page')
            
            # Prepare the prompt
            prompt = f"""Explain the following web page content from "{title}" in simple terms:

{content}

Provide a clear explanation that would help someone understand this content, including any technical terms or concepts.
"""
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            if response:
                self.result_ready.emit('explain', response)
            else:
                self.result_ready.emit('error', "Failed to get a response from Gemini.")
                
        except Exception as e:
            self.result_ready.emit('error', f"Error explaining with Gemini: {str(e)}")
    
    def _call_gemini_api(self, prompt):
        """Call the Gemini 1.5 Flash API with the given prompt."""
        try:
            # Validate API key before proceeding
            if not self.api_key:
                print("Error: API key is not set")
                return "Error: API key not found. Please check your .env file and ensure GEMINI_API_KEY is set correctly."
                
            # Check if the API key is valid (not empty or placeholder)
            if self.api_key.strip() == "" or "your-api-key" in self.api_key.lower():
                print("Error: API key appears to be invalid")
                return "Error: API key appears to be invalid. Please set a valid API key in your .env file."
                
            # Reload the API key configuration just to be sure
            genai.configure(api_key=self.api_key)
            
            # Create a Gemini model instance
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate content with timeout handling
            try:
                response = model.generate_content(prompt)
                
                # Extract the text from the response
                if response and hasattr(response, 'text'):
                    return response.text
                else:
                    return "No response generated. Please try again."
            except Exception as api_error:
                error_message = str(api_error).lower()
                if "timeout" in error_message or "timed out" in error_message:
                    return "Error: Request to Gemini API timed out. Please try again with shorter content or check your internet connection."
                elif "key" in error_message and ("invalid" in error_message or "unauthorized" in error_message):
                    return "Error: Invalid API key. Please check your API key in the .env file and try again."
                else:
                    raise  # Re-raise for the outer exception handler
                
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error calling Gemini API: {str(e)}\nDetails: {error_details}")
            return f"Error: {str(e)}. Please check your API key in the .env file and try again."
    
    def _handle_timeout(self):
        """Handle timeout when processing takes too long."""
        if self.current_action:
            # Create a message for the timeout
            result = f"The {self.current_action} operation timed out after 30 seconds. This could be due to:\n\n"
            result += "- Network connectivity issues\n"
            result += "- Gemini API being temporarily unavailable\n"
            result += "- The content being too large to process quickly\n\n"
            result += "Please try again with a smaller selection of text or check your internet connection."
            
            # Emit the result
            self.result_ready.emit(self.current_action, result)
            
            # Reset the current action
            self.current_action = None 
    
    def process_question(self, web_page, question, callback):
        """Process a user question by reading the current page or searching the web.
        
        Args:
            web_page: The current web page.
            question: The user's question.
            callback: Callback function to receive the result.
        """
        # Validate API key before processing
        if not self._validate_api_key():
            callback("Error: API key not found or invalid. Please check your .env file and ensure GEMINI_API_KEY is set correctly.")
            return
            
        # Additional validation of API key format
        if self.api_key.strip() == "" or "your-api-key" in self.api_key.lower():
            callback("Error: API key appears to be invalid. Please set a valid API key in your .env file.")
            return
            
        # Set up a timeout timer
        if self.processing_timer is not None:
            self.processing_timer.stop()
        
        self.processing_timer = QTimer()
        self.processing_timer.setSingleShot(True)
        self.processing_timer.timeout.connect(lambda: callback("Error: Processing timed out. Please check your API key in the .env file and try again."))
        self.processing_timer.start(30000)  # 30 second timeout
        
        # JavaScript to call our injected function to get page content
        js_code = """
        (function() {
            try {
                const result = extractPageContent();
                return result;
            } catch (e) {
                return JSON.stringify({
                    error: true,
                    message: "JavaScript error: " + e.message
                });
            }
        })();
        """
        
        # Execute the JavaScript and get the result
        web_page.runJavaScript(js_code, lambda result: self._handle_question(result, question, callback))
    
    def _handle_question(self, result, question, callback):
        """Handle the extracted content and process the user's question.
        
        Args:
            result: The extracted page content.
            question: The user's question.
            callback: Callback function to receive the result.
        """
        try:
            # Parse the JSON result
            data = json.loads(result)
            
            if data.get('error', False):
                callback(f"Error: {data.get('message', 'Unknown error')}")
                return
            
            content = data.get('content', '')
            metadata = data.get('metadata', {})
            
            # Limit content length to avoid token limits
            if len(content) > 10000:
                content = content[:10000] + "..."
            
            # Prepare the prompt
            prompt = f"""I have a question about a webpage I'm viewing. The webpage title is "{metadata.get('title', 'Web Page')}" 
and the URL is {metadata.get('url', 'unknown')}.

Here's the content of the webpage:
{content}

My question is: {question}

Please answer my question based on the webpage content. If the answer is not in the webpage content, 
please indicate that and provide a general answer based on your knowledge. 
Make it clear whether your answer comes from the webpage or from your general knowledge.
"""
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            if response:
                callback(response)
            else:
                callback("Error: Failed to get a response from Gemini.")
                
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error handling question: {str(e)}\nDetails: {error_details}")
            callback(f"Error: {str(e)}")