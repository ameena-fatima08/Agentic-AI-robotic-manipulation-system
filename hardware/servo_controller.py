import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio


class ServoController:

    def __init__(self, frequency=50):

        # 🔌 Initialize I2C
        self.i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = frequency

        # 🔥 Servo channel mapping (IMPORTANT)
        self.servo_map = {
            1: 0,  # Base
            2: 1,  # Shoulder
            3: 2,  # Elbow
            4: 4,  # Wrist Pitch
            5: 3,  # Wrist Rotate
            6: 5,  # Gripper
            7: 9   # Camera Servo
        }

        # 🔥 Calibration offsets (tune later)
        self.offsets = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }

        # 🔥 Servo limits (VERY IMPORTANT)
        self.limits = {
            1: (0, 180),
            2: (15, 165),
            3: (0, 180),
            4: (0, 180),
            5: (0, 180),
            6: (30, 90),   # Gripper (adjust physically)
            7: (0, 180)
        }

    # -----------------------------------
    # 🔧 CORE: Angle → PWM conversion
    # -----------------------------------
    def angle_to_pwm(self, angle):
        pulse_min = 150   # adjust if needed
        pulse_max = 600

        pwm = int(pulse_min + (angle / 180.0) * (pulse_max - pulse_min))
        return pwm

    # -----------------------------------
    # 🔥 MOVE SERVO
    # -----------------------------------
    def move(self, servo_id, angle):

        if servo_id not in self.servo_map:
            print(f" Invalid servo ID: {servo_id}")
            return

        # Apply offset
        angle += self.offsets.get(servo_id, 0)

        # Clamp angle
        min_a, max_a = self.limits.get(servo_id, (0, 180))
        angle = max(min_a, min(max_a, angle))

        channel = self.servo_map[servo_id]
        pwm = self.angle_to_pwm(angle)

        self.pca.channels[channel].duty_cycle = pwm

        print(f"[HW] Servo {servo_id} → {angle}°")

    # -----------------------------------
    # 🔥 SMOOTH MOVEMENT (IMPORTANT)
    # -----------------------------------
    def move_smooth(self, servo_id, target_angle, step=2, delay=0.02):

        current = 90  # assume mid start (can improve)

        if target_angle > current:
            angles = range(current, target_angle, step)
        else:
            angles = range(current, target_angle, -step)

        for a in angles:
            self.move(servo_id, a)
            time.sleep(delay)

        self.move(servo_id, target_angle)

    # -----------------------------------
    # 🔥 GRIPPER CONTROL
    # -----------------------------------
    def control_gripper(self, action):

        if action == "open":
            angle = self.limits[6][0]  # open
        elif action == "close":
            angle = self.limits[6][1]  # close
        else:
            print(" Invalid gripper action")
            return

        self.move(6, angle)
        print(f"[HW] Gripper → {action}")

    # -----------------------------------
    # 🎥 CAMERA SERVO
    # -----------------------------------
    def move_camera(self, angle):
        self.move(7, angle)

    # -----------------------------------
    # 🧘 HOME POSITION
    # -----------------------------------
    def go_home(self):

        print("[HW] Moving to home position")

        self.move(1, 90)
        self.move(2, 90)
        self.move(3, 90)
        self.move(4, 90)
        self.move(5, 90)
        self.control_gripper("open")
        self.move(7, 90)

    # -----------------------------------
    # 🛑 STOP ALL (optional)
    # -----------------------------------
    def stop_all(self):
        for i in range(16):
            self.pca.channels[i].duty_cycle = 0