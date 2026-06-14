import time
from typing import Dict, Any

def create_message(
    agent_name: str,
    message_type: str,
    data: Dict[str, Any],
    status: str = "success"
) -> Dict:
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agent": agent_name,
        "type": message_type,
        "data": data,
        "status": status
    }

def print_message(message: Dict):
    """Print a formatted agent message"""
    print(
        f"[{message['timestamp']}] "
        f"{message['agent']} | "
        f"{message['type']} | "
        f"{message['status']}"
    )
    print(f"Data: {message['data']}")
