"""
Transaction Journal
"""

from datetime import date
from piecash.core.book import Book
from piecash.core.transaction import ScheduledTransaction, Transaction
from sqlalchemy import or_
from piecash._common import Recurrence
import calendar
from core.transaction_data import TransactionData

from core.typings import RawTransactionData

ScheduledTransactionOccurences = tuple[ScheduledTransaction, list[date]]

class TransactionJournal:

    def __init__(self, book: Book) -> None:
        self.book = book
        pass
  

    def _get_monthly_recursive_occurences(self, recurrence:Recurrence, start_date: date, end_date: date) -> list[tuple[int, int]]:
        """Get the monthly occurences as a list of tuple(month, day)"""
        temp_year = 2000
        temp_start = start_date.replace(year = temp_year)
        temp_end = end_date.replace(year = temp_year)
        temp_date = temp_start.replace(day = recurrence.recurrence_period_start.day)

        month = recurrence.recurrence_period_start.month
        occurences = list()
        known_numbers = {}
        while month not in known_numbers:
            try:
                temp_date = temp_date.replace(month = month, day = recurrence.recurrence_period_start.day)
            except:
                range = calendar.monthrange(temp_year, month)
                temp_date = temp_date.replace(month = month, day = range[1])
            if temp_date >= temp_start and temp_date <= temp_end:
                occurences.append((temp_date.month, temp_date.day))
            known_numbers[month] = True
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
        monthOccurences = self._get_monthly_recursive_occurences(recurrence, start_date, end_date)
        for year in year_occurrences:
            for occ in monthOccurences:
                    occurences.append(date(year, occ[0], occ[1]))
        return occurences

    def _get_recursive_occurences(self, recurrence: Recurrence, start_date: date, end_date: date) -> list[date]:
        """Get the list of dates based on the recurrence patterns"""
        if recurrence.recurrence_period_type == "month":
            monthOccurences = self._get_monthly_recursive_occurences(recurrence, start_date, end_date)
            occurences = list()
            year = start_date.year
            while year <= end_date.year:
                for occ in monthOccurences:
                    occurences.append(date(year, occ[0], occ[1]))
                year = year + 1
            return occurences
        else:
            return self._get_yearly_recursive_occurences(recurrence, start_date, end_date)

    def _get_raw_transaction_data(self, recorded:list[Transaction] = [], scheduled:list[ScheduledTransactionOccurences] = []) -> RawTransactionData:
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

    def get_recorded_transactions(self, start_date: date, end_date: date) -> list[Transaction]:
        """Get all the recorded sessions for the period"""
        return self.book.query(Transaction).filter(Transaction.post_date >= start_date, Transaction.post_date <= end_date).all()

    def get_scheduled_transactions(self, start_date: date, end_date: date) -> list[ScheduledTransactionOccurences]:
        """Get a list of ScheduledTransactions with their lists of occurence dates"""
        raw_transactions: list[ScheduledTransaction] = self.book.query(
            ScheduledTransaction
        ).filter(
            ScheduledTransaction.start_date >= start_date, 
            ScheduledTransaction.start_date <= end_date,
            or_(ScheduledTransaction.end_date >= end_date, ScheduledTransaction.end_date == None),
            ScheduledTransaction.enabled == True
        ).all()

        transactions: list[ScheduledTransactionOccurences] = []
        for raw_tr in raw_transactions:
            occurences = self._get_recursive_occurences(raw_tr.recurrence, start_date, end_date)
            if len(occurences) > 0:
                transactions.append((raw_tr, occurences))
        return transactions

    def get_transaction_data(self, start_date: date, end_date: date) -> TransactionData:
        """Gets the transaction data for a given period"""
        recorded = self.get_recorded_transactions(start_date=start_date, end_date=end_date)
        scheduled = self.get_scheduled_transactions(start_date=start_date, end_date=end_date)

        raw_data = self._get_raw_transaction_data(recorded=recorded, scheduled=scheduled)

        return TransactionData(data=raw_data)


