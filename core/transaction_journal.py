"""
Transaction Journal
"""

from dataclasses import dataclass
from datetime import date, timedelta
from piecash.core.account import Account
from piecash.core.book import Book
from piecash.core.transaction import ScheduledTransaction, Transaction
from sqlalchemy import or_
from piecash._common import Recurrence
import calendar
from core.transaction_data import TransactionData, TransactionDataConfig
from core.typings import RawTransactionData

ScheduledTransactionOccurences = tuple[ScheduledTransaction, list[date]]


@dataclass
class TransactionJournalConfig:
    """
    Configurations related to the journal
    """
    checkings_parent_guid: str
    liabilities_parent_guid: str = None


class TransactionJournal:

    def __init__(self, book: Book, config: TransactionJournalConfig = None) -> None:
        self.book = book
        self.config = config
        pass

    def _get_monthly_recursive_occurences(
            self,
            recurrence: Recurrence,
            start_date: date,
            end_date: date) -> list[tuple[int, int]]:
        """Get the monthly occurences as a list of tuple(month, day)"""

        revert = False if (end_date.month >= start_date.month) else True
        same_month = start_date.month == end_date.month

        day = recurrence.recurrence_period_start.day
        month = recurrence.recurrence_period_start.month
        known_months = list()
        occurences = list()
        while month not in known_months:
            known_months.append(month)
            add_occurence = False

            if month == start_date.month or month == end_date.month:
                # If the month is in the border, need to test the day
                if same_month:
                    # If both start and end are the same month, day needs to be in range
                    if day >= start_date.day and day <= end_date.day:
                        add_occurence = True
                else:
                    # Otherwise, each "border" defines the upper or lower bound
                    if month == start_date.month and day >= start_date.day:
                        add_occurence = True
                    elif month == end_date.month and day <= end_date.day:
                        add_occurence = True

            else:
                in_range = month > start_date.month and month < end_date.month
                in_revert_range = month > start_date.month or month < end_date.month
                if (not revert and in_range) or (revert and in_revert_range):
                    add_occurence = True

            if add_occurence:
                occurences.append((month, day))

            month = month + recurrence.recurrence_mult
            if month > 12:
                month = month - 12

        return occurences

    def _get_yearly_recursive_occurences(self, recurrence: Recurrence, start_date: date, end_date: date) -> int:
        """Get the number of occurences, in a year, of the recurrence"""
        year = recurrence.recurrence_period_start.year
        year_occurrences = list()
        while year <= end_date.year:
            if (year >= start_date.year):
                year_occurrences.append(year)
            year = year + recurrence.recurrence_mult

        if len(year_occurrences) == 0:
            return []

        occurences = list()
        monthOccurences = self._get_monthly_recursive_occurences(
            recurrence, start_date, end_date)
        for year in year_occurrences:
            for occ in monthOccurences:
                occurences.append(date(year, occ[0], occ[1]))
        return occurences

    def _get_next_recursive_occurence(self, recurrence: Recurrence, previous_date: date = None):
        if previous_date is None:
            return recurrence.recurrence_period_start

        month = month = previous_date.month
        year = previous_date.year
        day = previous_date.day
        if "month" in recurrence.recurrence_period_type:
            month = month + recurrence.recurrence_mult
            if month > 12:
                month = month - 12
                year = year + 1
            if recurrence.recurrence_period_type == "end_of_month":
                # Get the last day
                range = calendar.monthrange(year, month)
                day = range[1]
        elif "year" == recurrence.recurrence_period_type:
            year = year + recurrence.recurrence_mult
        else:
            raise AttributeError("Unknown '{}' as period of recurrence".format(recurrence.recurrence_period_type))

        try:
            new_date = date(year, month, day)
        except Exception:
            range = calendar.monthrange(year, month)
            new_date = date(year, month, range[1])

        return new_date

    def _get_recursive_occurences(self, recurrence: Recurrence, start_date: date, end_date: date) -> list[date]:
        """Get the list of dates based on the recurrence patterns"""
        occurences = list()

        recursive_it = self._get_next_recursive_occurence(recurrence)
        keep_searching = True
        while keep_searching:
            if recursive_it >= start_date and recursive_it <= end_date:
                occurences.append(recursive_it)
            recursive_it = self._get_next_recursive_occurence(recurrence, recursive_it)
            keep_searching = recursive_it <= end_date

        return occurences

    def _get_raw_transaction_data(
            self,
            recorded: list[Transaction] = [],
            scheduled: list[ScheduledTransactionOccurences] = []) -> RawTransactionData:
        raw_data: RawTransactionData = dict()
        for tr in recorded:
            tr_date = tr.post_date
            if tr_date in raw_data:
                raw_data[tr_date][0].append(tr)
            else:
                raw_data[tr_date] = ([tr], [])

        for occ in scheduled:
            tr = occ[0]
            for tr_date in occ[1]:
                if tr_date in raw_data:
                    raw_data[tr_date][1].append(tr)
                else:
                    raw_data[tr_date] = ([], [tr])

        return raw_data

    def _get_account(self, guid: str) -> Account:
        return self.book.query(Account).filter(Account.guid == guid).first()

    def _get_recorded_transactions(self, start_date: date, end_date: date) -> list[Transaction]:
        """Get all the recorded sessions for the period"""
        return self.book.query(Transaction).filter(
            Transaction.post_date >= start_date,
            Transaction.post_date <= end_date).all()

    def _get_scheduled_transactions(self, start_date: date, end_date: date) -> list[ScheduledTransactionOccurences]:
        """Get a list of ScheduledTransactions with their lists of occurence dates"""
        raw_transactions: list[ScheduledTransaction] = self.book.query(
            ScheduledTransaction
        ).filter(
            ScheduledTransaction.start_date <= start_date,
            or_(ScheduledTransaction.end_date >= start_date,
                ScheduledTransaction.end_date == None),  # noqa: E711
            ScheduledTransaction.enabled == True  # noqa: E712
        ).all()

        transactions: list[ScheduledTransactionOccurences] = []
        for raw_tr in raw_transactions:
            occurences = self._get_recursive_occurences(
                raw_tr.recurrence, start_date, end_date)
            if len(occurences) > 0:
                transactions.append((raw_tr, occurences))
        return transactions

    def get_transaction_data(self, start_date: date, end_date: date) -> TransactionData:
        """Gets the transaction data for a given period"""
        recorded = self._get_recorded_transactions(
            start_date=start_date, end_date=end_date)
        scheduled = self._get_scheduled_transactions(
            start_date=start_date, end_date=end_date)

        raw_data = self._get_raw_transaction_data(
            recorded=recorded, scheduled=scheduled)

        config = None
        if self.config is not None:
            checkings_account = self._get_account(
                guid=self.config.checkings_parent_guid)
            previous_date = start_date - timedelta(days=1)
            opening_balance = checkings_account.get_balance(
                at_date=previous_date)

            opening_liability = None
            if self.config.liabilities_parent_guid is not None:
                liability = self._get_account(
                    guid=self.config.liabilities_parent_guid)
                opening_liability = liability.get_balance(
                    at_date=previous_date)

            config = TransactionDataConfig(
                opening_balance=opening_balance,
                opening_date=previous_date,
                checkings_parent=checkings_account.fullname,
                opening_liability=opening_liability)

        return TransactionData(data=raw_data, config=config)
