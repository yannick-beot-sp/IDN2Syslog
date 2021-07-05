# encoding = utf-8

import unittest
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from StoreFactory import StoreFactory

class TestStoreFactory(unittest.TestCase):

    def test_get_store(self):
        store = StoreFactory().get_store()
        self.assertIsNotNone(store)



    
if __name__ == '__main__':
    # load_dotenv()
    os.environ['CACHE_PATH'] = "./cache"
    unittest.main()
