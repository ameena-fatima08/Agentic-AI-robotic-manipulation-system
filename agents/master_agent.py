import time
from typing import Dict, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import MASTER_CONFIG
from utils.message_format import create_message, print_message

# Import other agents
from agents.speech_agent import SpeechAgent
from agents.vision_agent import VisionAgent
from agents.motor_agent import MotorAgent
from agents.learning_agent import LearningAgent

class MasterAgent:
    """
    Master Agent - Coordinates all sub-agents
    
    Workflow:
    1. Listen to user (Speech Agent)
    2. Understand intent (Speech Agent)
    3. Find object (Vision Agent)
    4. Plan action (Master logic)
    5. Execute action (Motor Agent)
    6. Log result (Learning Agent)
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("🧭 INITIALIZING MASTER AGENT (System Brain)")
        print("="*60 + "\n")
        
        # Initialize all sub-agents
        print("📋 Initializing sub-agents...\n")
        
        try:
            self.speech_agent = SpeechAgent()
            self.vision_agent = VisionAgent()
            self.motor_agent = MotorAgent()
            self.learning_agent = LearningAgent()
            
            print("\n" + "="*60)
            print("✅ MASTER AGENT READY - All systems operational!")
            print("="*60 + "\n")
            
            self.running = False
            
        except Exception as e:
            print(f"\n❌ Failed to initialize Master Agent: {e}")
            raise
    
    def start(self):
        """Start the main control loop"""
        print("\n" + "="*60)
        print("🚀 STARTING ROBOTIC GRASPING SYSTEM")
        print("="*60)
        
        # Start camera
        if not self.vision_agent.start_camera():
            print("❌ Cannot start without camera")
            return
        
        self.running = True
        
        print("\n📋 System Commands:")
        print("   Say: 'Pick [object]' - Pick up an object")
        print("   Say: 'Show objects' - Scan the scene")
        print("   Say: 'Stop' - Emergency stop")
        print("   Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        try:
            while self.running:
                self._process_command()
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
        finally:
            self.stop()
    
    def _process_command(self):
        """Process a single user command"""
        
        # Step 1: Listen to user
        print("\n" + "🎤" + "-"*58)
        print("Waiting for your command...")
        print("-"*60)
        
        speech_result = self.speech_agent.get_command()
        
        if speech_result["status"] != "success":
            print("❌ Could not understand command. Please try again.")
            return
        
        action = speech_result["data"].get("action")
        target_object = speech_result["data"].get("object")
        confidence = speech_result["data"].get("confidence", 0)
        
        print(f"\n✅ Understood: {action} {target_object} (confidence: {confidence:.2f})")
        
        # Handle different actions
        if action == "stop":
            self._handle_stop()
        elif action == "show":
            self._handle_show()
        elif action == "pick":
            self._handle_pick(target_object)
        elif action == "place":
            self._handle_place(target_object)
        else:
            print(f"⚠️ Unknown action: {action}")
    
    def _handle_stop(self):
        """Handle stop command"""
        print("\n🛑 STOPPING SYSTEM...")
        self.motor_agent.stop()
        self.running = False
    
    def _handle_show(self):
        """Handle show/scan command"""
        print("\n👁️ Scanning scene...")
        
        result = self.vision_agent.scan_scene()
        
        if result["status"] == "success":
            data = result["data"]
            print(f"\n📊 Scan Results:")
            print(f"   Total objects detected: {data['total_objects']}")
            print(f"   Graspable objects: {data['graspable_count']}")
            
            if data['graspable_count'] > 0:
                print("\n   Detected objects:")
                for obj in data['graspable_objects']:
                    print(f"      - {obj['class_name']} (confidence: {obj['confidence']:.2f})")
        else:
            print("❌ Failed to scan scene")
    
    def _handle_pick(self, target_object: str):
        """
        Handle pick command
        Complete workflow: Find object → Move → Grasp → Log
        """
        if not target_object:
            print("❌ No object specified")
            return
        
        start_time = time.time()
        
        print(f"\n🎯 Starting PICK workflow for: {target_object}")
        print("-"*60)
        
        # Step 1: Find object with vision
        print("\n1️⃣ Searching for object...")
        vision_result = self.vision_agent.find_object(target_object)
        
        if vision_result["status"] != "success" or not vision_result["data"].get("found"):
            print(f"❌ Could not find {target_object}")
            
            # Log failure
            self.learning_agent.log_action({
                "action": "pick",
                "object": target_object,
                "result": "failure",
                "duration": time.time() - start_time,
                "error": "Object not found"
            })
            return
        
        object_info = vision_result["data"]
        position = object_info.get("position")
        
        print(f"✅ Found {target_object}!")
        print(f"   Position: {position['horizontal']}, {position['vertical']}, {position['depth']}")
        
        # Step 2: Execute pick with motor agent
        print("\n2️⃣ Executing pick sequence...")
        motor_result = self.motor_agent.pick_object(object_info)
        
        duration = time.time() - start_time
        
        if motor_result["status"] == "success":
            print(f"\n✅ Successfully picked {target_object}! (took {duration:.1f}s)")
            
            # Log success
            self.learning_agent.log_action({
                "action": "pick",
                "object": target_object,
                "result": "success",
                "duration": duration
            })
            
        else:
            print(f"\n❌ Failed to pick {target_object}")
            
            # Log failure
            self.learning_agent.log_action({
                "action": "pick",
                "object": target_object,
                "result": "failure",
                "duration": duration,
                "error": motor_result["data"].get("error")
            })
        
        print("-"*60)
    
    def _handle_place(self, target_object: str):
        """Handle place command"""
        print(f"\n🎯 Starting PLACE workflow...")
        
        start_time = time.time()
        
        # Default position (center, front)
        target_position = {
            "horizontal": "center",
            "vertical": "middle",
            "depth": "close"
        }
        
        motor_result = self.motor_agent.place_object(target_position)
        duration = time.time() - start_time
        
        if motor_result["status"] == "success":
            print(f"\n✅ Successfully placed object! (took {duration:.1f}s)")
            
            self.learning_agent.log_action({
                "action": "place",
                "object": target_object or "unknown",
                "result": "success",
                "duration": duration
            })
        else:
            print(f"\n❌ Failed to place object")
            
            self.learning_agent.log_action({
                "action": "place",
                "object": target_object or "unknown",
                "result": "failure",
                "duration": duration
            })
    
    def stop(self):
        """Shutdown system gracefully"""
        print("\n" + "="*60)
        print("🛑 SHUTTING DOWN SYSTEM")
        print("="*60)
        
        # Stop camera
        self.vision_agent.stop_camera()
        
        # Print final statistics
        print("\n📊 Final Performance Statistics:")
        self.learning_agent.print_statistics()
        
        print("\n✅ System shut down successfully")
        print("="*60 + "\n")


# Main entry point
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 AI-POWERED VOICE-CONTROLLED ROBOTIC GRASPING SYSTEM")
    print("="*60)
    
    try:
        master = MasterAgent()
        master.start()
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        traceback.print_exc()

