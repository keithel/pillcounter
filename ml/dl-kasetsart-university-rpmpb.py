from roboflow import Roboflow
rf = Roboflow(api_key="TQJtB5of6Xvl2SKdjhbV")
project = rf.workspace("kasetsart-university-rpmpb").project("pills-pills")
version = project.version(3)
dataset = version.download("yolov8")
