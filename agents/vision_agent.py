import cv2
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import VISION_CONFIG, GRASPABLE_OBJECTS
from utils.message_format import create_message

class VisionAgent:
    """
    Detects objects using YOLO and estimates their positions
    """
    
    def __init__(self):
        print("👁️ Initializing Vision Agent...")
        
        # Load YOLO model
        self.model = YOLO(VISION_CONFIG["model_name"])
        self.class_names = self.model.names
        
        # Camera setup
        self.camera_index = VISION_CONFIG["camera_index"]
        self.cap = None
        self.frame_width = 0
        self.frame_height = 0
        
        # Graspable objects
        self.graspable_objects = GRASPABLE_OBJECTS
        
        print("✅ Vision Agent ready!")
    
    def start_camera(self) -> bool:
        """Initialize camera"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("❌ Failed to open camera")
            return False
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Camera started: {self.frame_width}x{self.frame_height}")
        return True
    
    def stop_camera(self):
        """Release camera"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            print("📷 Camera stopped")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture single frame"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect all objects in frame
        Returns: List of detected objects
        """
        results = self.model(
            frame, 
            conf=VISION_CONFIG["confidence_threshold"],
            verbose=False
        )
        
        detections = []
        
        for result in results:
            for box in result.boxes:
                # Extract detection info
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = int(box.cls[0])
                class_name = self.class_names[class_id]
                confidence = float(box.conf[0])
                
                # Calculate center and size
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                width = x2 - x1
                height = y2 - y1
                
                detection = {
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x1": x1, "y1": y1,
                        "x2": x2, "y2": y2,
                        "center_x": center_x,
                        "center_y": center_y,
                        "width": width,
                        "height": height
                    },
                    "is_graspable": class_name in self.graspable_objects
                }
                
                detections.append(detection)
        
        return detections
    
    def estimate_position(self, detection: Dict) -> Dict:
        """
        Estimate object position (left/center/right, near/far)
        """
        cx = detection["bbox"]["center_x"]
        cy = detection["bbox"]["center_y"]
        area = detection["bbox"]["width"] * detection["bbox"]["height"]
        
        # Horizontal position
        if cx < self.frame_width * 0.33:
            horizontal = "left"
        elif cx < self.frame_width * 0.66:
            horizontal = "center"
        else:
            horizontal = "right"
        
        # Vertical position
        if cy < self.frame_height * 0.33:
            vertical = "top"
        elif cy < self.frame_height * 0.66:
            vertical = "middle"
        else:
            vertical = "bottom"
        
        # Depth estimation (based on size)
        frame_area = self.frame_width * self.frame_height
        area_ratio = area / frame_area
        
        if area_ratio > 0.15:
            depth = "very_close"
        elif area_ratio > 0.08:
            depth = "close"
        elif area_ratio > 0.03:
            depth = "medium"
        else:
            depth = "far"
        
        return {
            "horizontal": horizontal,
            "vertical": vertical,
            "depth": depth,
            "coordinates": {
                "x": cx,
                "y": cy
            }
        }
    
    def find_object(self, target_object: str) -> Dict:
        """
        Find specific object in scene
        Returns: Message with object info or not_found
        """
        frame = self.capture_frame()
        if frame is None:
            return create_message(
                "vision_agent",
                "detection",
                {"error": "Camera not available"},
                "error"
            )
        
        detections = self.detect_objects(frame)
        
        # Filter for target object
        for det in detections:
            if target_object.lower() in det["class_name"].lower() and det["is_graspable"]:
                position = self.estimate_position(det)
                
                return create_message(
                    "vision_agent",
                    "detection",
                    {
                        "found": True,
                        "object": det,
                        "position": position
                    },
                    "success"
                )
        
        # Not found
        return create_message(
            "vision_agent",
            "detection",
            {
                "found": False,
                "target": target_object,
                "total_objects": len(detections)
            },
            "error"
        )
    
    def scan_scene(self) -> Dict:
        """
        Scan scene and return all graspable objects
        """
        frame = self.capture_frame()
        if frame is None:
            return create_message(
                "vision_agent",
                "scan",
                {"error": "Camera not available"},
                "error"
            )
        
        detections = self.detect_objects(frame)
        graspable = [d for d in detections if d["is_graspable"]]
        
        return create_message(
            "vision_agent",
            "scan",
            {
                "total_objects": len(detections),
                "graspable_count": len(graspable),
                "graspable_objects": graspable
            },
            "success"
        )


# Test the agent
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING VISION AGENT")
    print("="*60)
    
    agent = VisionAgent()
    
    if not agent.start_camera():
        print("❌ Cannot start camera")
        exit(1)
    
    print("\nCommands:")
    print("  's' - Scan scene")
    print("  'f' - Find object")
    print("  'q' - Quit")
    print("="*60)
    
    try:
        while True:
            frame = agent.capture_frame()
            if frame is not None:
                cv2.imshow("Vision Agent", frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                result = agent.scan_scene()
                print(f"\n📊 Scan Result:")
                print(f"   Total objects: {result['data']['total_objects']}")
                print(f"   Graspable: {result['data']['graspable_count']}")
                input("Press ENTER to continue...")
            elif key == ord('f'):
                target = input("\nEnter object to find: ")
                result = agent.find_object(target)
                if result['data'].get('found'):
                    print(f"✅ Found {target}!")
                    print(f"   Position: {result['data']['position']}")
                else:
                    print(f"❌ {target} not found")
                input("Press ENTER to continue...")
    
    finally:
        agent.stop_camera()


from flask import Flask, jsonify
from vision_agent import VisionAgent

app = Flask(__name__)
vision_agent = VisionAgent()

@app.route('/vision/latest', methods=['GET'])
def get_latest_vision():
    frame_data = vision_agent.capture_frame()
    detections = vision_agent.detect_objects(frame_data)
    response = {
        "timestamp": vision_agent.timestamp(),
        "frame_b64": frame_data["frame_b64"],
        "detections": detections,
        "status": "ok"
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
