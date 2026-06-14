import cv2
import time

from picamera2 import Picamera2
from perception.vision.object_detector import detect_objects


class VisionAgent:

    def __init__(self):

        self.detector = detect_objects()

        # Raspberry Pi Camera
        self.picam2 = Picamera2()

        self.picam2.configure(
            self.picam2.create_preview_configuration(
                main={"size": (640, 480)}
            )
        )

        self.picam2.start()

        time.sleep(2)

        self.last_object = None
        self.last_label = None
        self.current_frame = None

        print("📷 Pi Camera Initialized")

    def get_detections(self):

        try:
            frame = self.picam2.capture_array()

            if frame is None:
                return {
                    "status": "camera_error",
                    "detections": []
                }

            self.current_frame = frame

            # Debug image (optional)
            cv2.imwrite("latest_frame.jpg", frame)

            detections = self.detector.detect(frame)

            print("\n========== DETECTIONS ==========")
            print(detections)
            print("================================\n")

            if not detections:
                return {
                    "status": "no_object",
                    "detections": []
                }

            return {
                "status": "ok",
                "detections": detections
            }

        except Exception as e:
            print("Vision Error:", e)

            return {
                "status": "error",
                "detections": [],
                "message": str(e)
            }

    @staticmethod
    def get_object_center(detection):

        x1, y1, x2, y2 = detection["bbox"]

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        return cx, cy

    def get_frame(self):

        return self.current_frame

    def track_object(self, detections, target_label):

        if not detections:
            return None

        candidates = [
            d for d in detections
            if target_label.lower() in d["label"].lower()
        ]

        if not candidates:
            return None

        if self.last_object is None:

            best = max(
                candidates,
                key=lambda x: x["confidence"]
            )

            self.last_object = best
            return best

        prev_x, prev_y = self.last_object["center"]

        def distance(obj):

            x, y = obj["center"]

            return (
                ((x - prev_x) ** 2 +
                 (y - prev_y) ** 2) ** 0.5
            )

        best = min(candidates, key=distance)

        self.last_object = best

        return best

    def release(self):

        try:
            self.picam2.stop()
            print("📷 Camera Released")

        except Exception:
            pass