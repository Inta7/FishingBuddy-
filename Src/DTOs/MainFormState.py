from Src.DTOs.AdditionalKeysCollection import AdditionalKeysCollection
from Src.DTOs.ButtonToPress import ButtonToPress
from Src.Helpers.Logger import LogLevel


class MainFormState:
    def __init__(self, fishingKey, sensValue, imagePath, logLevel: LogLevel, buttonsToPress: AdditionalKeysCollection):
        self.fishingKey = fishingKey
        self.sensitivityValue = sensValue
        self.imagePath = imagePath
        self.logLevel = logLevel
        self.buttonsToPress = buttonsToPress

    @staticmethod
    def Deserialize(data):
        return MainFormState(
            MainFormState.__defaultIfNone(data.get('"fishingKey"'), "1"),
            MainFormState.__defaultIfNone(data.get('"sensitivityValue"'), 0.5),
            MainFormState.__defaultIfNone(data.get('"imagePath"'), None),
            MainFormState.__defaultIfNone(data.get('"logLevel"'), LogLevel.System),
            MainFormState.__deserializeAdditionalKeysCollection(data.get('"buttonsToPress"')))

    @staticmethod
    def __deserializeAdditionalKeysCollection(data):
        result = AdditionalKeysCollection()
        for dict in data:
            result.Add(ButtonToPress(dict.get('"key"'), dict.get('"time"')))
        return result

    @staticmethod
    def __defaultIfNone(value, default):
        if value is None:
            return default
        return value
