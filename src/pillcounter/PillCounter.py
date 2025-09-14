# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property, QThread, Qt, QTimer
from PySide6.QtQml import QmlElement
from pathlib import Path

import cv2
import numpy as np
import math
from .ImageProviders import CVImageProvider
from ultralytics import YOLO # Import YOLO

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


class ImageProcessor(QThread):
    processed = Signal(object)

    def __init__(self): # Removed old OpenCV parameters
        super().__init__()
        self._capture = cv2.VideoCapture(0)

        if not self._capture.isOpened():
            print("Can't open camera")
            raise OSError(-1, "OpenCV cannot open camera", "0")

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # --- NEW: Load your trained YOLOv8 model ---
        # Construct the path to the model file relative to this script
        model_path = Path(__file__).resolve().parent / "best.pt"
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        print("Model loaded successfully.")
        # --- End of new section ---

        self._frameTimer = QTimer()
        self._frameTimer.timeout.connect(self.process_image)
        self._frameTimer.start(30) # Process at ~30 FPS

    def __del__(self):
        self._capture.release()

    def rotate_90(self, image):
        # This function can remain as-is if you need it.
        # It's generally better to orient the camera correctly if possible.
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    @Slot()
    def process_image(self):
        """Process the camera frame using the YOLO model."""
        try:
            grabbed, image = self._capture.read()
            if not grabbed:
                return

            if image.shape[0] > image.shape[1]:
                image = self.rotate_90(image)

            # --- NEW: Perform detection with YOLO model ---
            # The model call handles all the detection logic.
            # verbose=False reduces console spam.
            results = self.model(image, verbose=False)

            # Get the number of detected pills
            pill_count = len(results[0].boxes)

            # Use the model's built-in plot() method to draw boxes and labels
            annotated_frame = results[0].plot()

            # Display the final total count on the image
            cv2.putText(annotated_frame, f"Total Pills: {pill_count}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            # --- End of new section ---

            # We emit the annotated frame to be displayed in the GUI.
            # The other images are no longer relevant, but we can send placeholders.
            self.processed.emit((annotated_frame, pill_count))

        except Exception as e:
            print(f"Error processing image: {e}")

@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal(str)
    image_count_changed = Signal(int)
    pill_count_changed = Signal(int)
    # --- REMOVED obsolete properties for blur, threshold, etc. ---

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = "pillCamera"
        self._image_count = 0
        self._pill_count = -1

        # Image processor no longer takes any parameters
        self.image_processor = ImageProcessor()
        self.image_processor.processed.connect(self.update_image_provider, Qt.QueuedConnection)
        self.image_processor.start()

    @Slot()
    def quit(self):
        self.image_processor.quit()
        self.image_processor.deleteLater()

    @Slot()
    def activate(self):
        # Nothing to connect here anymore
        pass

    def update_image_provider(self, images):
        image, pill_count = images
        image_provider = CVImageProvider.instance()
        # Update the main image view
        image_provider.set_cv_image("orig_" + self._image_path, image)

        self.increment_image_count()
        self.set_pill_count(pill_count)

    # --- Getter/Setter functions for pill count, image path etc. remain the same ---
    # (Getters/setters for blur, threshold etc. have been removed)
    def get_image_format(self):
        return self._image_format

    def set_image_format(self, image_format):
        self._image_format = image_format
        self.image_format_changed.emit(self._image_format)

    def get_image_path(self):
        return self._image_path

    def get_image_count(self):
        return self._image_count

    def increment_image_count(self):
        self._image_count += 1
        self.image_count_changed.emit(self._image_count)

    def get_pill_count(self):
        return self._pill_count

    def set_pill_count(self, pill_count):
        self._pill_count = pill_count
        self.pill_count_changed.emit(self._pill_count)


    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
