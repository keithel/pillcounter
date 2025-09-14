# ChatGPT never finished providing it's full answer, so some of this is hand
# written.
# ChatGPT prompt: "Show me How I can count the number of identical pills that
#     are in an image with python and PySide6. Please provide controls for
#     changing the gray threshold and morphology iterations, and show the
#     intermediate results in a small window."

import cv2
import numpy as np
import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QFileDialog


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Identical Pills Counter")
        self.setGeometry(100, 100, 800, 600)

        # Create a label to display the image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Create a layout and add the image label to it
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        # Create label to display pill count
        pcl = QLabel()
        self.pill_count_label = pcl
        pcl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pcl.setAlignment(Qt.AlignHCenter)
        pcl_font = pcl.font()
        pcl_font.setPixelSize(50)
        pcl.setFont(pcl_font)
        self.set_pill_count(0)

        # Add the pill count label to the main layout
        layout.addWidget(pcl)

        # Create a slider to adjust the gray threshold
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(128)

        # Create a slider to adjust the morphology iterations
        self.morphology_slider = QSlider(Qt.Horizontal)
        self.morphology_slider.setRange(0, 10)
        self.morphology_slider.setValue(3)

        # Connect the sliders to the update function
        self.threshold_slider.valueChanged.connect(self.update_image)
        self.morphology_slider.valueChanged.connect(self.update_image)

        # Create a layout for the sliders
        sliders_layout = QHBoxLayout()
        sliders_layout.addWidget(QLabel("Gray Threshold:"))
        sliders_layout.addWidget(self.threshold_slider)
        sliders_layout.addWidget(QLabel("Morphology Iterations:"))
        sliders_layout.addWidget(self.morphology_slider)

        # Add the slider count layout to the main layout
        layout.addLayout(sliders_layout)

        # Create a label to display the intermediate results
        self.intermediate_label = QLabel()
        self.intermediate_label.setFixedSize(300, 300)
        self.intermediate_label.setAlignment(Qt.AlignCenter)

        # Add the intermediate label to the main layout
        layout.addWidget(self.intermediate_label)

        # Create a widget to hold the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the main window
        self.setCentralWidget(widget)

        # Load an example image
        image_fn = "pills1.jpg"
        self.image = cv2.imread(image_fn, cv2.IMREAD_COLOR)

        if self.image is None:
            print(f"Failed to load image {image_fn}")
            sys.exit(1)

        # Update and display the image
        self.update_image()

    def set_pill_count(self, pill_count):
        self.pill_count = pill_count
        self.pill_count_label.setText(f"{pill_count} Pills")

    def open_image(self):
        # Open a file dialog to choose an image
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec_():
            filename = file_dialog.selectedFiles()[0]

            # Load the image using OpenCV
            self.image = cv2.imread(filename, cv2.IMREAD_COLOR)

            # Display the image
            self.display_image(self.image)

    def display_image(self, display_image):
        # Convert the image to a QImage and then to a QPixmap
        height, width, channel = display_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_image = q_image.transformed(QTransform().rotate(90))
        q_image_scaled = q_image.scaled(q_image.width() // 4, q_image.height() // 4)
        q_pixmap = QPixmap.fromImage(q_image_scaled)

        # Set the pixmap of the image label
        self.image_label.setPixmap(q_pixmap)

        # Update the intermediate results
        #self.update_image()

    @Slot()
    def update_image(self):
        # Convert the image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, self.threshold_slider.value(), 255,
cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=self.morphology_slider.value())
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=self.morphology_slider.value())

        # Find contours in the image
        contours, hierarchy = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contours_image = np.copy(self.image)
        # Draw the contours on the image and count the number of pills
        pill_count = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 200 and h > 200 and w < 300 and h < 300:  # Only count pills with a certain size
                cv2.drawContours(contours_image, [contour], 0, (0, 255, 0), 2)
                pill_count += 1

        self.set_pill_count(pill_count)
        self.display_image(contours_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pill_window = Window()
    pill_window.show()
    app.exec()
