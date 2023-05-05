from enum import Enum
from PySide6.QtCore import Signal, QObject
from datetime import datetime


class LogLevel(Enum):
    System = 0
    Info = 1
    Error = 2
    Crit = 3

    @staticmethod
    def toListNames():
        return [LogLevel.System.name,
                LogLevel.Info.name,
                LogLevel.Error.name,
                LogLevel.Crit.name]
    @staticmethod
    def toList():
        return [LogLevel.System,
                LogLevel.Info,
                LogLevel.Error,
                LogLevel.Crit]

    @staticmethod
    def FromInt(value):
        return LogLevel.toList()[value]

    @staticmethod
    def FromString(value):
        return LogLevel[value]

    def __dict__(self):
        return self.name


class LogDto:
    def __init__(self, text: str, level: LogLevel):
        self.text = text
        self.datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.logLevel = level

    def __str__(self):
        return f"[{self.logLevel.name}] [{self.datetime}] {self.text}"


class Logger(QObject):
    logAppended = Signal(LogDto)

    def __init__(self, minimumLogLevel: LogLevel):
        super().__init__()
        self.minimumLogLevel = minimumLogLevel

    def SetMinimumLogLevel(self, level: LogLevel):
        if type(level) is int:
            self.minimumLogLevel = LogLevel.FromInt(level)
        elif type(level) is str:
            self.minimumLogLevel = LogLevel.FromString(level)
        else:
            self.minimumLogLevel = level
        self.Log(f"Minimum log level set to {self.minimumLogLevel.name}")

    def Log(self, text, level: LogLevel = LogLevel.System):
        logDto = LogDto(text, level)
        self.logAppended.emit(logDto)

    def LogError(self, text):
        if self.minimumLogLevel.value <= LogLevel.Error.value:
            self.Log(text, LogLevel.Error)

    def LogInfo(self, text):
        if self.minimumLogLevel.value <= LogLevel.Info.value:
            self.Log(text, LogLevel.Info)

    def LogCrit(self, text):
        if self.minimumLogLevel.value <= LogLevel.Crit.value:
            self.Log(text, LogLevel.Crit)

