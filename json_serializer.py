from enum import Enum

class JsonFieldType(Enum):
    Array = 1
    Json = 2
    BLUE = 3

# Опора на https://jsonlint.com/
class JsonDeserializer:
    """
    Диссериализация Json -> object
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
            else:
                raise ValueError(f'Неожиданный символ')
                #raise ValueError(f'Невалидный JSON')
        self._skip_spaces()
        return obj
    
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
