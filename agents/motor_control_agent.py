import yaml
import math


class MotorControlAgent:

    def __init__(self, config_path="config/servo_limits.yaml"):

        # -----------------------------
        # LOAD LIMITS
        # -----------------------------
        try:
            with open(config_path, "r") as f:
                self.limits = yaml.safe_load(f)

        except Exception as e:
            print(f"[SAFETY] Failed to load servo limits: {e}")

            self.limits = {
                "servo1": {"min": 0, "max": 180},
                "servo2": {"min": 0, "max": 180},
                "servo3": {"min": 0, "max": 180},
                "servo4": {"min": 0, "max": 180},
                "servo5": {"min": 0, "max": 180},
                "servo6": {"min": 0, "max": 180}
            }

        # -----------------------------
        # SAFETY CONFIG
        # -----------------------------
        self.max_reach = 30  # cm
        self.max_servo_step = 60  # max allowed change in one move

        # stores last known servo positions
        self.last_positions = {
            "servo1": 90,
            "servo2": 90,
            "servo3": 90,
            "servo4": 90,
            "servo5": 90,
            "servo6": 90
        }

    # =====================================================
    # MAIN VALIDATION FUNCTION
    # =====================================================
    def validate(self, steps, target_position=None):

        logs = []
        logs.append("Safety validation started")

        # -----------------------------
        # STEP 1: Normalize input
        # -----------------------------
        if isinstance(steps, dict):
            converted = []

            for k, v in steps.items():
                if "servo" in k:
                    converted.append({
                        "servo_id": int(k.replace("servo", "")),
                        "angle": v
                    })

            steps = converted

        if not isinstance(steps, list):
            return self._fail("Invalid step format (must be list or dict)", logs)

        # -----------------------------
        # STEP 2: Validate each step
        # -----------------------------
        for step in steps:

            # -------------------------
            # Servo step validation
            # -------------------------
            if "servo_id" in step:

                sid = step["servo_id"]
                angle = step.get("angle", None)

                if angle is None:
                    return self._fail(f"Missing angle for servo {sid}", logs)

                servo_key = f"servo{sid}"

                # check servo exists
                if servo_key not in self.limits:
                    return self._fail(f"Invalid servo ID: {sid}", logs)

                limits = self.limits[servo_key]

                # range check
                if not (limits["min"] <= angle <= limits["max"]):
                    return self._fail(
                        f"Servo {sid} angle {angle} out of range {limits}",
                        logs
                    )

                # step jump check
                prev = self.last_positions.get(servo_key, 90)

                if abs(angle - prev) > self.max_servo_step:
                    return self._fail(
                        f"Servo {sid} jump too large ({prev} → {angle})",
                        logs
                    )

            # -------------------------
            # Gripper validation
            # -------------------------
            if "gripper" in step:
                if step["gripper"] not in ["open", "close"]:
                    return self._fail("Invalid gripper command", logs)

            if "gripper_action" in step:
                if step["gripper_action"] not in ["grasp"]:
                    return self._fail("Invalid gripper action", logs)

        # -----------------------------
        # STEP 3: Update state safely
        # -----------------------------
        for step in steps:
            if "servo_id" in step:
                sid = step["servo_id"]
                self.last_positions[f"servo{sid}"] = step["angle"]

        # -----------------------------
        # SAFE OUTPUT
        # -----------------------------
        return {
            "safe": True,
            "reason": "All safety checks passed",
            "logs": logs
        }

    # =====================================================
    # FAILURE RESPONSE FORMAT
    # =====================================================
    def _fail(self, reason, logs):
        logs.append(f"SAFETY BLOCKED: {reason}")

        return {
            "safe": False,
            "reason": reason,
            "logs": logs
        }