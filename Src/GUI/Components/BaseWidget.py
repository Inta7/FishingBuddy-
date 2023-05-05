from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSpacerItem, QSlider, QLabel, QPushButton, QLineEdit


class BaseWidget(QWidget):
    def GroupHorizontally(self, objects):
        layout = QHBoxLayout(self)
        for object in objects:
            if type(object) is QSpacerItem:
                layout.addSpacerItem(object)
            else:
                layout.addWidget(object)
        return layout

    def GetSlider(self, min, max, tick):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickInterval(tick)
        return slider

    def GetLabel(self, labelText):
        label = QLabel(self)
        label.setText(labelText)
        return label

    def GetButton(self, buttonText):
        button = QPushButton(self)
        button.setText(buttonText)
        return button

    def GetNumberOnlyEntry(self):
        onlyInt = QIntValidator()
        onlyInt.setRange(0, 999999999)
        return self.GetEntry(onlyInt)

    def GetEntry(self, validator=None):
        entry = QLineEdit(self)
        if validator is not None:
            entry.setValidator(validator)
        return entry
