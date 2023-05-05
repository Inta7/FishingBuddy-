from Src.GUI.MainWindow import MainWindow
from PySide6 import QtWidgets, QtGui
import sys


class App:
    def __init__(self, directory):
        app = QtWidgets.QApplication([])
        app.setWindowIcon(QtGui.QIcon('appicon.jpg'))
        app.setApplicationName("Fishing buddy")
        mainWindow = MainWindow(directory)
        mainWindow.show()
        sys.exit(app.exec())
