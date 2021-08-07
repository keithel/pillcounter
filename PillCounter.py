# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QmlElement

import os
import imghdr

QML_IMPORT_NAME = "io.qt.dev"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PillCounter(QObject):
    image_format_changed = Signal()
    image_path_changed = Signal()
    pill_count_changed = Signal()

    def __init__(self):
        super().__init__()
        self._image_format = "None"
        self._image_path = ""
        self._pill_count = -1

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
        # Kick off work to count pills

    def get_pill_count(self):
        return self._pill_count

    def set_pill_count(self, pill_count):
        self._pill_count = pill_count
        self.pill_count_changed.emit()

    image_format = Property(str, get_image_format, notify=image_format_changed)
    image_path = Property(str, get_image_path, set_image_path,
                          notify=image_path_changed)
    pill_count = Property(int, get_pill_count, notify=pill_count_changed)
