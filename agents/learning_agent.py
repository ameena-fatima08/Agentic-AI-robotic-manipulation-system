from datetime import datetime

from agents import memory_collection, history_collection


class LearningAgent:

    def __init__(self):

        # -----------------------------
        # STATE
        # -----------------------------
        self.state = "idle"
        self.holding = False
        self.current_object = None
        self.last_command = None
        self.position = "home"

        # -----------------------------
        # MEMORY
        # -----------------------------
        self.history = []
        self.memory = {}
        self.retry_count = 0

        # -----------------------------
        # LOAD MEMORY FROM MONGODB
        # -----------------------------
        try:
            memory_doc = memory_collection.find_one(
                {"_id": "system_memory"}
            )

            if memory_doc:
                self.memory = memory_doc.get("memory", {})

        except Exception as e:
            print(f"⚠️ MongoDB load error: {e}")

    # -----------------------------
    # SAVE MEMORY
    # -----------------------------
    def save(self):

        try:
            memory_collection.update_one(
                {"_id": "system_memory"},
                {
                    "$set": {
                        "memory": self.memory
                    }
                },
                upsert=True
            )

        except Exception as e:
            print(f"⚠️ MongoDB save error: {e}")

    # -----------------------------
    # STATE MANAGEMENT
    # -----------------------------
    def update_state(self, new_state):
        print(f"State: {self.state} → {new_state}")
        self.state = new_state

    # -----------------------------
    # VALIDATE COMMAND
    # -----------------------------
    def validate_command(self, command):

        action = command.get("action")
        obj = command.get("object")

        self.last_command = command

        if action == "pick" and self.holding:
            return False, "Already holding an object"

        if action == "drop" and not self.holding:
            return False, "No object to drop"

        if action == "bring" and self.holding:
            return False, "Already holding something, cannot bring"

        self.current_object = obj

        return True, None

    # -----------------------------
    # UPDATE AFTER ACTION
    # -----------------------------
    def update_after_action(self, action, success=True):

        if not success:
            self.update_state("error")
            return

        if action == "search":
            self.update_state("searching")

        elif action == "approach":
            self.update_state("approaching")

        elif action == "pick":
            self.holding = True
            self.update_state("holding")

        elif action == "return_home":
            self.position = "home"
            self.update_state("returning")

        elif action == "drop":
            self.holding = False
            self.current_object = None
            self.update_state("idle")

    # -----------------------------
    # MEMORY UPDATE
    # -----------------------------
    def update_memory(self, key, value):

        self.memory[key] = value
        self.save()

    # -----------------------------
    # RECORD EXPERIENCE
    # -----------------------------
    def record(self, command, result):

        try:
            history_collection.insert_one({
                "timestamp": datetime.utcnow(),
                "command": command,
                "result": result
            })

        except Exception as e:
            print(f"⚠️ MongoDB history error: {e}")

        if result == "success":
            self.reset_retry()

    # -----------------------------
    # RETRY LOGIC
    # -----------------------------
    def should_retry(self):
        return self.retry_count < 2

    def increase_retry(self):
        self.retry_count += 1

    def reset_retry(self):
        self.retry_count = 0

    # -----------------------------
    # INTELLIGENT SUGGESTION
    # -----------------------------
    def suggest_action(self):

        try:
            last_success = history_collection.find_one(
                {"result": "success"},
                sort=[("timestamp", -1)]
            )

            if last_success:
                return last_success["command"]

        except Exception as e:
            print(f"⚠️ MongoDB query error: {e}")

        return None