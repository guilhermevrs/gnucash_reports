from datetime import date
from decimal import Decimal

from piecash.core.account import Account
from core import TransactionJournalConfig, RawTransactionData
from tests.test_piecash_helper import TestPiecashHelper
from piecash.core.transaction import ScheduledTransaction, Transaction
import pytest
from sqlalchemy.sql.expression import or_
from core import TransactionJournal
from piecash.core.book import Book
from mock_alchemy.mocking import AlchemyMagicMock
from mock_recurrence import MockRecurrence
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()


class TestTransactionJournal:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        self.mockBook = Book()
        self.mockBook.session = AlchemyMagicMock()
        self.testClass = TransactionJournal(self.mockBook)
        yield  # this is where the testing happens
        # Teardown

    def test__get_recorded_transactions(self):
        """should return recorded transactions inside a date range"""
        start_date = date(2021, 9, 10)
        end_date = date(2021, 9, 20)
        self.testClass._get_recorded_transactions(start_date, end_date)

        self.mockBook.session.query.return_value.filter.assert_called_once_with(
            Transaction.post_date >= start_date, Transaction.post_date <= end_date)

    def test__get_scheduled_transactions_filter_candidates(self):
        """should return scheduled transactions enabled inside a date range"""
        start_date = date(2021, 9, 10)
        end_date = date(2021, 9, 20)
        self.testClass._get_scheduled_transactions(start_date, end_date)

        self.mockBook.session.query.return_value.filter.assert_called_once_with(
            ScheduledTransaction.start_date >= start_date,
            ScheduledTransaction.start_date <= end_date,
            or_(ScheduledTransaction.end_date >= end_date,
                ScheduledTransaction.end_date is None),
            ScheduledTransaction.enabled is True
        )

    def test__get_recursive_occurences_monthly_in(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 1
        recurrence.recurrence_period_type = "month"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(
            2021, 10, 12), date(2021, 10, 22)) == [date(2021, 10, 15)]
        assert len(self.testClass._get_recursive_occurences(
            recurrence, date(2023, 7, 12), date(2023, 12, 22))) == 6
        assert self.testClass._get_recursive_occurences(recurrence, date(
            2023, 8, 12), date(2023, 9, 22)) == [date(2023, 8, 15), date(2023, 9, 15)]
        assert self.testClass._get_recursive_occurences(recurrence, date(
            2021, 9, 12), date(2021, 10, 11)) == [date(2021, 9, 15)]
        assert self.testClass._get_recursive_occurences(recurrence, date(
            2020, 9, 12), date(2021, 10, 11)) == [date(2020, 9, 15), date(2021, 9, 15)]
        recurrence.recurrence_mult = 2
        assert self.testClass._get_recursive_occurences(recurrence, date(
            2023, 8, 12), date(2023, 9, 22)) == [date(2023, 8, 15)]

    def test__get_recursive_occurences_monthly_out(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 3
        recurrence.recurrence_period_type = "month"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(
            recurrence, date(2021, 11, 12), date(2021, 12, 22)) == []
        assert self.testClass._get_recursive_occurences(
            recurrence, date(2021, 10, 12), date(2021, 10, 13)) == []

    def test__get_recursive_occurences_yearly_in(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 1
        recurrence.recurrence_period_type = "year"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(
            2021, 10, 12), date(2021, 10, 22)) == [date(2021, 10, 15)]
        assert len(self.testClass._get_recursive_occurences(
            recurrence, date(2020, 10, 12), date(2023, 10, 22))) == 4

    def test__get_recursive_occurences_yearly_out(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 2
        recurrence.recurrence_period_type = "year"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(
            recurrence, date(2020, 10, 12), date(2020, 10, 22)) == []
        assert self.testClass._get_recursive_occurences(
            recurrence, date(2020, 10, 12), date(2021, 10, 13)) == []

    def test__get_raw_transaction_data_empty(self):
        """should return the correct raw data"""
        result = self.testClass._get_raw_transaction_data()
        expected: RawTransactionData = dict([])
        assert result == expected

    def test__get_raw_transaction_data_recorded(self, piecash_helper: TestPiecashHelper):
        """should return the correct raw data"""
        # Single record
        expense = piecash_helper.get_expense_record()
        result = self.testClass._get_raw_transaction_data(recorded=[expense])
        expected: RawTransactionData = dict([
            (date(2021, 9, 15), ([expense], []))
        ])
        assert result == expected

        # Double record, different days
        another_expense = piecash_helper.get_record_previously_scheduled()
        result = self.testClass._get_raw_transaction_data(
            recorded=[expense, another_expense])
        expected: RawTransactionData = dict([
            (date(2021, 9, 15), ([expense], [])),
            (date(2021, 10, 5), ([another_expense], []))
        ])
        assert result == expected

        # Double record, same day
        result = self.testClass._get_raw_transaction_data(
            recorded=[expense, expense])
        expected: RawTransactionData = dict([
            (date(2021, 9, 15), ([expense, expense], []))
        ])
        assert result == expected

    def test__get_raw_transaction_data_scheduled(self, piecash_helper: TestPiecashHelper):
        """should return the correct raw data"""
        # Single scheduled
        scheduled = piecash_helper.get_scheduled_expense()
        result = self.testClass._get_raw_transaction_data(
            scheduled=[(scheduled, [date(2000, 10, 15)])])
        expected: RawTransactionData = dict([
            (date(2000, 10, 15), ([], [scheduled]))
        ])
        assert result == expected

        # Single scheduled, several days
        scheduled = piecash_helper.get_scheduled_expense()
        result = self.testClass._get_raw_transaction_data(
            scheduled=[(scheduled, [date(2000, 10, 15), date(2020, 10, 15)])])
        expected: RawTransactionData = dict([
            (date(2000, 10, 15), ([], [scheduled])),
            (date(2020, 10, 15), ([], [scheduled]))
        ])
        assert result == expected

        # Double scheduled, different days
        another_scheduled = piecash_helper.get_scheduled_only()
        result = self.testClass._get_raw_transaction_data(scheduled=[
            (scheduled, [date(2000, 10, 15)]),
            (another_scheduled, [date(2020, 10, 10)])
        ])
        expected: RawTransactionData = dict([
            (date(2000, 10, 15), ([], [scheduled])),
            (date(2020, 10, 10), ([], [another_scheduled]))
        ])
        assert result == expected

        # Double scheduled, same days
        another_scheduled = piecash_helper.get_scheduled_only()
        result = self.testClass._get_raw_transaction_data(scheduled=[
            (scheduled, [date(2000, 10, 15)]),
            (another_scheduled, [date(2000, 10, 15)])
        ])
        expected: RawTransactionData = dict([
            (date(2000, 10, 15), ([], [scheduled, another_scheduled]))
        ])
        assert result == expected

    def test__get_raw_transaction_data_recorded_and_scheduled(self, piecash_helper: TestPiecashHelper):
        """should return the correct raw data"""
        expense = piecash_helper.get_expense_record()
        scheduled = piecash_helper.get_scheduled_expense()

        result = self.testClass._get_raw_transaction_data(
            recorded=[expense],
            scheduled=[(scheduled, [date(2000, 10, 15)])]
        )
        expected: RawTransactionData = dict([
            (date(2021, 9, 15), ([expense], [])),
            (date(2000, 10, 15), ([], [scheduled]))
        ])
        assert result == expected

        # record, expense, same day

        result = self.testClass._get_raw_transaction_data(
            recorded=[expense],
            scheduled=[(scheduled, [date(2021, 9, 15)])]
        )
        expected: RawTransactionData = dict([
            (date(2021, 9, 15), ([expense], [scheduled]))
        ])
        assert result == expected

    def test__get_account(self):
        """should correctly query for an account"""
        self.testClass._get_account(guid="ThisAccountGuid")

        self.mockBook.session.query.return_value.filter.assert_called_once_with(
            Account.guid == "ThisAccountGuid"
        )

    @patch.object(Account, 'get_balance')
    @patch.object(TransactionJournal, '_get_account')
    @patch.object(TransactionJournal, '_get_raw_transaction_data')
    @patch.object(TransactionJournal, '_get_scheduled_transactions')
    @patch.object(TransactionJournal, '_get_recorded_transactions')
    def test_get_transaction_data(self,
                                  mock__get_recorded_transactions: MagicMock,
                                  mock__get_scheduled_transactions: MagicMock,
                                  mock__get_raw_transaction_data: MagicMock,
                                  mock__get_account: MagicMock,
                                  mock_get_balance: MagicMock,
                                  piecash_helper: TestPiecashHelper):
        """should call the correct internal methods to generate the data"""
        # Arrange
        config = TransactionJournalConfig(checkings_parent_guid="abcdefsdfs")
        cls = TransactionJournal(book=self.mockBook, config=config)

        assert cls._get_recorded_transactions is mock__get_recorded_transactions
        assert cls._get_scheduled_transactions is mock__get_scheduled_transactions
        assert cls._get_raw_transaction_data is mock__get_raw_transaction_data
        assert cls._get_account is mock__get_account

        checkings_account: Account = piecash_helper.get_checkings_account()
        assert checkings_account.get_balance == mock_get_balance

        mock__get_recorded_transactions.return_value = 6666
        mock__get_scheduled_transactions.return_value = 7777
        mock__get_account.return_value = checkings_account
        mock_get_balance.return_value = Decimal(1234560)

        # Act
        data = cls.get_transaction_data(start_date=date(
            2000, 10, 10), end_date=date(2000, 11, 20))

        # Test
        mock__get_recorded_transactions.assert_called_once_with(
            start_date=date(2000, 10, 10), end_date=date(2000, 11, 20))
        mock__get_scheduled_transactions.assert_called_once_with(
            start_date=date(2000, 10, 10), end_date=date(2000, 11, 20))
        mock__get_raw_transaction_data.assert_called_once_with(
            recorded=6666, scheduled=7777)
        mock__get_account.assert_called_once_with(guid="abcdefsdfs")

        assert data.config.opening_date == date(2000, 10, 9)
        assert data.config.opening_balance == Decimal(1234560)
        assert data.config.checkings_parent == "Assets:Checkings"

    @patch.object(Account, 'get_balance')
    @patch.object(TransactionJournal, '_get_account')
    @patch.object(TransactionJournal, '_get_raw_transaction_data')
    @patch.object(TransactionJournal, '_get_scheduled_transactions')
    @patch.object(TransactionJournal, '_get_recorded_transactions')
    def test_get_transaction_data_with_config(self,
                                              mock__get_recorded_transactions: MagicMock,
                                              mock__get_scheduled_transactions: MagicMock,
                                              mock__get_raw_transaction_data: MagicMock,
                                              mock__get_account: MagicMock,
                                              mock_get_balance: MagicMock,
                                              piecash_helper: TestPiecashHelper):
        """should work correctly with configs"""
        # Arrange
        config = TransactionJournalConfig(
            checkings_parent_guid="abcdefsdfs", liabilities_parent_guid="11111111")
        cls = TransactionJournal(book=self.mockBook, config=config)

        checkings_account: Account = piecash_helper.get_checkings_account()
        assert checkings_account.get_balance == mock_get_balance

        mock__get_account.return_value = checkings_account
        mock_get_balance.return_value = Decimal(11223)

        # Act
        data = cls.get_transaction_data(start_date=date(
            2000, 10, 10), end_date=date(2000, 11, 20))

        # Test
        mock__get_account.assert_called_with(guid="11111111")

        assert data.config.opening_date == date(2000, 10, 9)
        assert data.config.opening_liability == Decimal(11223)
