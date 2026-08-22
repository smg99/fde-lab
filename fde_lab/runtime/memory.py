from typing import List, Dict, Any

class Memory:
    """Basic state management for the agent."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        
    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the memory."""
        message = {"role": role, "content": content}
        message.update(kwargs)
        self.history.append(message)
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve the full conversation history."""
        return self.history
        
    def clear(self):
        """Clear the memory."""
        self.history = []
