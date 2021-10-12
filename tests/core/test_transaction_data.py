from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from piecash.core.transaction import Transaction
from core.simple_transaction import SimpleTransaction
from core.transaction_data_item import TransactionDataItem
from core.typings import RawTransactionData
from tests.test_piecash_helper import TestPiecashHelper
from core.transaction_data import TransactionData, TransactionDataConfig
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

    def test_get_dataframe(self):
        dic: RawTransactionData = dict([])
        result = TransactionData(data=dic)

        assert len(result.get_dataframe()) == 0

    def test_get_balance_data_with_config(self):
        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(400), opening_date=date(2000,11,10))
        result = TransactionData(data=dic, config=config)

        df = result.get_balance_data()
        assert len(df) == 1
        assert df['date'][0] == date(2000,11,10)
        assert df['diff'][0] == Decimal(0)
        assert df['balance'][0] == Decimal(400)


    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data(self, mock_get_balance: MagicMock):
        mock_get_balance.return_value = Decimal(-1000)

        dic: RawTransactionData = dict([])
        result = TransactionData(data=dic)

        result.items = [
            TransactionDataItem(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 1
        assert len(df.columns) == 3

        assert df['date'][0] == date(2000,10,10)
        assert df['diff'][0] == Decimal(-1000)
        assert df['balance'][0] == Decimal(-1000)

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data(self, mock_get_balance: MagicMock):
        mock_get_balance.return_value = Decimal(-1000)

        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(2300), opening_date=date(2000,11,10))
        result = TransactionData(data=dic, config=config)

        result.items = [
            TransactionDataItem(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 2

        assert df['date'][1] == date(2000,10,10)
        assert df['diff'][1] == Decimal(-1000)
        assert df['balance'][1] == Decimal(1300)