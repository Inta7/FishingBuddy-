import numpy as np
from PIL import Image
from Src.Exceptions.NotSupportedImageType import NotSupportedImageType


class ImageDto:
    __innerImageArray = None

    def __init__(self, image):
        if type(image) is np.ndarray:
            self.__innerImageArray = image
        elif type(image) is Image:
            self.__innerImageArray = np.array(image)
        else:
            raise NotSupportedImageType

    def GetImage(self):
        return self.__innerImageArray