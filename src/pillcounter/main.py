# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import argparse

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from .ImageProviders import ColorImageProvider, CVImageProvider
from . import PillCounter
from . import config

def main():
    """Main function to set up and run the Qt application."""

    parser = argparse.ArgumentParser(description="Pill Counting Application.")
    parser.add_argument(
        '--tflite',
        action='store_true',
        help="Use the TensorFlow Lite model (.tflite) instead of the default PyTorch model (.pt)."
    )
    args = parser.parse_args()

    if args.tflite:
        config.model_name = "best_float32.tflite"
        print(f"Configuration using TensorFlow Lite model ({config.model_name})")
    else:
        print(f"Configuration using PyTorch model ({config.model_name})")

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImageProvider("colors", ColorImageProvider())
    engine.addImageProvider("cv", CVImageProvider.instance())

    # Correct path resolving for QML file when installed as a package
    qml_file = os.fspath(Path(__file__).resolve().parent / "Main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
