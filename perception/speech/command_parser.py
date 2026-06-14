import json


def parse_command(text):
    parser = CommandParser(
        "robo",
        ["move left", "move up", "move down", "move right",
         "pick up", "drop", "open gripper", "close gripper", "stop", "bring"]
    )

    if not parser.check_wake_word(text):
        print("Wake word not detected.")
        return None

    return parser.parse_command(text)


class CommandParser:

    def __init__(self, wake_word, commands):
        self.wake_word = wake_word.lower()
        self.commands = commands

    def check_wake_word(self, text):
        if not text:
            return False

        if self.wake_word in text.lower():
            print("Wake word detected!")
            return True

        return False

    def parse_command(self, text):
        if not text:
            return None

        text = text.lower().replace(self.wake_word, "").strip()

        structured_output = {
            "action": None,
            "object": None,
            "destination": None,
            "confidence": 0.95
        }

        words = text.split()

        IGNORE = ["the", "a", "an", "me", "that"]

        # -------------------------
        # MOVE
        # -------------------------
        if "move" in words:
            structured_output["action"] = "move"

            if "left" in words:
                structured_output["destination"] = "left"
            elif "right" in words:
                structured_output["destination"] = "right"
            elif "up" in words:
                structured_output["destination"] = "forward"
            elif "down" in words:
                structured_output["destination"] = "backward"

            print("Valid command: move")
            return structured_output

        # -------------------------
        # PICK
        # -------------------------
        elif any(w in words for w in ["pick", "grab", "take"]):
            structured_output["action"] = "pick"

            for w in reversed(words):
                if w not in ["pick", "grab", "take"] + IGNORE:
                    structured_output["object"] = w
                    break

            print("Valid command: pick")
            return structured_output

        # -------------------------
        # BRING
        # -------------------------
        elif any(w in words for w in ["bring", "give", "deliver"]):
            structured_output["action"] = "bring"

            for w in reversed(words):
                if w not in ["bring", "give", "deliver"] + IGNORE:
                    structured_output["object"] = w
                    break

            print("Valid command: bring")
            return structured_output

        # -------------------------
        # DROP
        # -------------------------
        elif "drop" in words or "place" in words:
            structured_output["action"] = "drop"

            for w in reversed(words):
                if w not in ["drop", "place"] + IGNORE:
                    structured_output["object"] = w
                    break

            print("Valid command: drop")
            return structured_output

        # -------------------------
        # GRIPPER
        # -------------------------
        elif "open" in words:
            structured_output["action"] = "open_gripper"
            return structured_output

        elif "close" in words:
            structured_output["action"] = "close_gripper"
            return structured_output

        # -------------------------
        # STOP
        # -------------------------
        elif "stop" in words:
            structured_output["action"] = "stop"
            return structured_output

        print("Invalid command.")
        return None

    def get_grammar(self):
        return json.dumps(self.commands)