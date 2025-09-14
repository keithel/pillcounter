# PillCounter

A PySide6 and OpenCV application to count pills from a camera feed.


# Machine learning models:
https://universe.roboflow.com/bhavin-mami4/pill-scanner
https://universe.roboflow.com/kasetsart-university-rpmpb/pills-pills


# ML model kasetsart-university-rpmpb:

!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="my-api-key")
project = rf.workspace("kasetsart-university-rpmpb").project("pills-pills")
version = project.version(3)
dataset = version.download("yolov8")

