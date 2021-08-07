# This Python file uses the following encoding: utf-8
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QColor, QImage

import cv2
from PySide6.QtCore import Qt


def QImage_from_cv_image(cv_img):
    """Convert from an opencv image to QImage"""
    # https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1
    cv_height, cv_width, cv_channels = cv_img.shape
    bytes_per_line = cv_width * cv_channels
    return QImage(cv_img.data, cv_width, cv_height, bytes_per_line,
                  QImage.Format_BGR888)


class ColorImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)

    def requestPixmap(self, id, size, requestedSize):
        width = 100
        height = 50

        if size is not None:
            size = QSize(width, height)
        if requestedSize.width() > 0:
            width = requestedSize.width()
        if requestedSize.height() > 0:
            height = requestedSize.height()

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(id).rgba())
        return pixmap


class CVImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Image)

    def requestImage(self, id, size, requestedSize):
        print(f"requestImage(self, {id}, {str(size)}, {str(requestedSize)}")
        cv_image = cv2.imread(id)
        qimage = QImage_from_cv_image(cv_image)

        if size is not None:
            size.setWidth(qimage.width())
            size.setHeight(qimage.height())

        if requestedSize != size:
            width = size.width()
            if requestedSize.width() > 0:
                width = requestedSize.width()
            height = size.height()
            if requestedSize.height() > 0:
                height = requestedSize.height()
            qimage = qimage.scaled(width, height,
                                   Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation)

        return qimage
