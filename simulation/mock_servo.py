class MockServoController:

    def move(self, servo_id, angle):
        print(f"[SIM] Moving Servo {servo_id} → {angle}°")

    def control_gripper(self, action):
        print(f"[SIM] Gripper → {action}")

    def move_camera(self, angle):
        print(f"[SIM] Moving Camera Servo → {angle}°")

    def stop_all(self):
        print("[SIM] Stopping all servos")