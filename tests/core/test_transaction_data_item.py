from datetime import date
from decimal import Decimal

import pandas as pd
from core.simple_transaction import TransactionType
from core.transaction_data_item import TransactionDataItem
import pytest

from tests.test_piecash_helper import TestPiecashHelper

@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()

class TestTransactionDataItem:

    def test_remove_scheduled_guid(self, piecash_helper: TestPiecashHelper):
        scheduled = [
            piecash_helper.get_scheduled_only(),
            piecash_helper.get_scheduled_already_recorded()
        ]
        recorded = [
            piecash_helper.get_expense_record(),
            piecash_helper.get_expense_record(),
            piecash_helper.get_expense_record(),
            piecash_helper.get_record_previously_scheduled()
        ]

        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)

        assert len(data_item.transactions) == 5

    def test_get_balance_with_expenses(self, piecash_helper: TestPiecashHelper):
        """should return negative balances for expenses"""
        scheduled = []
        recorded = [
            piecash_helper.get_expense_record()
        ]


        # Test a simple record item
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('-50')
        # Test if the balance is zero
        data_item = TransactionDataItem(date(2000, 10, 10), [], [])
        assert data_item.get_balance() == Decimal('0')
        # Test two recorded
        scheduled = []
        recorded = [
            piecash_helper.get_expense_record(),
            piecash_helper.get_expense_record()
        ]
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('-100')
        # Test two scheduled
        scheduled = [
            piecash_helper.get_scheduled_only(),
            piecash_helper.get_scheduled_only()
        ]
        recorded = []
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('-200')
        # Test both
        scheduled = [
            piecash_helper.get_scheduled_only(),
            piecash_helper.get_scheduled_only()
        ]
        recorded = [
            piecash_helper.get_expense_record()
        ]
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('-250')

    def test_get_balance_with_incomes(self, piecash_helper):
        scheduled = [
        ]
        recorded = [
            piecash_helper.get_income_record()
        ]
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('400')
        # Test two recorded
        scheduled = [
        ]
        recorded = [
            piecash_helper.get_income_record(),
            piecash_helper.get_income_record()
        ]
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('800')
        # Test with scheduled
        scheduled = [
            piecash_helper.get_scheduled_income()
        ]
        recorded = []
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('123')
    
    def test_get_balance_with_transfer(self, piecash_helper):
        # Test with recorded
        scheduled = []
        recorded = [
            piecash_helper.get_recorded_transfer()
        ]
        data_item = TransactionDataItem(date(2000, 10, 10), recorded, scheduled)
        assert data_item.get_balance() == Decimal('0')

    def test_get_dataframe(self, piecash_helper: TestPiecashHelper):
        data_item = TransactionDataItem(date(2000,10,10), [], [])

        assert len(data_item.get_dataframe()) == 0

        data_item = TransactionDataItem(date(2000,10,10), [
            piecash_helper.get_recorded_transfer(),
            piecash_helper.get_income_record()
        ], [])
        df = data_item.get_dataframe()
        assert len(df) == 2

        assert len(df.columns) == 8
        assert df['date'][0] == date(2000,10,10)
        assert df['date'][1] == date(2000,10,10)