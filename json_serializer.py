from enum import Enum

class JsonFieldType(Enum):
    Array = 1
    Json = 2
    BLUE = 3

class JsonDeserializer:
    """
    Дисериализация Json -> object
    # https://jsonlint.com/
    """

    def __init__(self):
        pass
    
    __ignored_chars = ['\n', ' ', '\r', '\t']

    def _skip_spaces(self):
        while self._index < len(self._text) and self._text[self._index] in self.__ignored_chars:
            self._index += 1
    
    @property
    def _is_finish(self):
        return self._index >= len(self._text)
    
    @property
    def _current(self):
        return self._text[self._index]

    def deserialize(self, _text: str):
        self._text = _text
        self._index = 0

        try:
            value = self._find_next_value()
        except Exception as e:
            raise type(e)(f'Ошибка чтения JSON: {e.args[0]}')
        return value

    def _find_next_value(self):
        obj = None
        self._skip_spaces()
        if not self._is_finish:
            cur = self._current
            if cur.isdigit():
                # число
                obj = self._find_digit()
            elif cur == '\"':
                # строка
                obj = self._find_str()
            elif cur == '{':
                # dict
                obj = self._find_dict()
            elif cur == '[':
                # array
                obj = self._find_array()
            elif cur == 't' or cur == 'f':
                obj = self._find_bool()
            elif cur == 'n':
                obj = self._find_null()
            else:
                raise ValueError(f'Неожиданный символ')
                #raise ValueError(f'Невалидный JSON')
        self._skip_spaces()
        return obj

    def _find_bool(self) -> bool:
        value = True
        if self._current == 't' \
            and (right := self._index + 4) <= len(self._text) \
            and self._text[self._index : right] == 'true':
            self._index += 4
        elif self._current == 'f' \
            and (right := self._index + 5) <= len(self._text) \
            and self._text[self._index : right] == 'false':
            self._index += 5
            value = False
        else:
            raise ValueError('Ожидалось bool')
        
        self._skip_spaces()
        return value
        
    def _find_null(self) -> bool:
        if self._current == 'n' \
            and (right := self._index + 4) <= len(self._text) \
            and self._text[self._index : right] == 'null':
            self._index += 4
        else:
            raise ValueError('Ожидалось null')
        
        self._skip_spaces()
        return None

    def _find_digit(self) -> int:
        value = 0
        if not self._current.isdigit():
            raise ValueError('Expecting \\d')

        while(not self._is_finish):
            cur = self._current
            if cur.isdigit():
                value = value * 10 + int(cur)
            else:
                break
            
            self._index += 1
        
        self._skip_spaces()
        return value
    
    def _find_str(self) -> str:
        if self._current != '\"':
            raise ValueError('Expecting \'"\'')
        self._index += 1
        end = self._text.find('"', self._index)

        if end == -1:
            raise ValueError('Expecting \'"\'')

        result = self._text[self._index: end]
        self._index = end + 1
        self._skip_spaces()
        return result

    def _find_dict(self) -> dict:
        result = {}

        if self._current != '{':
            raise ValueError('Expecting \'{\'')
        self._index += 1
        self._skip_spaces()
        if self._current == '}':
            self._index += 1
            self._skip_spaces()
            return result

        while not self._is_finish:
            field_name = self._find_str()

            if self._is_finish or self._current != ':':
                raise ValueError('Expecting \':\'')
            self._index += 1
            self._skip_spaces()

            field_value = self._find_next_value()
            result[field_name] = field_value

            if self._is_finish or (sep := self._current) not in [',', '}']:
                raise ValueError('Expecting \',\' or \'}\'')           
            
            self._index += 1
            
            if sep == '}':
                break
            # мы не можем закончить на , - ждём ещё ключ
            self._skip_spaces()
            if self._is_finish:
                raise ValueError('Expecting \'"\'')           
        else:
            raise ValueError('Expecting \'}\'')  
        
        self._skip_spaces()
        return result

    def _find_array(self):
        arr = []
        if self._current != '[':
            raise ValueError('Expecting \'[\'')
        self._index += 1
        self._skip_spaces()
        if self._current == ']':
            self._index += 1
            self._skip_spaces()
            return arr

        while(not self._is_finish):
            arr.append(self._find_next_value())
            # дальше, может быть ,
            if self._is_finish or (sep := self._current) not in [',', ']']:
                raise ValueError('Expecting \',\' or \']\'') 
            
            self._index += 1            
            
            if sep == ']':
                break

            self._skip_spaces()
            # нельзя закончить , - ждём следующих элемент
            if self._is_finish:
                raise ValueError('UnExpecting \',\'') 

        else:
            raise ValueError('Expecting \']\'') 
        
        self._skip_spaces()
        return arr

class JsonSerializer:
    """
    Cериализация Json -> object
    # https://jsonformatter.org/
    """

    def __init__(self):
        pass

    def serialize(self, object) -> str:
        """
        Сериализация в JSON
        """
        return self._serialize(object, 0)

    def _serialize(self, object, space_count: int) -> str:
        if isinstance(object, dict):
            return self._dict_serialize(object, space_count)
        elif isinstance(object, list):
            return self._array_serialize(object, space_count)
        elif isinstance(object, str):
            return f'"{object}"'
        elif isinstance(object, bool):
            return 'true' if object else 'false'
        elif object is None:
            return 'null'
        else:
            return str(object)

    def _dict_serialize(self, object: dict, space_count: int) -> str:
        rows = []

        for key, value in object.items():
            rows.append(' '*((space_count+1)*2) + f'"{key}": {self._serialize(value, space_count + 1)}')
        result = ',\n'.join(rows)

        if len(rows) > 0:
            return '{\n' + result + '\n' + ' '*(space_count*2) + '}'
        else:
            return '{}'
        
    def _array_serialize(self, array: dict, space_count: int) -> str:
        rows = []

        for item in array:
            rows.append(' '*((space_count+1)*2) + f'{self._serialize(item, space_count + 1)}')
        result = ',\n'.join(rows)

        if len(rows) > 0:
            return '[\n' + result + '\n' + ' '*(space_count*2) + ']'
        else:
            return '[]'
