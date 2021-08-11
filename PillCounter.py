# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property, QThread, Qt
from PySide6.QtQml import QmlElement

import os
import imghdr
import cv2
import numpy as np
import math
from ImageProviders import CVImageProvider
import imutils

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


class ImageProcessor(QThread):
    processed = Signal(object)

    def __init__(self, image_path, gray_threshold):
        super().__init__()
        self._image_path = image_path
        self._gray_threshold = gray_threshold

    # Default run() method calls exec() which starts a Qt event loop.
    # This is what we want, as we want to get the asynchronous slot calls from
    # the main thread, so we don't override run().

    @Slot()
    def process_image(self):
        """Do the work of processing the image and returning data about the image"""
        image, image_blur, image_blur_gray, image_thresh, closing, opening, pill_count = (None, None, None, None, None, None, -1)

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
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50,50))
            closing = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel)
            opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
            # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
            # dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            # _, last_image = cv2.threshold(dist_transform, 0.3*dist_transform.max(), 255, 0)
            # last_image = np.uint8(last_image)

            contours = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)

            # Need a way to filter out area outliers - those contours that are too big or too small.
            # This I think will involve finding the median of contour areas, and adding some +- factor to use
            # to determine what is a 'good' contour.
            contour_areas = [cv2.contourArea(c) for c in contours]
            contour_areas.sort()
            median_area = contour_areas[round(len(contour_areas)/2)]
            area_thresh = 5000
            pill_contours = [c for c in contours if (cv2.contourArea(c) < median_area + area_thresh and cv2.contourArea(c) > median_area - area_thresh)]
            pill_count = len(pill_contours)

            for (i,c) in enumerate(pill_contours):
                ((x,y), _) = cv2.minEnclosingCircle(c)
                cv2.putText(image, f"#{i+1}", (int(x)-45, int(y)+20), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5)
                cv2.drawContours(image, [c], -1, (80, 10, 255), 2)
                print(f"Contour {i} area: {cv2.contourArea(c)}")
        except cv2.error as e:
            print("cv2.error: " + str(e))

        self.processed.emit((image, image_blur, image_blur_gray, image_thresh, closing, opening, pill_count))

    @Slot(str)
    def set_image_path(self, image_path):
        self._image_path = image_path
        self.process_image()

    @Slot(int)
    def set_gray_threshold(self, gray_threshold):
        self._gray_threshold = gray_threshold
        self.process_image()

@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal(str)
    image_path_changed = Signal(str)
    image_count_changed = Signal(int)
    pill_count_changed = Signal(int)
    gray_threshold_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = ""
        self._image_count = 0
        self._pill_count = -1
        self._gray_threshold = 190

        self.image_processor = ImageProcessor(self._image_path, self._gray_threshold)
        # self.image_processor.moveToThread(self.thread)
        # self.thread.started.connect(self.image_processor.run)
        # self.image_processor.finished.connect(self.thread.quit)
        # self.image_processor.finished.connect(self.image_processor.deleteLater)
        # self.image_processor.finished.connect(self.thread.deleteLater)
        self.image_path_changed.connect(self.image_processor.set_image_path, Qt.QueuedConnection)
        self.image_processor.processed.connect(self.update_image_provider, Qt.QueuedConnection)
        self.image_processor.start()

    @Slot()
    def quit(self):
        self.image_processor.quit()
        self.image_processor.deleteLater()

    @Slot()
    def activate(self):
        self.gray_threshold_changed.connect(self.image_processor.set_gray_threshold, Qt.QueuedConnection)

    @Slot()
    def update(self):
        self.image_path_changed.emit(self._image_path)

    def update_image_provider(self, images):
        print("Images: " + str(len(images)))
        image, image_blur, image_blur_gray, image_thresh, closing, opening, pill_count = images
        image_provider = CVImageProvider.instance()
        image_provider.set_cv_image("orig_" + self._image_path, image)
        image_provider.set_cv_image("1_" + self._image_path, image_blur)
        image_provider.set_cv_image("2_" + self._image_path, image_blur_gray)
        image_provider.set_cv_image("3_" + self._image_path, image_thresh)
        image_provider.set_cv_image("4_" + self._image_path, closing)
        image_provider.set_cv_image("5_" + self._image_path, opening)
        # image_provider.set_cv_image("6_" + self._image_path, last_image)
        image_provider.set_cv_image(self._image_path, opening)
        self.increment_image_count()
        self.set_pill_count(pill_count)

    def get_image_format(self):
        return self._image_format

    def set_image_format(self, image_format):
        self._image_format = image_format
        self.image_format_changed.emit(self._image_format)

    def get_image_path(self):
        return self._image_path

    def set_image_path(self, image_path):
        self._image_path = image_path

        # Validate if the path is valid
        if not os.path.isfile(image_path):
            return

        # Validate if the file is in a supported image format.
        self.set_image_format(imghdr.what(image_path))

        self.image_path_changed.emit(self._image_path)

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

    def get_gray_threshold(self):
        return self._gray_threshold

    def set_gray_threshold(self, threshold):
        self._gray_threshold = threshold
        self.gray_threshold_changed.emit(self._gray_threshold)

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path, set_image_path,
                          notify=image_path_changed)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    gray_threshold = Property(int, get_gray_threshold, set_gray_threshold,
                              notify=gray_threshold_changed)
