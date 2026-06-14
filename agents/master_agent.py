import time

from agents.speech_agent import SpeechAgent
from agents.vision_agent import VisionAgent
from agents.learning_agent import LearningAgent
from agents.motor_control_agent import MotorControlAgent
from agents.navigation_agent import NavigationAgent

from planner.task_planner import TaskPlanner
from planner.ik_solver import IKSolver

from perception.depth_estimator import DepthEstimator

try:
    from hardware.servo_controller import ServoController
    HARDWARE_MODE = True
    print("[SYSTEM] Hardware mode enabled")

except Exception as e:
    print(f"[WARNING] Hardware not available: {e}")

    from simulation.mock_servo import MockServoController as ServoController
    HARDWARE_MODE = False

    print("[SYSTEM] Simulation mode enabled")
if HARDWARE_MODE:

    from hardware.motor_driver import MotorDriver

    print("[SYSTEM] Real MotorDriver loaded")

else:

    from simulation.mock_motor import MockMotorDriver as MotorDriver

    print("[SYSTEM] Simulation MotorDriver loaded")

class MasterAgent:

    def __init__(self):

        self.speech = SpeechAgent()
        self.vision = VisionAgent()
        self.context = LearningAgent()
        self.safety = MotorControlAgent()
        self.planner = TaskPlanner()
        self.ik = IKSolver()
        self.depth = DepthEstimator()

        self.motor = MotorDriver()
        self.servo = ServoController()

        self.navigation = NavigationAgent(
            vision=self.vision,
            ultrasonic=None,
            servo=self.servo,
            motor=self.motor
        )

    # =========================================================
    # RUN LOOP
    # =========================================================
    def run(self):

        print(" AI Robotic Arm System Initialized...\n")

        while True:

            result = self.process_cycle()

            print("\n========== RESULT ==========")
            print(result)
            print("============================\n")
            time.sleep(1)

    # =========================================================
    # SEARCH OBJECT
    # =========================================================
    def search_object(self, target_label):

        print(" Searching using camera...")

        for angle in [60, 90, 120, 150, 30]:

            self.servo.move_camera(angle)

            time.sleep(1)

            vision_out = self.vision.get_detections()

            if vision_out["status"] != "no_object":

                for d in vision_out["detections"]:

                    if target_label in d["label"]:

                        print(f" Found {target_label}")

                        return d

        print(" Object not found after search")

        return None

    # =========================================================
    # DEPTH ESTIMATION
    # =========================================================
    def estimate_depth(self, obj):

        frame = self.vision.get_frame()

        if frame is None:
            return 20

        bbox = obj.get("bbox")

        if not bbox:
            return 20

        depth = self.depth.estimate(frame, bbox)

        print(f" Estimated Depth: {depth}")

        return depth

    # =========================================================
    # VERIFY GRASP
    # =========================================================
    def verify_grasp(self, obj):

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":

            print(" Object disappeared → grasp success")

            return True

        labels = [d["label"] for d in vision_out["detections"]]

        if obj["label"] in labels:

            print(" Object still visible → grasp failed")

            return False

        print(" Object grasped")

        return True

    # =========================================================
    # RETRY GRASP
    # =========================================================
    def retry_grasp(self, obj):

        print(" Attempting grasp...")

        self.servo.control_gripper("close")

        time.sleep(1)

        if self.verify_grasp(obj):

            return True

        print(" Retry grasping...")

        for attempt in range(2):

            print(f" Retry Attempt {attempt + 1}")

            self.servo.move(2, 60 + attempt * 5)

            time.sleep(0.5)

            self.servo.control_gripper("open")

            time.sleep(0.5)

            self.servo.control_gripper("close")

            time.sleep(1)

            if self.verify_grasp(obj):

                print(" Grasp successful")

                return True

        print(" Failed to grasp object")

        return False

    # =========================================================
    # MAIN PROCESS CYCLE
    # =========================================================
    def process_cycle(self, input_command=None):

        logs = []

        # =====================================================
        # INPUT
        # =====================================================
        if input_command is None:

            print("\n Speech Agent → Listening...")

            speech_out = self.speech.get_command()

            if speech_out["status"] == "no_input":

                return {
                    "status": "failed",
                    "command": {},
                    "logs": [" No voice input"],
                    "state": self.context.state,
                    "holding": self.context.holding

                }

            if speech_out["status"] != "ok":

                return {
                    "status": "failed",
                    "command": {},
                    "logs": [" Speech error"],
                    "state": self.context.state,
                    "holding": self.context.holding
                }

            command = speech_out["command"]

        else:

            if isinstance(input_command, dict):

                command = input_command

            else:

                parts = input_command.lower().split()

                # remove wake word properly
                if parts and parts[0] in ["robo", "robot"]:
                    parts = parts[1:]

                action = parts[0] if len(parts) > 0 else "pick"
                # MOVE COMMANDS
                if action == "move":

                    direction = parts[1] if len(parts) > 1 else "forward"

                    command = {
                        "action": "move",
                        "direction": direction,
                        "confidence": 1.0
                    }

                # PICK / DROP COMMANDS
                else:

                    obj = parts[-1] if len(parts) > 1 else None

                    command = {
                        "action": action,
                        "object": obj,
                        "confidence": 1.0
                    }
        logs.append(f" Action: {command['action']}")

        if command.get("object"):

            logs.append(f" Object: {command['object']}")

        self.context.update_memory(
            "last_command",
            command
        )

        # =====================================================
        # DROP
        # =====================================================
        if command["action"] == "drop":

            logs.append(" Opening gripper")

            self.servo.control_gripper("open")

            self.context.holding = False

            self.context.state = "idle"

            logs.append(" Object dropped")

            return {
                "status": "completed",
                "command": {},
                "logs": logs,
                "state": self.context.state,
                "holding": self.context.holding
            }

        # =====================================================
        # MOVE
        # =====================================================
        if command["action"] == "move":

            direction = command.get("direction", "forward")

            logs.append(f" Moving robot → {direction}")

            # call motor driver properly
            self.motor.move(direction)

            return {
                "status": "completed",
                "command": command,
                "state": self.context.state,
                "holding": self.context.holding,
                "logs": logs
            }
        # =====================================================
        # VISION
        # =====================================================
        logs.append(" Vision scanning started")

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":

            logs.append(" No object detected")

            return {
                "status": "failed",
                "command": command,
                "logs": logs,
                "state": self.context.state,
                "holding": self.context.holding
            }

        detections = vision_out["detections"]

        target_object = command.get("object")

        if command.get("action") == "move":
            return {
                "status": "completed",
                "command": command,
                "state": self.context.state,
                "holding": self.context.holding,
                "logs": [" Movement executed"]
            }
        obj = self.vision.track_object(
            detections,
            target_object
        )

        if obj is None:

            logs.append(" Searching target object")

            obj = self.search_object(target_object)

        if obj is None:

            logs.append(" Target object not found")

            return {
                "status": "failed",
                "command": command,
                "logs": logs,
                "state": self.context.state,
                "holding": self.context.holding
            }

        logs.append(f" Detected: {obj['label']}")

        cx, cy = obj["center"]

        logs.append(f" Center: {obj['center']}")

        # =====================================================
        # NAVIGATION
        # =====================================================
        logs.append(" Navigation started")

        nav_result = self.navigation.approach_object(obj)

        if nav_result is False:

            logs.append(" Path blocked")

            return {
                "status": "failed",
                "command": command,
                "logs": logs,
                "state": self.context.state,
                "holding": self.context.holding
            }

        logs.append(" Object reached")

        # =====================================================
        # DEPTH
        # =====================================================
        logs.append(" Estimating depth")

        z = self.estimate_depth(obj)

        x = (cx - 320) * 0.05
        y = (cy - 240) * 0.05

        logs.append(f" 3D Position: {(x, y, z)}")

        # =====================================================
        # IK
        # =====================================================
        logs.append(" Solving IK")

        angles = self.ik.solve(x, y, z)

        print("IK OUTPUT:", angles)

        if not angles:

            logs.append(" IK failed → fallback")

            angles = {}

        # Always ensure required servos exist
        default_angles = {
            "servo1": 90,
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90
        }

        for key, value in default_angles.items():

            if key not in angles:
                angles[key] = value

        # =====================================================
        # STEPS
        # =====================================================
        steps = [

            {"gripper": "open"},

            {"servo_id": 1, "angle": angles["servo1"]},
            {"servo_id": 2, "angle": angles["servo2"]},
            {"servo_id": 3, "angle": angles["servo3"]},
            {"servo_id": 4, "angle": angles["servo4"]},
            {"servo_id": 5, "angle": angles["servo5"]},

            {"gripper_action": "grasp"}
        ]

        # =====================================================
        # SAFETY
        # =====================================================
        logs.append(" Safety validation")

        safety = self.safety.validate(steps)

        if not safety["safe"]:

            logs.append(f" Unsafe: {safety['reason']}")

            return {
                "status": "failed",
                "command": command,
                "logs": logs,
                "state": self.context.state,
                "holding": self.context.holding

            }

        logs.append(" Plan approved")

        # =====================================================
        # EXECUTION
        # =====================================================
        execution_logs = []

        logs.append(" Executing motion")

        for step in steps:

            if "servo_id" in step:

                servo_id = step["servo_id"]

                angle = step["angle"]

                self.servo.move(servo_id, angle)

                execution_logs.append(
                    f" Servo {servo_id} → {angle}°"
                )

            elif "gripper" in step:

                self.servo.control_gripper(step["gripper"])

                execution_logs.append(
                    f" Gripper → {step['gripper']}"
                )

            elif "gripper_action" in step:

                success = self.retry_grasp(obj)

                if success:

                    execution_logs.append(
                        " Object grasped"
                    )

                    self.context.holding = True

                    self.context.state = "holding"

                else:

                    execution_logs.append(
                        " Grasp failed"
                    )

                    return {
                        "status": "failed",
                        "command": command,
                        "logs": logs,
                        "execution": execution_logs,
                        "state": self.context.state,
                        "holding": self.context.holding

                    }

            time.sleep(0.5)

        # =====================================================
        # FINAL
        # =====================================================
        logs.append(" Task completed successfully")

        self.context.update_after_action(
            command["action"],
            success=True
        )

        # =====================================================
        # RETURN DASHBOARD DATA
        # =====================================================
        return {

            "status": "completed",

            "command": command,

            "vision": {
                "object": obj["label"],
                "center": obj["center"],
                "confidence": obj["confidence"]
            },

            "navigation": {
                "status": "completed"
            },

            "planner": {
                "steps": steps
            },

            "execution": {
                "steps": execution_logs
            },

            "logs": logs,

            "state": self.context.state,

            "holding": self.context.holding
        }