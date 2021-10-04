from datetime import date
from core.typings import RawTransactionData
from tests.test_piecash_helper import TestPiecashHelper
from core.transaction_data import TransactionData
import pytest

@pytest.fixture(scope="class")
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
        dic: RawTransactionData = dict([])
        result = TransactionData(data=dic)
        assert len(result.items) == 0

    def test_load_from_simple_dic(self, piecash_helper: TestPiecashHelper):
        recorded_expense = piecash_helper.get_expense_record()
        scheduled_transfer = piecash_helper.get_scheduled_transfer()
        dic: RawTransactionData = dict([
            (date(2000, 10, 10), ([
                recorded_expense
            ], [
                scheduled_transfer
            ]))
        ])
        result = TransactionData(data=dic)
        assert len(result.items) == 1
        assert len(result.items[0].transactions) == 2

    def test_filter_by_date(self, piecash_helper: TestPiecashHelper):
        data = TransactionData(data=dict())
        result = data.filter_by_date(start_date=date(2000,10,20), end_date=date(2000,10,20))
        assert len(result) == 0

        recorded_expense = piecash_helper.get_expense_record()
        dic: RawTransactionData = dict([
            (date(2000, 10, 10), ([
                recorded_expense
            ], []))
        ])
        data = TransactionData(data=dic)
        result = data.filter_by_date(start_date=date(2000,10,10), end_date=date(2000,10,20))
        assert len(result) == 1

        result = data.filter_by_date(start_date=date(2000,10,11), end_date=date(2000,10,20))
        assert len(result) == 0