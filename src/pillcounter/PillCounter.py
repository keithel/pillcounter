# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtCore import QThread, QTimer, QUrl, QMetaObject, Q_ARG
from PySide6.QtQml import QmlElement
from pathlib import Path
import time
from collections import deque

import cv2
import numpy as np
import math
from .ImageProviders import CVImageProvider
from ultralytics import YOLO # Import YOLO
from ultralytics.utils.plotting import colors # Just need the color utility

from . import config

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


class ImageProcessor(QThread):
    processed = Signal(object)

    def __init__(self):
        super().__init__()
        self._capture = None
        self._frameTimer = QTimer()
        self._frameTimer.timeout.connect(self.process_camera_frame)
        self.running = False
        self._camera_idx = -1

        self._confidence_threshold = -1
        self._font_size = -1

        # --- NEW: For running average in live mode ---
        self._count_history = deque() # Stores (timestamp, count) tuples

        model_path = Path(__file__).resolve().parent / config.model_name
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        print("Model loaded successfully.")

    def __del__(self):
        if self._capture:
            self._capture.release()

    def rotate_90(self, image):
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    def run_model(self, image, is_live=False):
        if self._confidence_threshold == -1:
            print(f"Invalid confidence threshold {self._confidence_threshold}")
            return
        original_image = image.copy()
        if image.shape[0] > image.shape[1]:
            image = self.rotate_90(image)
            original_image = self.rotate_90(original_image)

        results = self.model(image, conf=self._confidence_threshold, verbose=False)
        pill_count = len(results[0].boxes)
        display_count = pill_count # Default to instantaneous count

        # --- NEW: Calculate running average for live mode ---
        if is_live:
            current_time = time.monotonic()
            # Add the new count and timestamp
            self._count_history.append((current_time, pill_count))

            # Remove counts older than 5 seconds
            while self._count_history and self._count_history[0][0] < current_time - 5.0:
                self._count_history.popleft()

            # Calculate the running average if there are any samples
            if self._count_history:
                counts = [c for t, c in self._count_history]
                display_count = round(sum(counts) / len(counts))
        # --- End of new logic ---

        annotated_frame = image.copy()
        for box in results[0].boxes:
            x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
            class_id = int(box.cls)
            class_letters = ['C', 'T' ]
            confidence = float(box.conf)
            confidence_str = f"{confidence:.2f}"[1:]
            label = f'{class_letters[class_id]}{confidence_str}'
            color = colors(class_id, True)
            line_thickness = 1

            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, line_thickness)

            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self._font_size, 1)

            text_color = color
            cv2.putText(annotated_frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, self._font_size, text_color, 1, cv2.LINE_AA)

        # --- MODIFIED: Use the new display_count variable ---
        #cv2.putText(annotated_frame, f"Total Pills: {display_count}", (20, 50),
        #            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)

        # --- MODIFIED: Emit the new display_count variable ---
        self.processed.emit((annotated_frame, original_image, display_count))

    @Slot()
    def process_camera_frame(self):
        if self.running and self._capture and self._capture.isOpened():
            grabbed, image = self._capture.read()
            if grabbed:
                # --- MODIFIED: Pass is_live=True ---
                self.run_model(image, is_live=True)

    @Slot(str)
    def process_static_image(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is not None:
                # --- MODIFIED: Pass is_live=False (default behavior) ---
                self.run_model(image, is_live=False)
            else:
                print(f"Error: Could not read image from path {image_path}")
        except Exception as e:
            print(f"Error processing static image: {e}")

    @Slot(float)
    def set_confidence_threshold(self, threshold):
        self._confidence_threshold = threshold

    @Slot(float)
    def set_font_size(self, size):
        self._font_size = size

    @Slot()
    def start_live_mode(self):
        self.stop_processing()
        print("Starting live mode...")
        for i in range(5, -1, -1):
            self._capture = cv2.VideoCapture(i)
            if self._capture.isOpened():
                self._camera_idx = i
                break
        if not self._capture.isOpened():
            print("Can't open camera")
            return
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print(f"Using camera {self._camera_idx}")
        self.running = True
        self._frameTimer.start(30)

    @Slot()
    def stop_processing(self):
        self.running = False
        self._frameTimer.stop()
        if self._capture:
            self._capture.release()
            self._capture = None
        # --- NEW: Clear history when stopping ---
        self._count_history.clear()
        print("Processing stopped.")


@QmlElement
class PillCounter(QObject):
    live_image_count_changed = Signal(int)
    static_image_count_changed = Signal(int)
    pill_count_changed = Signal(int)
    image_files_loaded = Signal(bool)
    current_image_index_changed = Signal(int)
    confidence_threshold_changed = Signal(float)
    font_size_changed = Signal(float)

    def __init__(self):
        super().__init__()
        self._image_path = "pillCamera"
        self._live_image_count = 0
        self._pill_count = -1
        self._image_files = []
        self._current_image_index = -1
        self._confidence_threshold = -1
        self._font_size = -1

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
        self.confidence_threshold_changed.connect(self.image_processor.set_confidence_threshold)
        self.font_size_changed.connect(self.image_processor.set_font_size)
        self.setLiveMode(True)

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
        self.static_image_count_changed.emit(len(self._image_files))

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

    @Slot(bool)
    def setLiveMode(self, enable):
        if enable:
            self._image_files = []
            self.static_image_count_changed.emit(len(self._image_files))
            self._current_image_index = -1
            self.image_files_loaded.emit(False)
            QMetaObject.invokeMethod(self.image_processor, "start_live_mode", Qt.QueuedConnection)
        else:
            self.image_processor.stop_processing()

    def process_current_image(self):
        if 0 <= self._current_image_index < len(self._image_files):
            path = self._image_files[self._current_image_index]
            QMetaObject.invokeMethod(self.image_processor, "process_static_image", Qt.QueuedConnection, Q_ARG(str, path))

    @Slot()
    def processCurrentImage(self):
        self.process_current_image()

    def update_image_provider(self, data):
        annotated_image, original_image, pill_count = data
        image_provider = CVImageProvider.instance()
        image_provider.set_cv_image("annotated_" + self._image_path, annotated_image)
        image_provider.set_cv_image("unannotated_" + self._image_path, original_image)
        self.increment_live_image_count()
        self.set_pill_count(pill_count)

    def get_image_path(self): return self._image_path
    def get_live_image_count(self): return self._live_image_count
    def get_static_image_count(self): return len(self._image_files)
    def increment_live_image_count(self):
        self._live_image_count += 1
        self.live_image_count_changed.emit(self._live_image_count)
    def get_pill_count(self): return self._pill_count
    def set_pill_count(self, c):
        self._pill_count = c
        self.pill_count_changed.emit(c)
    def get_current_image_index(self): return self._current_image_index

    def get_confidence_threshold(self):
        return self._confidence_threshold

    def set_confidence_threshold(self, threshold):
        if self._confidence_threshold != threshold:
            self._confidence_threshold = threshold
            self.confidence_threshold_changed.emit(self._confidence_threshold)

    def get_font_size(self):
        return self._font_size

    def set_font_size(self, size):
        if self._font_size != size:
            self._font_size = size
            self.font_size_changed.emit(self._font_size)

    image_path = Property(str, get_image_path, constant=True)
    live_image_count = Property(int, get_live_image_count, notify=live_image_count_changed)
    static_image_count = Property(int, get_static_image_count, notify=static_image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    current_image_index = Property(int, get_current_image_index, notify=current_image_index_changed)
    confidence_threshold = Property(float, get_confidence_threshold, set_confidence_threshold, notify=confidence_threshold_changed)
    font_size = Property(float, get_font_size, set_font_size, notify=font_size_changed)
