import unittest
from json_serializer import JsonDeserializer
import json

class Assert:
    def __init__(self, data: str):
        current = json.loads(data)
        applicant = JsonDeserializer().deserialize(data)
        TestDeserializeMethods().assertEquals(json.dumps(applicant), json.dumps(current))


class Fail:
    def __init__(self, data: str):
        current, applicant = None, None
        try:
            json.loads(data)
        except:
            current = True
        try:
            JsonDeserializer().deserialize(data)
        except:
            applicant = True
        TestDeserializeMethods().assertEquals(applicant, current)


# Опора на https://jsonlint.com/
class TestDeserializeMethods(unittest.TestCase):
    # TODO: написать тесты для сценариев с невалидной JSON
    def test_simple(self):
        # по умолчанию не умеет, а наш умеет
        #Assert('')

        Assert('1234')
        Assert('"dfsfsdfsdfsdf"')
        Assert('null')
        Assert('true')
        Assert('false')
        Fail('False')
        Fail('True')
        Fail('NULL')
        Fail('true')
    
    def test_dict(self):
        Assert('{}')
        Assert('{"a":1,   "b123s": 23       ,   "csd3":     12}')
        Assert('{\
                    "a":1,   \
                    "b123s": 23       ,\
                    "csd3":     12\
               }')
        Assert('''{
            "glossary": {
                "title": "example glossary",
                "GlossDiv": {
                    "title": "S",
                    "GlossList": {
                        "GlossEntry": {
                            "ID": "SGML",
                            "SortAs": "SGML",
                            "GlossTerm": "Standard Generalized Markup Language",
                            "Acronym": "SGML",
                            "Abbrev": "ISO 8879:1986",
                            "GlossDef": {
                                "para": "A meta-markup language, used to create markup languages such as DocBook.",
                                "GlossSeeAlso": ["GML", "XML"]
                            },
                            "GlossSee": "markup"
                        }
                    }
                }
            }
        }
''')

    def test_array(self):
        Assert('[]')
        Assert('[1,2,3]')
        Assert('[1,"dsdsf}",[1,2,3]]')
        Assert('{"a":1, "b": {}, "c":[1,2,3]}')

    def null_bool(self):
        Assert('{"test": null, "t2": true,     "t3"   : false}')

if __name__ == '__main__':
    unittest.main()