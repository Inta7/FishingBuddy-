import os
from threading import Thread, Event
from Src.FB import FishingBuddy
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal
from PySide6.QtWidgets import *
from Src.DTOs.MainFormState import MainFormState
from Src.GUI.Components.AdditionalKeysArea import AdditionalKeysArea, AdditionalKeysCollection
from Src.GUI.Components.BaseWidget import BaseWidget
from Src.GUI.Components.DropArea import ImageDropArea
from Src.GUI.LogWindow import LogWindow
from Src.Helpers.Logger import Logger, LogLevel
from Src.Helpers.ScreenHelper import Screen
from Src.Helpers.Serializer import Serializer


class MainForm(BaseWidget):
    changed = Signal(MainFormState)
    state = None
    imageObject = None
    scriptState = False
    processingThread = None
    startButton = None

    def __init__(self, logger: Logger, logWindow: LogWindow, parent=None):
        super(MainForm, self).__init__(parent)
        self.logger = logger
        self.logger.LogInfo("Initializing main window")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.cancellationEvent = Event()
        self.setWindowTitle("Fishing Buddy")
        self.bot = FishingBuddy(self.logger)
        self.screen = Screen()
        self.logWindow = logWindow
        self.logWindow.logLevelChanged.connect(self.LogLevelChanged)
        self.setMinimumSize(500, 500)
        self.additionalKeysArea = None

    def ComposeLayout(self):
        drop_area = ImageDropArea(self)
        if self.state.imagePath is not None:
            drop_area.setImage(self.screen.ReadImage(self.state.imagePath))
        else:
            drop_area.setImage(self.imageObject)
        drop_area.changed.connect(self.ImageChanged)

        logWindowOpenBtn = self.GetButton("Open logs")
        logWindowOpenBtn.clicked.connect(self.OpenLogWindow)
        self.main_layout.addWidget(logWindowOpenBtn)

        mainLabel = self.GetLabel("Fishing Buddy")
        mainLabel.setFont(QFont("Times New Roman", 35, 1, True))
        fishKeyLabel = self.GetLabel("Fishing key")
        patternLabel = self.GetLabel("Pattern image")
        fishKeyEntry = self.GetNumberOnlyEntry()
        fishKeyEntry.setText(self.state.fishingKey)
        fishKeyEntry.textChanged.connect(self.FishKeyChanged)

        self.startButton = self.GetButton("Start")
        self.startButton.clicked.connect(self.StartButtonPressed)
        self.startButton.setMinimumHeight(100)

        sensLabel = self.GetLabel("Sensitivity")
        sensSlider = self.GetSlider(70, 100, 5)
        sensSlider.setSliderPosition(int(self.state.sensitivityValue*100))
        sensSlider.valueChanged.connect(self.SliderChanged)

        self.additionalKeysArea = AdditionalKeysArea(self)
        self.additionalKeysArea.LoadState(self.state.buttonsToPress)
        self.main_layout.addWidget(mainLabel)
        self.main_layout.addLayout(
            self.GroupHorizontally([sensLabel, sensSlider]))
        self.main_layout.addLayout(
            self.GroupHorizontally([fishKeyLabel, fishKeyEntry]))
        self.main_layout.addLayout(self.additionalKeysArea.GetLayout())
        self.main_layout.addLayout(
            self.GroupHorizontally([patternLabel, drop_area]))
        self.main_layout.addWidget(self.startButton)
        self.additionalKeysArea.changed.connect(self.AdditionalKeysChanged)

    def OpenLogWindow(self):
        self.logger.LogInfo("Opening logs window")
        self.logWindow.show()

    def StartButtonPressed(self):
        if not self.scriptState:
            self.logger.LogInfo("Starting script")
            self.logger.LogInfo(f"Current configuration: {Serializer.Serialize(self.state)}")
            self.bot.SetParams(self.state.fishingKey, self.imageObject, self.state.sensitivityValue, self.state.buttonsToPress)
            self.scriptState = True
            self.processingThread = Thread(target=self.bot.Start, args=(self.cancellationEvent,))
            self.processingThread.start()
            self.startButton.setText("Cancel")
        else:
            self.logger.LogInfo("Stopping script")
            self.cancellationEvent.set()
            self.processingThread.join()
            self.startButton.setText("Start")
            self.scriptState = False
            self.cancellationEvent.clear()

    def AdditionalKeysChanged(self, value: AdditionalKeysCollection):
        self.state.buttonsToPress = value
        self.changed.emit(self.state)

    def ImageChanged(self, value):
        self.state.imagePath = value
        self.changed.emit(self.state)

    def FishKeyChanged(self, value):
        self.state.fishingKey = value
        self.changed.emit(self.state)

    def SliderChanged(self, value):
        self.state.sensitivityValue = value/100
        self.changed.emit(self.state)

    def LogLevelChanged(self, value: LogLevel):
        self.state.logLevel = value.value
        self.changed.emit(self.state)


class MainWindow(QMainWindow):
    configName = "config.json"
    defaultImageBase64 = "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"
    defaultState = MainFormState("2", 0.85, None, LogLevel.Info, [])

    def __init__(self, directory, parent=None):
        super(MainWindow, self).__init__(parent)
        self.logger = Logger(LogLevel.Info)
        self.logWindow = LogWindow(self.logger, self)
        self.form_widget = MainForm(self.logger, self.logWindow, self)
        self.logger.LogInfo("Loading state")
        self.configPath = directory + "/" + self.configName
        self.LoadState()
        self.form_widget.ComposeLayout()
        self.form_widget.changed.connect(self.SaveState)
        self.setCentralWidget(self.form_widget)

    def LoadState(self):
        screenHelper = Screen()
        self.logger.LogInfo(f"Trying to find configuration file in '{self.configPath}'")
        if os.path.exists(self.configPath):
            self.logger.LogInfo("File found")
            file = open(self.configPath, "r")
            data = Serializer.Deserialize(self.MergeText(file.readlines()))
            data = MainFormState.Deserialize(data)
            self.form_widget.state = data
            if data.imagePath is None:
                self.form_widget.imageObject = screenHelper.ReadImageFromBase64(self.defaultImageBase64)
            else:
                self.form_widget.imageObject = screenHelper.ReadImage(data.imagePath)
            self.logger.SetMinimumLogLevel(data.logLevel)
            self.logger.LogInfo(f"Current state: {self.form_widget.state}")
        else:
            self.logger.LogInfo(f"File not found - using default state: {Serializer.Serialize(self.defaultState)}")
            self.form_widget.imageObject = screenHelper.ReadImageFromBase64(self.defaultImageBase64)
            self.form_widget.state = self.defaultState

    def SaveState(self, state: MainFormState):
        self.logger.LogInfo("Saving current state")
        serialized = Serializer.Serialize(state)
        file = open(self.configPath, "w+")
        file.writelines(serialized)
        file.close()

    def MergeText(self, texts):
        result = ""
        for text in texts:
            result = result + text
        return result
