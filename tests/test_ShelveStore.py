# encoding = utf-8

import unittest
import os
import sys
import uuid
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import Helper
from ShelveStore import ShelveStore

class TestShelveStore(unittest.TestCase):

    def test_get_set_get_value(self):
        value = str(uuid.uuid4())
        cache_path = "./cache"
        key_name = "guid"
        cache = ShelveStore(db_path=cache_path)
        cache.set_parameter(key_name, value)

        self.assertEqual(value, cache.get_parameter(key_name))
        del cache


        cache2 =  ShelveStore(db_path=cache_path)
        self.assertEqual(value, cache2.get_parameter(key_name))
    
    def test_unexisting_key(self):
        cache_path = "./cache"
        key_name = "guid"
        cache = ShelveStore(db_path=cache_path)
        value = None
        try:
            value = cache.get_parameter(key_name)
        except KeyError:
            pass


    
if __name__ == '__main__':
    load_dotenv()
    unittest.main()
