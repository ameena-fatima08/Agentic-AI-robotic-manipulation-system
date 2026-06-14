class MockMotorDriver:

    def move_forward(self):
        print("[SIM] Moving Forward")

    def move_backward(self):
        print("[SIM] Moving Backward")

    def move_left(self):
        print("[SIM] Turning Left")

    def move_right(self):
        print("[SIM] Turning Right")

    def stop_all(self):
        print("[SIM] Stopping Motors")