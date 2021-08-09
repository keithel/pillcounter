# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

import os
import imghdr
import cv2
import numpy as np
from ImageProviders import CVImageProvider

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal()
    image_path_changed = Signal()
    image_count_changed = Signal()
    pill_count_changed = Signal()
    hue_low_changed = Signal()
    hue_high_changed = Signal()
    saturation_low_changed = Signal()
    saturation_high_changed = Signal()
    value_low_changed = Signal()
    value_high_changed = Signal()

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = ""
        self._image_count = 0
        self._pill_count = -1
        self._hue_low = 0
        self._hue_high = 180
        self._saturation_low = 0
        self._saturation_high = 255
        self._value_low = 0
        self._value_high = 255

    @Slot()
    def activate(self):
        self.hue_low_changed.connect(self.process_image)
        self.hue_high_changed.connect(self.process_image)
        self.saturation_low_changed.connect(self.process_image)
        self.saturation_high_changed.connect(self.process_image)
        self.value_low_changed.connect(self.process_image)
        self.value_high_changed.connect(self.process_image)

    @Slot()
    def update(self):
        self.process_image()

    def process_image(self):
        try:
            print(f"Processing image {self._image_path} with hsv thresholds: h {self._hue_low}-{self._hue_high}, s {self._saturation_low}-{self._saturation_high}, v {self._value_low}-{self._value_high}")
            # Kick off work to count pills
            # Going to see if this technique will work for pills:
            # https://stackoverflow.com/questions/58751101/count-number-of-cells-in-the-image
            # https://stackoverflow.com/questions/17239253/opencv-bgr2hsv-creates-lots-of-artifacts
            image = cv2.imread(self._image_path)
    #        original = image.copy()
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            hsv_lower = np.array([self._hue_low, self._saturation_low,
                                  self._value_low])  # [156, 60, 0])
            hsv_upper = np.array([self._hue_high, self._saturation_high,
                                  self._value_high])  # [179, 115, 255])

            # https://docs.opencv.org/3.4/da/d97/tutorial_threshold_inRange.html
            mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

            image_provider = CVImageProvider.instance()
            image_provider.set_cv_image(self._image_path, mask)
            self.increment_image_count()
        except cv2.error as e:
            print("cv2.error: " + str(e))

    def get_image_format(self):
        return self._image_format

    def set_image_format(self, image_format):
        self._image_format = image_format
        self.image_format_changed.emit()

    def get_image_path(self):
        return self._image_path

    def set_image_path(self, image_path):
        self._image_path = image_path
        self.image_path_changed.emit()

        # Validate if the path is valid
        if not os.path.isfile(image_path):
            return

        # Validate if the file is in a supported image format.
        self.set_image_format(imghdr.what(image_path))

        self.process_image()

    def get_image_count(self):
        return self._image_count

    def increment_image_count(self):
        self._image_count += 1
        self.image_count_changed.emit()

    def get_pill_count(self):
        return self._pill_count

    def set_pill_count(self, pill_count):
        self._pill_count = pill_count
        self.pill_count_changed.emit()

    def get_hue_low(self):
        return self._hue_low

    def set_hue_low(self, low):
        self._hue_low = low
        self.hue_low_changed.emit()

    def get_hue_high(self):
        return self._hue_high

    def set_hue_high(self, high):
        self._hue_high = high
        self.hue_high_changed.emit()

    def get_saturation_low(self):
        return self._saturation_low

    def set_saturation_low(self, low):
        self._saturation_low = low
        self.saturation_low_changed.emit()

    def get_saturation_high(self):
        return self._saturation_high

    def set_saturation_high(self, high):
        self._saturation_high = high
        self.saturation_high_changed.emit()

    def get_value_low(self):
        return self._value_low

    def set_value_low(self, low):
        self._value_low = low
        self.value_low_changed.emit()

    def get_value_high(self):
        return self._value_high

    def set_value_high(self, high):
        self._value_high = high
        self.value_high_changed.emit()

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path, set_image_path,
                          notify=image_path_changed)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    hue_low = Property(int, get_hue_low, set_hue_low, notify=hue_low_changed)
    hue_high = Property(int, get_hue_high, set_hue_high,
                        notify=hue_high_changed)
    saturation_low = Property(int, get_saturation_low, set_saturation_low,
                              notify=saturation_low_changed)
    saturation_high = Property(int, get_saturation_high, set_saturation_high,
                               notify=saturation_high_changed)
    value_low = Property(int, get_value_low, set_value_low,
                         notify=value_low_changed)
    value_high = Property(int, get_value_high, set_value_high,
                          notify=value_high_changed)
