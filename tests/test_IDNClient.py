# encoding = utf-8

import unittest
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import Helper
from IDNClient import IDNClient

class TestIDNClient(unittest.TestCase):
    def setUp(self):
        self.client_id = os.getenv("IDN_CLIENT_ID")
        self.client_secret = os.getenv("IDN_CLIENT_SECRET")
        self.org_name = os.getenv("IDN_TENANT")
        helper = Helper.Helper
        self.client = IDNClient(
            self.org_name, self.client_id, self.client_secret, helper=helper)

    def test_get_access_token(self):
        access_token = self.client.get_access_token()
        self.assertIsNotNone(access_token, "accesstoken not None")
        self.assertNotEqual(access_token, "", "accesstoken not empty")
        # print(f"access_token={access_token}")

    def test_get_audit(self):
        count = 0
        results = self.client.search(query="created:[2021-06-25 TO 2021-06-28]")
        for event in results:
            count += 1

        self.assertGreater(count, 0)
        print(f"count={count}")


if __name__ == '__main__':
    load_dotenv()
    unittest.main()
