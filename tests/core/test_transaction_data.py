from datetime import date
from tests.test_piecash_helper import TestPiecashHelper
import pytest

@pytest.fixture(autouse=True, scope="class")
def piecash_helper():
    return TestPiecashHelper()

class TestTransactionData:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        yield # this is where the testing happens
        # Teardown

    def test_load_from_empty_dic(self):
        dic = {}
        dic[date(2000, 10, 10)] = [[], []]
