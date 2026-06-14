import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
MODELS_DIR = DATA_DIR / "models"

# Create folders if they don't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Load API keys from environment
load_dotenv(BASE_DIR / "config" / "api_keys.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# AGENT SETTINGS


# 👂 Speech Agent
SPEECH_CONFIG = {
    "timeout": 5,                    # Seconds to wait for speech
    "confidence_threshold": 0.7,     # Minimum confidence to accept command
    "use_gemini": True,              # Use AI for understanding
}

# 👁️ Vision Agent
VISION_CONFIG = {
    "model_name": "yolov8n.pt",      # YOLO model (n=nano, s=small, m=medium)
    "camera_index": 0,               # 0 = default webcam
    "confidence_threshold": 0.5,     # Minimum detection confidence
    "resolution": (640, 480),        # Camera resolution
}

# 🦾 Motor Agent
MOTOR_CONFIG = {
    "simulation_mode": True,         # True = simulate, False = real hardware
    "serial_port": "/dev/ttyUSB0",   # Arduino/RPi port (for hardware)
    "baud_rate": 9600,
    "max_reach": 0.5,                # Maximum reach in meters
    "gripper_range": (0, 90),        # Servo angle range
}

# 🧠 Learning Agent
LEARNING_CONFIG = {
    "enable_logging": True,
    "log_file": LOGS_DIR / "system.log",
    "save_frequency": 10,            # Save after every 10 actions
}

# 🧭 Master Agent
MASTER_CONFIG = {
    "retry_attempts": 3,             # Retry failed actions
    "timeout": 30,                   # Maximum time per task (seconds)
}

# GRASPABLE OBJECTS

GRASPABLE_OBJECTS = {
    "bottle", "cup", "wine glass", "bowl",
    "banana", "apple", "orange", "sandwich",
    "cell phone", "book", "remote", "mouse",
    "keyboard", "scissors", "teddy bear"
}