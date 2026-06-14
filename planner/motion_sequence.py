class MotionPlanner:
    def __init__(self):
        pass

    def plan(self, command, detections):
        """
        command: string (speech input)
        detections: list of detected objects from vision
        """

        command = command.lower()

        # Extract target object from command
        target_object = None

        for word in command.split():
            for det in detections:
                if word == det["label"]:
                    target_object = det
                    break

        if target_object is None:
            return {"status": "object_not_found"}

        cx, cy = target_object["center"]

        # Generate motion plan
        motion_plan = [
            {"action": "move_to", "target": [cx, cy]},
            {"action": "lower_arm"},
            {"action": "close_gripper"},
            {"action": "lift_arm"}
        ]

        return {
            "status": "success",
            "object": target_object["label"],
            "motion_sequence": motion_plan
        }