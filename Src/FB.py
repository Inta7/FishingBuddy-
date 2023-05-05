import time
import pyautogui

from Src.DTOs.AdditionalKeysCollection import AdditionalKeysCollection
from Src.Exceptions.PatternImageNotFound import PatternImageNotFound
from Src.Helpers.Logger import Logger
from Src.Helpers.ScreenHelper import Screen
from Src.Helpers.SystemHelper import System
import datetime


class FishingBuddy:
    __wowProcessName = ["wow", "world of warcraft"]

    def __init__(self, logger: Logger):
        self.__screen = Screen()
        self.__system = System()
        self.__initialKey = None
        self.__imageDiffTrigger = None
        self.__templateImage = None
        self.__cancelToken = None
        self.__innerFrameSize = None
        self.__additionalKeys = AdditionalKeysCollection()
        self.__additionalKeysTime = {}
        self.logger = logger
        self.CalculateInnerFrameSize()

    def CalculateInnerFrameSize(self):
        resolutionInfo = self.__screen.GetScreenResolution()
        pureSize = 100
        pureH = 900
        pureW = 1440
        currentH = (resolutionInfo.height * pureSize) / pureH
        currentW = (resolutionInfo.width * pureSize) / pureW
        self.__innerFrameSize = int((currentH + currentW) / 2)

    def SetParams(self, initialKey, patternImage, sensValue, additionalKeys: AdditionalKeysCollection):
        self.__initialKey = initialKey
        if patternImage is None:
            self.logger.LogCrit("Image not found")
            raise PatternImageNotFound
        self.__templateImage = patternImage
        self.__imageDiffTrigger = sensValue
        self.__additionalKeys = additionalKeys

    def Start(self, cancellation):
        self.__cancelToken = cancellation
        try:
            while True:
                if self.__cancelToken.is_set():
                    self.logger.LogInfo("Cancelling requested")
                    break
                self.__innerLoop()
                self.logger.LogInfo("Waiting 1 second")
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.LogInfo("Keyboard interrupt pressed - stopping")
            pass

    def TriggerTimeAction(self):
        self.logger.LogInfo("Trying to trigger time action")
        for keysCollection in self.__additionalKeys.Get():
            if keysCollection.time is None or str(keysCollection.time) == "":
                continue
            if self.CheckTime(self.__additionalKeysTime[keysCollection.key] + datetime.timedelta(seconds=keysCollection.time)):
                self.logger.LogInfo(f"Triggering key '{keysCollection.key}'")
                pyautogui.press(keysCollection.key)
                self.__additionalKeysTime[keysCollection.key] = datetime.datetime.now()

    def CheckTime(self, time1):
        return time1 < datetime.datetime.now()

    def SetAdditionalKeysTime(self):
        if self.__additionalKeys is None or type(self.__additionalKeys) is not AdditionalKeysCollection:
            return
        for keyTime in self.__additionalKeys.Get():
            self.__additionalKeysTime[keyTime.key] = datetime.datetime.now()

    def __logDetectedImage(self, counter, image, coordX, coordY):
        self.__screen.DrawRectangle(image, coordX, coordY, self.__innerFrameSize)
        self.__screen.WriteImage(image, "tryImage" + str(counter) + ".png")

    def CheckProcess(self):
        windowFound = False
        processFound = False
        self.logger.LogInfo("Searching for World of warcraft process")
        for name in self.__wowProcessName:
            processFound = self.__system.ProcessRunning(name)
            if processFound:
                self.logger.LogInfo("Process found")
                break

        if not processFound:
            self.logger.LogInfo("Process not found - going for another loop")
            return False

        self.logger.LogInfo("Searching for World of warcraft current active window")
        for name in self.__wowProcessName:
            windowFound = self.__system.IsActiveWindow(name)
            if windowFound:
                self.logger.LogInfo("Window found")
                break

        if not windowFound:
            self.logger.LogInfo("Window not found - going for another loop")
            return False

        return True

    def __innerLoop(self):
        if not self.CheckProcess():
            return
        try:
            self.SetAdditionalKeysTime()
            self.logger.LogInfo(f"Pressing '{self.__initialKey}' key")
            pyautogui.press(self.__initialKey)  # press fishing key
            self.logger.LogInfo("Waiting 1.5 seconds")
            self.__cancelToken.wait(1.5)  # wait for action
            self.logger.LogInfo("Trying to get object on screen")
            ([coordY], [coordX]), conf, image = self.__screen.GetObjectOnScreenCoordinates(self.__templateImage)
            self.logger.LogInfo(f"Finest object found by template - X:{coordX}, Y:{coordY}, Confidence:{conf}")
            #self.__logDetectedImage(counter, image, coordX, coordY)  # debug
            if conf < 0.5:
                self.logger.LogInfo("Confidence is less than 50% -- going for another loop")
                return

            normX, normY = self.__screen.NormalizeToScreenResolution(coordX, coordY, image)
            self.logger.LogInfo(f"Normalized coordinates - X:{normX}, Y:{normY}")

            self.__awaitAction(normX, normY, 60)

            self.logger.LogInfo(f"Moving cursor to coordinates")
            pyautogui.moveTo(normX, normY, 0.5)
            self.logger.LogInfo(f"Clicking")
            pyautogui.click()  # click
            self.logger.LogInfo(f"Waiting 0.5 seconds")
            self.__cancelToken.wait(0.5)
            self.logger.LogInfo(f"Getting random coordinates for cursor")
            x, y = self.__system.GetRandomXYInsideBoundaries(100, 300, 100, 300)
            self.logger.LogInfo(f"Moving cursor to coordinates")
            pyautogui.moveTo(x, y, 0.5)
            self.TriggerTimeAction()
        except Exception as ex:
            self.logger.LogError(f"Exception in __InnerLoop method: {ex.__str__()}")

    def __awaitAction(self, xCoord, yCoord, timeout):
        try:
            self.logger.LogInfo(f"Starting action detection - timeout: {timeout.__str__()}")
            counter = 0
            while counter < timeout and not self.__cancelToken.is_set():
                first = self.__screen.TakePartScreenshot(
                    xCoord - self.__innerFrameSize/2,
                    yCoord - self.__innerFrameSize/2,
                    self.__innerFrameSize)
                self.__cancelToken.wait(0.08)
                second = self.__screen.TakePartScreenshot(
                    xCoord - self.__innerFrameSize/2,
                    yCoord - self.__innerFrameSize/2,
                    self.__innerFrameSize)

                difValue = self.__screen.FindDifferenceBetweenImages(first, second)
                self.logger.LogInfo("Difference - " + str(difValue))
                counter = counter + 1
                if difValue < self.__imageDiffTrigger:
                    self.logger.LogInfo("Found action - breaking loop")
                    break
                self.logger.LogInfo(f"Difference is less than {self.__imageDiffTrigger*100}%")
        except Exception as ex:
            self.logger.LogError(f"Exception in __awaitAction method: {ex.__str__()}")
