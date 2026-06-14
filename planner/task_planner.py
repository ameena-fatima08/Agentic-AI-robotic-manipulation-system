class TaskPlanner:

    def __init__(self):
        self.state = "idle"
        self.holding = False

    def plan_task(self, command, detections, context):

        action = command.get("action")
        obj = command.get("object")

        # -----------------------------
        # 🚫 STATE SAFETY
        # -----------------------------
        if self.holding and action in ["pick", "bring"]:
            return {
                "status": "error",
                "message": "Already holding object. Drop first."
            }

        if not self.holding and action == "drop":
            return {
                "status": "error",
                "message": "Nothing to drop"
            }

        # -----------------------------
        # 🎯 ACTION LOGIC
        # -----------------------------

        if action == "pick":
            return self._plan_pick()

        elif action == "bring":
            return self._plan_bring()

        elif action == "drop":
            return self._plan_drop()

        elif action == "move":
            return self._plan_move(command.get("destination"))

        return {"status": "error", "message": "Invalid action"}

    # ---------------------------------
    # PICK
    # ---------------------------------
    def _plan_pick(self):

        steps = [
            {"gripper": "open"},
            {"servo_id": 1, "angle": 90},
            {"servo_id": 2, "angle": 50},
            {"servo_id": 3, "angle": 70},
            {"gripper": "close"},
            {"servo_id": 3, "angle": 40}
        ]

        self.holding = True
        self.state = "holding"

        return {"status": "ok", "steps": steps}

    # ---------------------------------
    # BRING (🔥 FIXED)
    # ---------------------------------
    def _plan_bring(self):

        steps = [
            {"gripper": "open"},
            {"servo_id": 1, "angle": 90},
            {"servo_id": 2, "angle": 50},
            {"servo_id": 3, "angle": 70},
            {"gripper": "close"},
            {"servo_id": 3, "angle": 40},

            # 🔥 RETURN HOME
            {"servo_id": 1, "angle": 90},
            {"servo_id": 2, "angle": 40},

            # 🔥 DROP
            {"gripper": "open"}
        ]

        self.holding = False
        self.state = "idle"

        return {"status": "ok", "steps": steps}

    # ---------------------------------
    # DROP
    # ---------------------------------
    def _plan_drop(self):

        steps = [{"gripper": "open"}]

        self.holding = False
        self.state = "idle"
        self.update_after_action("drop", success=True)

        return {"status": "ok", "steps": steps}

    # ---------------------------------
    # MOVE
    # ---------------------------------
    def _plan_move(self, direction):

        if direction == "left":
            return {"status": "ok", "steps": [{"move": "left"}]}

        if direction == "right":
            return {"status": "ok", "steps": [{"move": "right"}]}

        if direction == "forward":
            return {"status": "ok", "steps": [{"move": "forward"}]}

        if direction == "backward":
            return {"status": "ok", "steps": [{"move": "backward"}]}

        return {"status": "error", "message": "Invalid move"}