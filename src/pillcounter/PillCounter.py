# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtCore import QThread, QTimer, QUrl, QMetaObject, Q_ARG
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

    def __init__(self):
        super().__init__()
        self._capture = None
        self._frameTimer = QTimer()
        self._frameTimer.timeout.connect(self.process_camera_frame)
        self.running = False # Flag to control the processing loop

        model_path = Path(__file__).resolve().parent / "best.pt"
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        print("Model loaded successfully.")

    def __del__(self):
        if self._capture:
            self._capture.release()

    def rotate_90(self, image):
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    def run_model(self, image):
        """Runs the YOLO model on a single image and emits both original and annotated frames."""
        original_image = image.copy() # Keep a copy of the original
        if image.shape[0] > image.shape[1]:
            image = self.rotate_90(image)
            original_image = self.rotate_90(original_image)


        results = self.model(image, verbose=False)
        pill_count = len(results[0].boxes)
        annotated_frame = results[0].plot()

        cv2.putText(annotated_frame, f"Total Pills: {pill_count}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # --- MODIFIED: Emit original frame, annotated frame, and count ---
        self.processed.emit((annotated_frame, original_image, pill_count))

    @Slot()
    def process_camera_frame(self):
        """Processes a single frame from the camera."""
        if self.running and self._capture and self._capture.isOpened():
            grabbed, image = self._capture.read()
            if grabbed:
                self.run_model(image)

    @Slot(str)
    def process_static_image(self, image_path):
        """Loads and processes a single static image file."""
        try:
            image = cv2.imread(image_path)
            if image is not None:
                self.run_model(image)
            else:
                print(f"Error: Could not read image from path {image_path}")
        except Exception as e:
            print(f"Error processing static image: {e}")

    @Slot()
    def start_live_mode(self):
        """Starts the camera and the processing timer."""
        self.stop_processing() # Ensure any previous state is cleared
        print("Starting live mode...")
        self._capture = cv2.VideoCapture(0)
        if not self._capture.isOpened():
            print("Can't open camera")
            return

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        self._frameTimer.start(30) # Process at ~30 FPS

    @Slot()
    def stop_processing(self):
        """Stops the camera and the timer."""
        self.running = False
        self._frameTimer.stop()
        if self._capture:
            self._capture.release()
            self._capture = None
        print("Processing stopped.")


@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal(str)
    image_count_changed = Signal(int)
    pill_count_changed = Signal(int)
    # New signals to control the UI state
    image_files_loaded = Signal(bool)
    current_image_index_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = "pillCamera"
        self._image_count = 0
        self._pill_count = -1

        self._image_files = []
        self._current_image_index = -1

        self.image_processor = ImageProcessor()
        self.image_processor.processed.connect(self.update_image_provider, Qt.QueuedConnection)
        self.image_processor.start()

    @Slot()
    def quit(self):
        self.image_processor.stop_processing()
        self.image_processor.quit()
        self.image_processor.wait()

    @Slot()
    def activate(self):
        self.setLiveMode()

    @Slot(list)
    def loadImageFiles(self, file_urls):
        self.image_processor.stop_processing()
        self._image_files = [QUrl(url).toLocalFile() for url in file_urls]
        if self._image_files:
            self._current_image_index = 0
            self.image_files_loaded.emit(True)
            self.current_image_index_changed.emit(self._current_image_index)
            self.process_current_image()
        else:
            self.image_files_loaded.emit(False)

    @Slot()
    def nextImage(self):
        if self._image_files and self._current_image_index < len(self._image_files) - 1:
            self._current_image_index += 1
            self.current_image_index_changed.emit(self._current_image_index)
            self.process_current_image()

    @Slot()
    def previousImage(self):
        if self._image_files and self._current_image_index > 0:
            self._current_image_index -= 1
            self.current_image_index_changed.emit(self._current_image_index)
            self.process_current_image()

    @Slot()
    def setLiveMode(self):
        self._image_files = []
        self._current_image_index = -1
        self.image_files_loaded.emit(False)
        QMetaObject.invokeMethod(self.image_processor, "start_live_mode", Qt.QueuedConnection)

    def process_current_image(self):
        if 0 <= self._current_image_index < len(self._image_files):
            path = self._image_files[self._current_image_index]
            QMetaObject.invokeMethod(self.image_processor, "process_static_image", Qt.QueuedConnection, Q_ARG(str, path))

    def update_image_provider(self, data):
        # --- MODIFIED: Handle both annotated and original images ---
        annotated_image, original_image, pill_count = data
        image_provider = CVImageProvider.instance()
        # Set both images in the provider with different prefixes
        image_provider.set_cv_image("annotated_" + self._image_path, annotated_image)
        image_provider.set_cv_image("unannotated_" + self._image_path, original_image)

        self.increment_image_count()
        self.set_pill_count(pill_count)

    def get_image_format(self): return self._image_format
    def set_image_format(self, f):
        self._image_format = f
        self.image_format_changed.emit(f)
    def get_image_path(self): return self._image_path
    def get_image_count(self): return self._image_count
    def increment_image_count(self):
        self._image_count += 1
        self.image_count_changed.emit(self._image_count)
    def get_pill_count(self): return self._pill_count
    def set_pill_count(self, c):
        self._pill_count = c
        self.pill_count_changed.emit(c)
    def get_current_image_index(self): return self._current_image_index

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    current_image_index = Property(int, get_current_image_index, notify=current_image_index_changed)
