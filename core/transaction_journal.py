"""
Transaction Journal
"""

from datetime import date, datetime
from typing import List, Tuple
from piecash.core.book import Book
from piecash.core.transaction import ScheduledTransaction, Transaction
from sqlalchemy import or_
from piecash._common import Recurrence
import calendar

class TransactionJournal:

    def __init__(self, book: Book) -> None:
        self.book = book
        pass
  

    def _get_monthly_recursive_occurences(self, recurrence:Recurrence, start_date: date, end_date: date) -> List[Tuple]:
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

    def _get_recursive_occurences(self, recurrence: Recurrence, start_date: date, end_date: date) -> List[date]:
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

    def get_recorded_transactions(self, start_date: date, end_date: date) -> List[Transaction]:
        return self.book.query(Transaction).filter(Transaction.post_date >= start_date, Transaction.post_date <= end_date).all()

    def get_scheduled_transactions(self, start_date: date, end_date: date) -> List[Tuple[ScheduledTransaction, List[date]]]:
        raw_transactions: List[ScheduledTransaction] = self.book.query(
            ScheduledTransaction
        ).filter(
            ScheduledTransaction.start_date >= start_date, 
            ScheduledTransaction.start_date <= end_date,
            or_(ScheduledTransaction.end_date >= end_date, ScheduledTransaction.end_date == None),
            ScheduledTransaction.enabled == True
        ).all()

        transactions = []
        for raw_tr in raw_transactions:
            occurences = self._get_recursive_occurences(raw_tr.recurrence, start_date, end_date)
            if len(occurences) > 0:
                transactions.append((raw_tr, occurences))
        return transactions

    # TODO: Get transactions by date, filtering scheduled when they are recorded


