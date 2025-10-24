"""
Chat History Manager for Zypher AI Logo Generator
Handles storing and retrieving chat history
"""
import json
import os
from datetime import datetime
import config


class ChatHistoryManager:
    """Manages chat history persistence and retrieval"""
    
    def __init__(self):
        self.history_file = config.HISTORY_FILE
        self.max_items = config.MAX_HISTORY_ITEMS
        self.history = []
        self._ensure_history_file()
        self.load_history()
    
    def _ensure_history_file(self):
        """Create history file and directory if they don't exist"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def load_history(self):
        """Load chat history from file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
                # Limit history size
                if len(self.history) > self.max_items:
                    self.history = self.history[-self.max_items:]
                    self.save_history()
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
    
    def save_history(self):
        """Save chat history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_entry(self, prompt, image_path, use_lora=False):
        """
        Add a new entry to chat history
        
        Args:
            prompt (str): The prompt used to generate the image
            image_path (str): Path to the generated image
            use_lora (bool): Whether LoRA was used
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "image_path": image_path,
            "model_type": "LoRA" if use_lora else "Base Model",
            "use_lora": use_lora
        }
        
        self.history.append(entry)
        
        # Maintain max history size
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items:]
        
        self.save_history()
    
    def get_history(self):
        """Get all chat history"""
        return self.history
    
    def get_recent_history(self, n=10):
        """Get n most recent history entries"""
        return self.history[-n:] if len(self.history) >= n else self.history
    
    def clear_history(self):
        """Clear all chat history"""
        self.history = []
        self.save_history()
        return "Chat history cleared"
    
    def format_for_display(self):
        """
        Format history for display in Gradio chat interface
        
        Returns:
            list: List of tuples (user_message, assistant_response) for Gradio
        """
        formatted = []
        for entry in self.history:
            user_msg = f"{entry['prompt']} ({entry['model_type']})"
            # For Gradio chatbot, we'll show timestamp and model info
            assistant_msg = f"Generated at {entry['timestamp'][:19]}"
            formatted.append([user_msg, assistant_msg])
        return formatted
    
    def export_history(self, export_path=None):
        """Export history to a JSON file"""
        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(
                config.CHAT_LOGS_DIR, 
                f"history_export_{timestamp}.json"
            )
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return f"History exported to {export_path}"
        except Exception as e:
            return f"Error exporting history: {e}"
