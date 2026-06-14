import time
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import MOTOR_CONFIG
from utils.message_format import create_message

class MotorAgent:
    """
    Controls robot arm movements (simulated)
    Later: Connect to Arduino/Raspberry Pi for real hardware
    """
    
    def __init__(self):
        print("🦾 Initializing Motor Agent...")
        
        self.simulation_mode = MOTOR_CONFIG["simulation_mode"]
        self.current_position = {"x": 0, "y": 0, "z": 0}
        self.gripper_open = True
        
        if self.simulation_mode:
            print("⚠️ Running in SIMULATION mode")
        else:
            print("🔌 Hardware mode (not implemented yet)")
            # TODO: Initialize serial connection to Arduino
            # self.serial = serial.Serial(MOTOR_CONFIG["serial_port"], MOTOR_CONFIG["baud_rate"])
        
        print("✅ Motor Agent ready!")
    
    def move_to_position(self, target_position: Dict) -> Dict:
        """
        Move robot arm to target position
        
        Args:
            target_position: {x, y, z} or {horizontal, vertical, depth}
        
        Returns:
            Message with movement result
        """
        print(f"\n🦾 Moving to position: {target_position}")
        
        if self.simulation_mode:
            # Simulate movement with delays
            print("   ↔️ Moving horizontally...")
            time.sleep(0.5)
            
            print("   ↕️ Moving vertically...")
            time.sleep(0.5)
            
            print("   ⬆️ Adjusting height...")
            time.sleep(0.5)
            
            print("   ✅ Position reached!")
            
            self.current_position = target_position
            
            return create_message(
                "motor_agent",
                "movement",
                {
                    "action": "move_complete",
                    "position": target_position
                },
                "success"
            )
        else:
            # TODO: Send actual commands to hardware
            # self.serial.write(f"MOVE {x} {y} {z}\n".encode())
            pass
    
    def open_gripper(self) -> Dict:
        """Open gripper to release object"""
        print("\n🖐️ Opening gripper...")
        
        if self.simulation_mode:
            time.sleep(0.3)
            print("   ✅ Gripper opened!")
            self.gripper_open = True
            
            return create_message(
                "motor_agent",
                "gripper",
                {"action": "open", "state": "open"},
                "success"
            )
        else:
            # TODO: Send command to servo
            # self.serial.write("GRIPPER OPEN\n".encode())
            pass
    
    def close_gripper(self) -> Dict:
        """Close gripper to grasp object"""
        print("\n✊ Closing gripper...")
        
        if self.simulation_mode:
            time.sleep(0.3)
            print("   ✅ Gripper closed!")
            self.gripper_open = False
            
            return create_message(
                "motor_agent",
                "gripper",
                {"action": "close", "state": "closed"},
                "success"
            )
        else:
            # TODO: Send command to servo
            # self.serial.write("GRIPPER CLOSE\n".encode())
            pass
    
    def pick_object(self, object_info: Dict) -> Dict:
        """
        Complete pick sequence:
        1. Move to object
        2. Open gripper
        3. Move down
        4. Close gripper
        5. Move up
        """
        print("\n🎯 Starting PICK sequence...")
        
        try:
            # Step 1: Move to object position
            position = object_info.get("position", {})
            self.move_to_position(position)
            
            # Step 2: Open gripper
            self.open_gripper()
            
            # Step 3: Move down to object
            print("\n⬇️ Moving down to object...")
            time.sleep(0.5)
            
            # Step 4: Close gripper (grasp)
            self.close_gripper()
            
            # Step 5: Lift object
            print("\n⬆️ Lifting object...")
            time.sleep(0.5)
            
            print("\n✅ PICK sequence complete!")
            
            return create_message(
                "motor_agent",
                "action",
                {
                    "action": "pick",
                    "status": "success",
                    "object": object_info.get("object", {}).get("class_name")
                },
                "success"
            )
            
        except Exception as e:
            print(f"\n❌ PICK sequence failed: {e}")
            return create_message(
                "motor_agent",
                "action",
                {"action": "pick", "error": str(e)},
                "error"
            )
    
    def place_object(self, target_position: Dict) -> Dict:
        """
        Complete place sequence:
        1. Move to position
        2. Move down
        3. Open gripper
        4. Move up
        """
        print("\n🎯 Starting PLACE sequence...")
        
        try:
            # Step 1: Move to target position
            self.move_to_position(target_position)
            
            # Step 2: Move down
            print("\n⬇️ Moving down...")
            time.sleep(0.5)
            
            # Step 3: Open gripper (release)
            self.open_gripper()
            
            # Step 4: Move up
            print("\n⬆️ Moving up...")
            time.sleep(0.5)
            
            print("\n✅ PLACE sequence complete!")
            
            return create_message(
                "motor_agent",
                "action",
                {"action": "place", "status": "success"},
                "success"
            )
            
        except Exception as e:
            print(f"\n❌ PLACE sequence failed: {e}")
            return create_message(
                "motor_agent",
                "action",
                {"action": "place", "error": str(e)},
                "error"
            )
    
    def stop(self) -> Dict:
        """Emergency stop"""
        print("\n🛑 EMERGENCY STOP!")
        
        return create_message(
            "motor_agent",
            "action",
            {"action": "stop", "status": "stopped"},
            "success"
        )
    
    def get_status(self) -> Dict:
        """Get current robot status"""
        return {
            "position": self.current_position,
            "gripper_state": "open" if self.gripper_open else "closed",
            "mode": "simulation" if self.simulation_mode else "hardware"
        }


# Test the agent
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING MOTOR AGENT")
    print("="*60)
    
    agent = MotorAgent()
    
    # Test pick sequence
    print("\n1️⃣ Testing PICK sequence...")
    test_object = {
        "object": {"class_name": "bottle"},
        "position": {"horizontal": "center", "vertical": "middle", "depth": "close"}
    }
    result = agent.pick_