class AdditionalKeysCollection:
    def __init__(self):
        self.additionalKeys = []

    def __dict__(self):
        return self.Get()

    def Remove(self, key):
        for el in self.additionalKeys:
            if el.key == key:
                self.additionalKeys.remove(el)
                return True

    def Add(self, key):
        self.additionalKeys.append(key)

    def Get(self):
        return self.additionalKeys
