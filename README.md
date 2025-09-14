# PillCounter

A PySide6 and OpenCV application to count pills from a camera feed.


# Machine learning models:
https://universe.roboflow.com/bhavin-mami4/pill-scanner
https://universe.roboflow.com/kasetsart-university-rpmpb/pills-pills

kasetsart-university-rpmpb selected.
To build the model, first download the training data. Roboflow created a Jupyter
script to download this that I have put in the `ml` dir.
Run:
```
python ml/dl-kasetsart-university-rpmpb.py
```

Next, train the yolov8 model on the kasetsart-university-rpmpb dataset.
`Pills-Pills-3` is the output directory created by the downloader script:
```
python yolov8_train.py Pills-Pills-3
```

## Converting pytorch model to TensorFlow Lite

The following converts the pytorch model to a tensorflow lite model
`yolo export model=runs/detect/pill_training3/weights/best.pt format=tflite`

## Installing models for use by the application

1. Run the above machine learning scripts, including the coversion from PyTorch to TensorFlow Lite.
2. Link or copy the `best.pt` and `best_float32.tflite` model files into the `src/pillcounter`
   directory.
