class MockMotorDriver:

    def forward(self):
        print("[SIM] Moving Forward")

    def backward(self):
        print("[SIM] Moving Backward")

    def turn_left(self):
        print("[SIM] Turning Left")

    def turn_right(self):
        print("[SIM] Turning Right")

    def stop(self):
        print("[SIM] Stopping Motors")

    # Optional compatibility aliases
    def move_forward(self):
        self.forward()

    def move_backward(self):
        self.backward()

    def move_left(self):
        self.turn_left()

    def move_right(self):
        self.turn_right()

    def stop_all(self):
        self.stop()

    def move(self, direction):
        print(f"[SIM] Moving {direction}")