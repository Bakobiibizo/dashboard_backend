import pytest
import unittest
from unittest.mock import patch

from generate.get_all_balance import get_balance_map, get_staketo_map, get_stakefrom_map, get_balance, get_staketo, get_stakefrom, get_all_balances


class TestGetAllBalances(unittest.TestCase):
    def setUp(self):
        self.REPORT_MAP = {
            "test": "tests/test.json"
        }
        
    def test_get_balance_map(self):
        with open("tests/test.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert get_balance_map() == data