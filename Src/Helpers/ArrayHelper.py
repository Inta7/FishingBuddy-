class Array:
    @staticmethod
    def find(array, predicate):
        for item in array:
            if predicate(item):
                return item
        return None