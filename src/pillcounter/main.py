# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from .ImageProviders import ColorImageProvider, CVImageProvider
from . import PillCounter

def main():
    """Main function to set up and run the Qt application."""
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImageProvider("colors", ColorImageProvider())
    engine.addImageProvider("cv", CVImageProvider.instance())

    # Correct path resolving for QML file when installed as a package
    qml_file = os.fspath(Path(__file__).resolve().parent / "main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
