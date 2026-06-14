def normalize(text):
    return text.lower().replace(" ", "").strip()


class NavigationAgent:

    def __init__(self, vision, ultrasonic, servo, motor):
        self.vision = vision
        self.motor = motor
        self.servo = servo

    def approach_object(self, obj):

        print(" Approaching using wheels...")

        for _ in range(10):

            vision_out = self.vision.get_detections()

            if vision_out["status"] == "no_object":
                self.motor.stop()
                return False

            target = None
            for d in vision_out["detections"]:
                if obj["label"] in d["label"]:
                    target = d
                    break

            if not target:
                self.motor.stop()
                return False

            cx, cy = target["center"]
            offset_x = cx - 320

            # 🔥 TURN USING WHEELS
            if offset_x > 50:
                self.motor.turn_right()
            elif offset_x < -50:
                self.motor.turn_left()
            else:
                self.motor.move_forward()

            # 🔥 STOP WHEN CLOSE
            if abs(offset_x) < 20:
                self.motor.stop()
                print(" Reached near object")
                return True

        self.motor.stop()
        return True
    
    def move_back(self):
        print("[HW] Moving backward")

        if self.move == "simulation":
            print("[SIM] Moving backward")
            return

        # 🔥 Real hardware (L293D logic)
        self.motor.backward()
        time.sleep(1)
        self.motor.stop()