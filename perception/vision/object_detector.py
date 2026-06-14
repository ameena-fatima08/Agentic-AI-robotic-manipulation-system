import cv2
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True

except ImportError:
    print("[SIMULATION] tflite_runtime not available")
    TFLITE_AVAILABLE = False

class detect_objects:
    def __init__(self, model_path="yolov8n_saved_model/yolov8n_float16.tflite"):
        # Load TFLite model
        if TFLITE_AVAILABLE:

    # Load TFLite model
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()

            # Model input/output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # Input size
            self.height = self.input_details[0]['shape'][1]
            self.width = self.input_details[0]['shape'][2]

        else:
            print("[SIMULATION] Running without TFLite model")

            self.interpreter = None
            self.input_details = None
            self.output_details = None

            self.height = 640
            self.width = 640
        # COCO labels (for yolov8n pretrained model)
        self.labels = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus",
            "train", "truck", "boat", "traffic light", "fire hydrant",
            "stop sign", "parking meter", "bench", "bird", "cat", "dog",
            "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"
        ]

    def detect(self, frame):
        if not TFLITE_AVAILABLE:

            return [{
                "id": 1,
                "label": "bottle",
                "confidence": 0.99,
                "bbox": [100, 100, 200, 200],
                "center": [150, 150]
            }]

        img = cv2.resize(frame, (self.width, self.height))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        input_data = np.expand_dims(img_rgb, axis=0)

        # Normalize
        input_data = np.array(input_data, dtype=np.float32) / 255.0

        # Set input tensor
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            input_data
        )

        # Run inference
        self.interpreter.invoke()

        # Get output tensor
        output_data = self.interpreter.get_tensor(
            self.output_details[0]['index']
        )

        detections = []

        # YOLO output parsing
        for detection in output_data[0]:

            confidence = detection[4]

            if confidence > 0.5:

                x_center, y_center, w, h = detection[:4]

                x1 = int((x_center - w / 2) * frame.shape[1])
                y1 = int((y_center - h / 2) * frame.shape[0])
                x2 = int((x_center + w / 2) * frame.shape[1])
                y2 = int((y_center + h / 2) * frame.shape[0])

                class_scores = detection[5:]
                class_id = np.argmax(class_scores)

                label = (
                    self.labels[class_id]
                    if class_id < len(self.labels)
                    else str(class_id)
                )

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                detections.append({
                    "id": int(class_id),
                    "label": label,
                    "confidence": round(float(confidence), 2),
                    "bbox": [x1, y1, x2, y2],
                    "center": [center_x, center_y]
                })

        return detections