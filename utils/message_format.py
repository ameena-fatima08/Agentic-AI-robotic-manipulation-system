import time
from typing import Dict, Any

def create_message(
    agent_name: str,
    message_type: str,
    data: Dict[str, Any],
    status: str = "success"
) -> Dict:
    """
    Create standardized message
    
    Args:
        agent_name: Name of sending agent
        message_type: Type of message (intent, detection, action, etc.)
        data: Message payload
        status: success/error/warning
    
    Returns:
        Standardized message dict
    """
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agent": agent_name,
        "type": message_type,
        "data": data,
        "status": status
    }

# Example usage:
# msg = create_message("speech_agent", "intent", {"action": "pick", "object": "bottle"})