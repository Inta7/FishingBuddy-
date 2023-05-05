from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QLabel
from Src.Helpers.ScreenHelper import Screen
from Src.DTOs.ImageDto import ImageDto
import platform


class ImageDropArea(QLabel):
    droppedImage = None
    changed = Signal(str)

    def __init__(self, parent=None):
        super(ImageDropArea, self).__init__(parent)
        self.__screen = Screen()
        self.setMinimumSize(100, 100)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.clear()

    def setImage(self, image):
        im = self.__screen.ToQImageObject(image)
        self.setPixmap(QPixmap.fromImage(im))

    def dragEnterEvent(self, event):
        self.setText("<drop content>")
        self.setBackgroundRole(QPalette.Highlight)
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasText():
            self.setText(mime_data.text())
            self.setTextFormat(Qt.PlainText)
            self.droppedImage = ImageDto(
                self.__screen.ReadImage(
                    ClearFilePath(
                        mime_data.text())))
            self.setPixmap(QPixmap(ClearFilePath(mime_data.text())))
            self.changed.emit(mime_data.text())
        else:
            self.setText("Cannot display data")

        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.clear()
        event.accept()

    @Slot()
    def clear(self):
        self.setText("<drop image>")
        self.setBackgroundRole(QPalette.Dark)
        self.changed.emit(None)


def ClearFilePath(filepath):
    if platform.system().lower() == "windows":
        return str(filepath).replace("file:///", "")
    else:
        return str(filepath).replace("file://", "")
