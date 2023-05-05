from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout, QComboBox
from Src.Helpers.Logger import Logger, LogDto, LogLevel


class LogWindow(QDialog):
    logLevelChanged = Signal(LogLevel)

    def __init__(self, logger: Logger, parent):
        super(LogWindow, self).__init__(parent)
        self.logger = logger
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.resize(500, 500)

        self.comboBox = QComboBox(self)
        self.comboBox.addItems(LogLevel.toListNames())
        self.comboBox.currentIndexChanged.connect(self.OnComboBoxChanged)

        self.textBox = QPlainTextEdit(self)
        logger.logAppended.connect(self.LogAppended)

        layout.addWidget(self.comboBox)
        layout.addWidget(self.textBox)

    def OnComboBoxChanged(self, index):
        self.logger.SetMinimumLogLevel(index)
        self.logLevelChanged.emit(LogLevel.FromInt(index))

    def LogAppended(self, logDto: LogDto):
        self.textBox.appendPlainText(logDto.__str__())
