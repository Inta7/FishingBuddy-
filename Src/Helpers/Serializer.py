from enum import Enum

from Src.DTOs.AdditionalKeysCollection import AdditionalKeysCollection


class Serializer:
    startingSign = '{'
    endingSign = '}'

    @staticmethod
    def Serialize(obj):
        result = []
        for field in obj.__dict__:
            result.append(f'"{field}":{Serializer.SerializeField(obj.__dict__[field])}')
        return f'{Serializer.startingSign}{",".join(result)}{Serializer.endingSign}'

    @staticmethod
    def Deserialize(data):
        result = {}
        data = data[1:-1]
        for field in data.split(','):
            name, value = field.split(':')
            result[name] = Serializer.DeserializeField(value)
        return result

    @staticmethod
    def DeserializeField(data):
        if data[0] == Serializer.startingSign:
            return Serializer.Deserialize(data)
        elif data[0] == '[':
            return Serializer.DeserializeCustomArrayCollection(data)
        elif data[0] == '"':
            return Serializer.DeserializeString(data)
        elif data == 'true':
            return True
        elif data == 'false':
            return False
        elif data == 'null':
            return None
        elif '.' in data:
            return float(data)
        else:
            return int(data)

    @staticmethod
    def DeserializeCustomArrayCollection(data):
        if data == '[]':
            return []
        result = []
        data = data[1:-1]
        for object in data.split('_'):
            semiresult = {}
            for field in object.split(';'):
                field = field.replace(Serializer.startingSign, '')
                field = field.replace(Serializer.endingSign, '')
                name, value = field.split('=')
                semiresult[name] = Serializer.DeserializeField(value)
            result.append(semiresult)
        return result

    @staticmethod
    def DeserializeList(data):
        result = []
        data = data.replace('[', '').replace(']', '')
        for field in data.split(','):
            result.append(Serializer.DeserializeField(field))
        return result

    @staticmethod
    def DeserializeString(data):
        return data.replace('"', '')

    @staticmethod
    def DeserializeNumber(data):
        try:
            return int(data)
        except:
            return float(data)

    @staticmethod
    def SerializeField(field):
        if type(field) is str:
            return f'"{field}"'
        elif type(field) is int:
            return f'{field}'
        elif type(field) is float:
            return f'{field}'
        elif type(field) is bool:
            return f'{field}'
        elif type(field) is list:
            return Serializer.SerializeList(field)
        elif type(field) is dict:
            return Serializer.SerializeDict(field)
        elif type(field) is AdditionalKeysCollection:
            return Serializer.SerializeAdditionalKeysCollection(field)
        elif isinstance(field, Enum):
            return f'"{field.name}"'
        elif field is None:
            return 'null'
        else:
            return Serializer.SerializeObject(field)

    @staticmethod
    def SerializeAdditionalKeysCollection(collection: AdditionalKeysCollection):
        result = []
        for button in collection.Get():
            result.append(f'{{"key"="{button.key}";"time"={button.time}}}')
        return f'[{"_".join(result)}]'

    @staticmethod
    def SerializeList(list):
        result = []
        for item in list:
            result.append(Serializer.SerializeField(item))
        return f'[{",".join(result)}]'

    @staticmethod
    def SerializeDict(dict):
        result = []
        for key in dict:
            result.append(f'"{key}":{Serializer.SerializeField(dict[key])}')
        return f'{{{",".join(result)}}}'

    @staticmethod
    def SerializeObject(obj):
        result = []
        for field in obj.__dict__:
            result.append(f'"{field}":{Serializer.SerializeField(obj.__dict__[field])}')
        return f'{{{",".join(result)}}}'