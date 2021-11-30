from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from core import (
    Balance, BalanceData, TransactionDataItem,
    BalanceType, RawTransactionData, TransactionData,
    TransactionDataConfig)
from tests.test_piecash_helper import TestPiecashHelper
import pytest


@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()


class TestTransactionData:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        yield  # this is where the testing happens
        # Teardown

    def test_load_from_empty_dic(self):
        """should load an object from empty dictionary"""
        dic: RawTransactionData = dict([])
        result = TransactionData.from_rawdata(data=dic)
        assert len(result.items) == 0

    def test_load_from_simple_dic(self, piecash_helper: TestPiecashHelper):
        """should load an object based on a dictionary"""
        recorded_expense = piecash_helper.get_expense_record()
        scheduled_transfer = piecash_helper.get_scheduled_transfer()
        dic: RawTransactionData = dict([
            (date(2000, 10, 10), ([
                recorded_expense
            ], [
                scheduled_transfer
            ]))
        ])
        result = TransactionData.from_rawdata(data=dic)
        assert len(result.items) == 1
        assert len(result.items[0].transactions) == 2

    def test_get_dataframe(self):
        """should return an empty dataframe from an empty object"""
        dic: RawTransactionData = dict([])
        result = TransactionData.from_rawdata(data=dic)

        assert len(result.get_dataframe()) == 0

    def test_get_balance_data_with_config_empty(self):
        """should return the correct balance data for empty object with config"""
        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(
            400), opening_date=date(2000, 11, 10))
        result = TransactionData.from_rawdata(data=dic, config=config)

        df = result.get_balance_data()
        assert len(df) == 1
        assert len(df.columns) == 5
        assert df['type'][0] == BalanceType.CHECKINGS
        assert df['date'][0] == date(2000, 11, 10)
        assert df['diff'][0] == Decimal(0)
        assert df['balance'][0] == Decimal(400)

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data_with_no_scheduled(self, mock_get_balance: MagicMock):
        """should return the balance data when we have only the open config"""
        checkings = Balance(recorded=Decimal(-1000), scheduled=Decimal(-1000))
        mock_get_balance.return_value = BalanceData(checkings=checkings)

        dic: RawTransactionData = dict([])
        result = TransactionData.from_rawdata(data=dic)

        result.items = [
            TransactionDataItem.from_transactions(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 1
        assert len(df.columns) == 5

        assert df['date'][0] == date(2000, 10, 10)
        assert df['type'][0] == BalanceType.CHECKINGS
        assert df['diff'][0] == Decimal(-1000)
        assert df['balance'][0] == Decimal(-1000)
        assert not df['scheduled'][0]

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data_with_config(self, mock_get_balance: MagicMock):
        """should return the balance data for recorded tx + config"""
        checkings = Balance(recorded=Decimal(-1000), scheduled=Decimal(-1000))
        mock_get_balance.return_value = BalanceData(checkings=checkings)

        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(
            2300), opening_date=date(2000, 11, 10))
        result = TransactionData.from_rawdata(data=dic, config=config)

        result.items = [
            TransactionDataItem.from_transactions(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 2

        assert df['date'][0] == date(2000, 11, 10)
        assert df['diff'][0] == Decimal(0)
        assert df['balance'][0] == Decimal(2300)
        assert not df['scheduled'][0]

        assert df['date'][1] == date(2000, 10, 10)
        assert df['diff'][1] == Decimal(-1000)
        assert df['balance'][1] == Decimal(1300)
        assert not df['scheduled'][1]

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data_with_checkings_config(self, mock_get_balance: MagicMock):
        """should indicate to the transaction items the checkings parent account"""
        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(
            2300), opening_date=date(2000, 11, 10), checkings_parent="MY_CHECKINGS")
        result = TransactionData.from_rawdata(data=dic, config=config)

        result.items = [
            TransactionDataItem.from_transactions(date(2000, 10, 10), [], [])
        ]

        result.get_balance_data()

        mock_get_balance.assert_called_with(checkings_parent="MY_CHECKINGS")

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data_with_scheduled(self, mock_get_balance: MagicMock):
        """should return correct balance data when having scheduled data"""
        checkings = Balance(recorded=Decimal(-1000), scheduled=Decimal(-5000))
        mock_get_balance.return_value = BalanceData(checkings=checkings)

        dic: RawTransactionData = dict([])
        result = TransactionData.from_rawdata(data=dic)

        result.items = [
            TransactionDataItem.from_transactions(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 2

        assert df['date'][0] == date(2000, 10, 10)
        assert df['diff'][0] == Decimal(-1000)
        assert df['balance'][0] == Decimal(-1000)
        assert not df['scheduled'][0]

        assert df['date'][1] == date(2000, 10, 10)
        assert df['diff'][1] == Decimal(-5000)
        assert df['balance'][1] == Decimal(-6000)
        assert df['scheduled'][1]

    @patch.object(TransactionDataItem, 'get_balance')
    def test_get_balance_data_with_liability(self, mock_get_balance: MagicMock):
        """should return the correct balance for liability"""
        liability = Balance(recorded=Decimal(1000), scheduled=Decimal(5000))
        mock_get_balance.return_value = BalanceData(liability=liability)

        dic: RawTransactionData = dict([])
        result = TransactionData.from_rawdata(data=dic)

        result.items = [
            TransactionDataItem.from_transactions(date(2000, 10, 10), [], [])
        ]

        df = result.get_balance_data()

        assert len(df) == 2

        assert df['date'][0] == date(2000, 10, 10)
        assert df['diff'][0] == Decimal(1000)
        assert df['balance'][0] == Decimal(1000)
        assert not df['scheduled'][0]
        assert df['type'][0] == BalanceType.LIABILITIES

        assert df['date'][1] == date(2000, 10, 10)
        assert df['diff'][1] == Decimal(5000)
        assert df['balance'][1] == Decimal(6000)
        assert df['scheduled'][1]
        assert df['type'][0] == BalanceType.LIABILITIES

    def test_get_balance_data_with_open_liability(self):
        """should return the correct balance when setting opening balance for liability"""
        dic: RawTransactionData = dict([])
        config = TransactionDataConfig(opening_balance=Decimal(
            2300), opening_date=date(2000, 11, 10), opening_liability=Decimal(5000))
        result = TransactionData.from_rawdata(data=dic, config=config)

        df = result.get_balance_data()
        assert len(df) == 2

        assert df['date'][1] == date(2000, 11, 10)
        assert df['diff'][1] == Decimal(0)
        assert df['balance'][1] == Decimal(5000)
        assert not df['scheduled'][1]
        assert df['type'][1] == BalanceType.LIABILITIES