# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property, QThread, Qt, QTimer
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

    def __init__(self, blur_aperture, gray_threshold, kernel_size, closing_enabled, opening_enabled):
        super().__init__()
        self._blur_aperture = blur_aperture
        self._gray_threshold = gray_threshold
        self._kernel_size = kernel_size
        self._closing_enabled = closing_enabled
        self._opening_enabled = opening_enabled
        self._capture = cv2.VideoCapture(0)

        if not self._capture.isOpened():
            print("Can't open camera")
            raise OSError(-1, "OpenCV cannot open camera", "0")

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._frameTimer = QTimer()
        self._frameTimer.timeout.connect(self.process_image)
        self._frameTimer.start(16)

    def __del__(self):
        self._capture.release()

    # Default run() method calls exec() which starts a Qt event loop.
    # This is what we want, as we want to get the asynchronous slot calls from
    # the main thread, so we don't override run().

    def rotate_90(self, image):
        degrees = 90
        if image is None:
            return
        size = image.shape[1::-1]
        image_center = tuple(np.array(size) / 2)
        rotation_matrix = cv2.getRotationMatrix2D(image_center, degrees, 1)
        radians = math.radians(degrees)
        sin = math.sin(radians)
        cos = math.cos(radians)
        b_w = int((size[1] * abs(sin)) + (size[0] * abs(cos)))
        b_h = int((size[1] * abs(cos)) + (size[0] * abs(sin)))

        rotation_matrix[0, 2] += ((b_w / 2) - image_center[0])
        rotation_matrix[1, 2] += ((b_h / 2) - image_center[1])

        result = cv2.warpAffine(image, rotation_matrix, (b_w, b_h), flags=cv2.INTER_LINEAR)

        return result

    @Slot()
    def process_image(self):
        """Do the work of processing the image and returning data about the image"""
        image, image_blur, image_blur_gray, image_thresh, closing, opening, pill_count = (None, None, None, None, None, None, 0)

        try:
            # print(f"Grabbing camera frame, processing with blur {self._blur_aperture}, gray threshold {self._gray_threshold}, kernel size {self._kernel_size}")
            # Kick off work to count pills
            # Going to see if this technique will work for pills:
            # https://stackoverflow.com/questions/58751101/count-number-of-cells-in-the-image
            # https://stackoverflow.com/questions/17239253/opencv-bgr2hsv-creates-lots-of-artifacts
            grabbed, image = self._capture.read()
            if image.shape[0] > image.shape[1]:
                image = self.rotate_90(image)
            image_blur = cv2.medianBlur(image, self._blur_aperture)
            image_blur_gray = cv2.cvtColor(image_blur, cv2.COLOR_BGR2GRAY)
            _, image_thresh = cv2.threshold(image_blur_gray, self._gray_threshold, 255, cv2.THRESH_BINARY)

            perform_contours_on = image_thresh
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self._kernel_size,self._kernel_size))

            closing, opening = (None, None)
            if self._closing_enabled:
                closing = cv2.morphologyEx(image_thresh, cv2.MORPH_CLOSE, kernel)
                perform_contours_on = closing
            if self._opening_enabled:
                opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
                perform_contours_on = opening
            # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
            # dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            # _, last_image = cv2.threshold(dist_transform, 0.3*dist_transform.max(), 255, 0)
            # last_image = np.uint8(last_image)

            contours = cv2.findContours(perform_contours_on, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)

            if len(contours) > 0:
                # Need a way to filter out area outliers - those contours that are too big or too small.
                # This I think will involve finding the median of contour areas, and adding some +- factor to use
                # to determine what is a 'good' contour.
                contour_areas = [cv2.contourArea(c) for c in contours]
                contour_areas.sort()
                median_area = contour_areas[round(len(contour_areas)/2)]
                area_thresh = median_area * 0.2 # 20% of the median area
                pill_contours = [c for c in contours if (cv2.contourArea(c) < median_area + area_thresh and cv2.contourArea(c) > median_area - area_thresh)]
                pill_count = len(pill_contours)

                area_strs = [ f"{len(pill_contours)} contours. Areas: " ]
                for (i,c) in enumerate(contours):
                    area = cv2.contourArea(c)
                    ((x,y), _) = cv2.minEnclosingCircle(c)
                    if area < median_area + area_thresh and area > median_area - area_thresh:
                        # TODO: Handle pills touching - include 2x, 3x, 4x median_area +/- area_thresh.
                        # TODO: To handle any multiple, make condition: if area % median_area < area_thresh and (area % median_area - median_area) > -area_thresh
                        # TODO: Then, pill_count will have to be adjusted by area / median_area or area / median_area+1 depending on where the error is.
                        cv2.putText(image, f"#{i+1}", (int(x)-12, int(y)+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
                        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                        area_strs.append(str(cv2.contourArea(c)))
                        if (i < len(pill_contours)-1):
                            area_strs.append(", ")
                    else:
                        # Contours that aren't identified as pills.
                        cv2.putText(image, f"#{i+1}", (int(x)-12, int(y)+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
                        cv2.drawContours(image, [c], -1, (0, 0, 127), 2)

                print("".join(area_strs))
        except cv2.error as e:
            print("cv2.error: " + str(e))

        self.processed.emit((image, image_blur, image_blur_gray, image_thresh, closing, opening, pill_count))

    @Slot(int)
    def set_blur_aperture(self, blur_aperture):
        self._blur_aperture = blur_aperture

    @Slot(int)
    def set_gray_threshold(self, gray_threshold):
        self._gray_threshold = gray_threshold

    @Slot(int)
    def set_kernel_size(self, kernel_size):
        self._kernel_size = kernel_size

    @Slot(bool)
    def set_closing_enabled(self, closing_enabled):
        self._closing_enabled = closing_enabled

    @Slot(bool)
    def set_opening_enabled(self, opening_enabled):
        self._opening_enabled = opening_enabled

@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal(str)
    image_count_changed = Signal(int)
    pill_count_changed = Signal(int)
    blur_aperture_changed = Signal(int)
    gray_threshold_changed = Signal(int)
    kernel_size_changed = Signal(int)
    closing_enabled_changed = Signal(bool)
    opening_enabled_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = "pillCamera"
        self._image_count = 0
        self._pill_count = -1
        self._blur_aperture = 13 # for brown ibuprofen and atomoxetine caplets
        self._gray_threshold = 135
        self._kernel_size = 19
        self._closing_enabled = True
        self._opening_enabled = False

        self.image_processor = ImageProcessor(self._blur_aperture, self._gray_threshold, self._kernel_size, self._closing_enabled, self._opening_enabled)
        # self.image_processor.moveToThread(self.thread)
        # self.thread.started.connect(self.image_processor.run)
        # self.image_processor.finished.connect(self.thread.quit)
        # self.image_processor.finished.connect(self.image_processor.deleteLater)
        # self.image_processor.finished.connect(self.thread.deleteLater)
        self.image_processor.processed.connect(self.update_image_provider, Qt.QueuedConnection)
        self.image_processor.start()

    @Slot()
    def quit(self):
        self.image_processor.quit()
        self.image_processor.deleteLater()

    @Slot()
    def activate(self):
        self.blur_aperture_changed.connect(self.image_processor.set_blur_aperture, Qt.QueuedConnection)
        self.gray_threshold_changed.connect(self.image_processor.set_gray_threshold, Qt.QueuedConnection)
        self.kernel_size_changed.connect(self.image_processor.set_kernel_size, Qt.QueuedConnection)
        self.closing_enabled_changed.connect(self.image_processor.set_closing_enabled, Qt.QueuedConnection)
        self.opening_enabled_changed.connect(self.image_processor.set_opening_enabled, Qt.QueuedConnection)

    def update_image_provider(self, images):
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

    def get_blur_aperture(self):
        return self._blur_aperture

    def set_blur_aperture(self, blur_aperture):
        self._blur_aperture = blur_aperture
        self.blur_aperture_changed.emit(self._blur_aperture)

    def get_gray_threshold(self):
        return self._gray_threshold

    def set_gray_threshold(self, threshold):
        self._gray_threshold = threshold
        self.gray_threshold_changed.emit(self._gray_threshold)

    def get_kernel_size(self):
        return self._kernel_size

    def set_kernel_size(self, kernel_size):
        self._kernel_size = kernel_size
        self.kernel_size_changed.emit(self._kernel_size)

    def get_closing_enabled(self):
        return self._closing_enabled

    def set_closing_enabled(self, closing_enabled):
        self._closing_enabled = closing_enabled
        self.closing_enabled_changed.emit(self._closing_enabled)

    def get_opening_enabled(self):
        return self._opening_enabled

    def set_opening_enabled(self, opening_enabled):
        self._opening_enabled = opening_enabled
        self.opening_enabled_changed.emit(self._opening_enabled)

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path)
    image_count = Property(int, get_image_count, notify=image_count_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
    blur_aperture = Property(int, get_blur_aperture, set_blur_aperture,
                              notify=blur_aperture_changed)
    gray_threshold = Property(int, get_gray_threshold, set_gray_threshold,
                              notify=gray_threshold_changed)
    kernel_size = Property(int, get_kernel_size, set_kernel_size,
                              notify=kernel_size_changed)
    closing_enabled = Property(int, get_closing_enabled, set_closing_enabled,
                              notify=closing_enabled_changed)
    opening_enabled = Property(int, get_opening_enabled, set_opening_enabled,
                              notify=opening_enabled_changed)
