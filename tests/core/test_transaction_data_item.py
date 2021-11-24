from datetime import date
from decimal import Decimal

from core import TransactionDataItem
import pytest

from tests.test_piecash_helper import TestPiecashHelper


@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()


class TestTransactionDataItem:

    def test_remove_scheduled_guid(self, piecash_helper: TestPiecashHelper):
        """
        should filter the scheduled that are already recorded
        """
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

        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)

        assert len(data_item.transactions) == 5

    def test_get_balance_with_expenses(self, piecash_helper: TestPiecashHelper):
        """should return negative balances for expenses (scheduled and or recorded)"""
        scheduled = []
        recorded = [
            piecash_helper.get_expense_record()
        ]

        # Test a simple record item
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.recorded == Decimal('-50')
        assert balance.checkings.scheduled == Decimal(-50)
        # Test if the balance is zero
        data_item = TransactionDataItem(date(2000, 10, 10), [], [])
        balance = data_item.get_balance()
        assert balance.checkings is None
        # Test two recorded
        scheduled = []
        recorded = [
            piecash_helper.get_expense_record(),
            piecash_helper.get_expense_record()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.recorded == Decimal('-100')
        assert balance.checkings.scheduled == Decimal('-100')
        # Test two scheduled
        scheduled = [
            piecash_helper.get_scheduled_only(),
            piecash_helper.get_scheduled_only()
        ]
        recorded = []
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.scheduled == Decimal('-200')
        assert balance.checkings.recorded == Decimal(0)
        # Test both
        scheduled = [
            piecash_helper.get_scheduled_only(),
            piecash_helper.get_scheduled_only()
        ]
        recorded = [
            piecash_helper.get_expense_record()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.recorded == Decimal(-50)
        assert balance.checkings.scheduled == Decimal('-250')

    def test_get_balance_with_incomes(self, piecash_helper):
        """
        Should return positive balances for income (scheduled / recorded)
        """
        scheduled = [
        ]
        recorded = [
            piecash_helper.get_income_record()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.recorded == Decimal('400')
        assert balance.checkings.scheduled == Decimal(400)
        # Test two recorded
        scheduled = [
        ]
        recorded = [
            piecash_helper.get_income_record(),
            piecash_helper.get_income_record()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.recorded == Decimal('800')
        assert balance.checkings.scheduled == Decimal('800')
        # Test with scheduled
        scheduled = [
            piecash_helper.get_scheduled_income()
        ]
        recorded = []
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings.scheduled == Decimal('123')
        assert balance.checkings.recorded == Decimal('0')

    def test_get_balance_with_transfer_no_account(self, piecash_helper):
        """should not consider transfers to accounts we don't care"""
        # Test with recorded
        scheduled = []
        recorded = [
            piecash_helper.get_recorded_transfer()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance()
        assert balance.checkings is None

    def test_get_balance_with_transfer_with_account(self, piecash_helper):
        """should handle the transfers when we have a checkings account"""
        # Test with recorded
        scheduled = []
        recorded = [
            piecash_helper.get_recorded_transfer()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)
        balance = data_item.get_balance(checkings_parent="Assets:Checkings")
        assert balance.checkings.recorded == Decimal('-666')
        assert balance.checkings.scheduled == Decimal('-666')

        balance = data_item.get_balance(checkings_parent="Assets:Savings")
        assert balance.checkings.recorded == Decimal('666')
        assert balance.checkings.scheduled == Decimal('666')

        balance = data_item.get_balance(checkings_parent="Assets")
        assert balance.checkings is None

    def test_get_balance_with_recorded_liabilities(self, piecash_helper: TestPiecashHelper):
        """should consider consider a balance for liability, with positive balance"""
        scheduled = []
        recorded = [
            piecash_helper.get_recorded_liability()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)

        balance = data_item.get_balance()
        assert balance.liability.recorded == Decimal(100)

    def test_get_balance_with_recorded_quittances(self, piecash_helper: TestPiecashHelper):
        """should consider quittance as reducing balance for liability"""
        scheduled = []
        recorded = [
            piecash_helper.get_credit_card_record()
        ]
        data_item = TransactionDataItem(
            date(2000, 10, 10), recorded, scheduled)

        balance = data_item.get_balance()
        assert balance.liability.recorded == Decimal(-50)
        assert balance.checkings.recorded == Decimal(-50)

    def test_get_dataframe(self, piecash_helper: TestPiecashHelper):
        """should return the correct dataframe"""
        data_item = TransactionDataItem(date(2000, 10, 10), [], [])

        assert len(data_item.get_dataframe()) == 0

        data_item = TransactionDataItem(date(2000, 10, 10), [
            piecash_helper.get_recorded_transfer(),
            piecash_helper.get_income_record()
        ], [])
        df = data_item.get_dataframe()
        assert len(df) == 2

        assert len(df.columns) == 9
        assert df['date'][0] == date(2000, 10, 10)
        assert df['date'][1] == date(2000, 10, 10)
