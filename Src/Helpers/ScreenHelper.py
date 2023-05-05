from PIL import ImageGrab, Image, ImageQt
from screeninfo import get_monitors

from Src.Helpers.NumbersHelper import Numbers
from skimage.metrics import structural_similarity
from io import BytesIO
import base64
import numpy as np
import cv2


class Screen:
    __numbersHelper = None

    def __init__(self):
        self.__numbersHelper = Numbers()

    def GetObjectOnScreenCoordinates(self, template):
        screens = []

        for i in range(0, 2):
            screens.append(self.TakeScrenShot())

        results = []

        for image in screens:
            res, conf, image = self.__confidence(image, template)
            results.append((res, conf, image))

        results.sort(key=lambda x: x[1], reverse=True)

        return results[0]

    def NormalizeToScreenResolution(self, coordX, coordY, screen):
        trows, tcols = screen.shape[:2]
        resolutionInfo = self.GetScreenResolution()
        monitorRows = resolutionInfo.height
        monitorCols = resolutionInfo.width
        return coordX / (tcols / monitorCols), coordY / (trows / monitorRows) + 25

    def GetScreenResolution(self):
        for m in get_monitors():
            if m.is_primary:
                return m

    def TakeScrenShot(self):
        snap = ImageGrab.grab()
        return np.array(snap)

    #  left, top, right, bottom = bbox
    def TakePartScreenshot(self, left, top, size):
        intValLeft = self.__numbersHelper.NumberOrZero(int(left))
        intValTop = self.__numbersHelper.NumberOrZero(int(top))

        print("Trying to take screenshot")
        print("Left " + str(intValLeft))
        print("Top " + str(intValTop))
        snapshot = ImageGrab.grab(bbox=(intValLeft,
                                        intValTop,
                                        intValLeft + size,
                                        intValTop + size))
        return np.array(snapshot)

    def FindDifferenceBetweenImages(self, firstImage, secondImage):
        # Convert images to grayscale
        before_gray = cv2.cvtColor(firstImage, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(secondImage, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the two images
        score = structural_similarity(before_gray, after_gray, full=False)
        return score

    def ReadImageFromBase64(self, base64Str):
        return Image.open(BytesIO(base64.b64decode(base64Str)))

    def ReadImage(self, imageName):
        img = Image.open(imageName)
        return np.array(img)

    def ToQImageObject(self, image: Image):
        return ImageQt.ImageQt(image)

    def DrawRectangle(self, image, x, y, size):
        cv2.rectangle(image, (x, y), (x + size, y + size), (0, 0, 255), 2)

    def WriteImage(self, image, imageName):
        cv2.imwrite(imageName, image)

    def __confidence(self, image, template):
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(np.array(template), cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(grayImage, template, cv2.TM_CCOEFF_NORMED)
        conf = res.max()
        return np.where(res == conf), conf, image
