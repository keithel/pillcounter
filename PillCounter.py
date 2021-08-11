# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

import os
import imghdr
import cv2
import numpy as np
import math
from ImageProviders import CVImageProvider

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal()
    image_path_changed = Signal()
    image_count_changed = Signal()
    pill_count_changed = Signal()
    gray_threshold_changed = Signal()

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = ""
        self._image_count = 0
        self._pill_count = -1
        self._gray_threshold = 192

    @Slot()
    def activate(self):
        self.gray_threshold_changed.connect(self.process_image)

    @Slot()
    def update(self):
        self.process_image()

    def process_image(self):
        try:
            print(f"Processing image {self._image_path} with gray threshold: {self._gray_threshold}")
            # Kick off work to count pills
            # Going to see if this technique will work for pills:
            # https://stackoverflow.com/questions/58751101/count-number-of-cells-in-the-image
            # https://stackoverflow.com/questions/17239253/opencv-bgr2hsv-creates-lots-of-artifacts
            image = cv2.imread(self._image_path)
    #        original = image.copy()
            image_blur = cv2.medianBlur(image, 25)
            image_blur_gray = cv2.cvtColor(image_blur, cv2.COLOR_BGR2GRAY)
            _, image_thresh = cv2.threshold(image_blur_gray, self._gray_threshold, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
            opening = cv2.morphologyEx(image_thresh, cv2.MORPH_OPEN, kernel)

            # contours = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # contours = contours[0] if len(contours) == 2 else contours[1]

            # minimum_area = 1500
            # average_cell_area = 1600
            # connected_cell_area = 2000
            # pills = 0

            # for c in contours:
            #     area = cv2.contourArea(c)
            #     if area > minimum_area:
            #         cv2.drawContours(image, [c], -1, (80, 10, 255), 2)
            #         if area > connected_cell_area:
            #             pills += math.ceil(area / average_cell_area)
            #         else:
            #             pills += 1

            # self.set_pill_count(pills)

            image_provider = CVImageProvider.instance()
            image_provider.set_cv_image("orig_" + self._image_path, image)
            image_provider.set_cv_image("1_" + self._image_path, image_blur)
            image_provider.set_cv_image("2_" + self._image_path, image_blur_gray)
            image_provider.set_cv_image("3_" + self._image_path, image_thresh)
            image_provider.set_cv_image("4_" + self._image_path, opening)
            image_provider.set_cv_image(self._image_path, image_thresh)
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

    def get_gray_threshold(self):
        return self._gray_threshold

    def set_gray_threshold(self, threshold):
        self._gray_threshold = threshold
        self.gray_threshold_changed.emit()

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path, set_image_path,
                          notify=image_path_changed)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    gray_threshold = Property(int, get_gray_threshold, set_gray_threshold,
                          notify=gray_threshold_changed)
