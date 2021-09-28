from datetime import date
from tests.test_piecash_helper import TestPiecashHelper
from unittest.mock import MagicMock
from piecash.core.transaction import ScheduledTransaction, Transaction
import pytest
from sqlalchemy.sql.expression import or_
from core import TransactionJournal
from piecash.core.book import Book
from mock_alchemy.mocking import AlchemyMagicMock
from mock_recurrence import MockRecurrence

@pytest.fixture(autouse=True, scope="class")
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
        yield # this is where the testing happens
        # Teardown

    def test_get_recorded_transactions(self):
        """should return recorded transactions inside a date range"""
        start_date = date(2021,9,10)
        end_date = date(2021,9,20)
        self.testClass.get_recorded_transactions(start_date, end_date)
        
        self.mockBook.session.query.return_value.filter.assert_called_once_with(Transaction.post_date >= start_date, Transaction.post_date <= end_date)

    def test_get_scheduled_transactions_filter_candidates(self):
        """should return scheduled transactions enabled inside a date range"""
        start_date = date(2021,9,10)
        end_date = date(2021,9,20)
        self.testClass.get_scheduled_transactions(start_date, end_date)
        
        self.mockBook.session.query.return_value.filter.assert_called_once_with(
            ScheduledTransaction.start_date >= start_date, 
            ScheduledTransaction.start_date <= end_date,
            or_(ScheduledTransaction.end_date >= end_date, ScheduledTransaction.end_date == None),
            ScheduledTransaction.enabled == True
        )

    def test__get_recursive_occurences_monthly_in(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 1
        recurrence.recurrence_period_type = "month"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(2021, 10, 12), date(2021, 10, 22)) == [date(2021, 10, 15)]
        assert len(self.testClass._get_recursive_occurences(recurrence, date(2023, 7, 12), date(2023, 12, 22))) == 6
        assert self.testClass._get_recursive_occurences(recurrence, date(2023, 8, 12), date(2023, 9, 22)) == [date(2023, 8, 15), date(2023, 9, 15)]
        assert self.testClass._get_recursive_occurences(recurrence, date(2021, 9, 12), date(2021, 10, 11)) == [date(2021, 9, 15)]
        assert self.testClass._get_recursive_occurences(recurrence, date(2020, 9, 12), date(2021, 10, 11)) == [date(2020, 9, 15), date(2021, 9, 15)]
        recurrence.recurrence_mult = 2
        assert self.testClass._get_recursive_occurences(recurrence, date(2023, 8, 12), date(2023, 9, 22)) == [date(2023, 8, 15)]

    def test__get_recursive_occurences_monthly_out(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 3
        recurrence.recurrence_period_type = "month"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(2021, 11, 12), date(2021, 12, 22)) == []
        assert self.testClass._get_recursive_occurences(recurrence, date(2021, 10, 12), date(2021, 10, 13)) == []

    def test__get_recursive_occurences_yearly_in(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 1
        recurrence.recurrence_period_type = "year"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(2021, 10, 12), date(2021, 10, 22)) == [date(2021, 10, 15)]
        assert len(self.testClass._get_recursive_occurences(recurrence, date(2020, 10, 12), date(2023, 10, 22))) == 4

    def test__get_recursive_occurences_yearly_out(self):
        """should return the number of occurences exists, given the recurence"""
        recurrence = MockRecurrence()
        recurrence.recurrence_mult = 2
        recurrence.recurrence_period_type = "year"
        recurrence.recurrence_period_start = date(2019, 10, 15)

        assert self.testClass._get_recursive_occurences(recurrence, date(2020, 10, 12), date(2020, 10, 22)) == []
        assert self.testClass._get_recursive_occurences(recurrence, date(2020, 10, 12), date(2021, 10, 13)) == []
