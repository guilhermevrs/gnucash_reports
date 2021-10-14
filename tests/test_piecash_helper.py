from typing import Dict
import piecash
import os
from piecash.core.account import Account
from piecash.core.book import Book

from piecash.core.transaction import ScheduledTransaction, Transaction

working_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class TestPiecashHelper:

    accounts: Dict[str, Account] = {}
    recorded_transactions: Dict[str, Transaction] = {}
    scheduled_transactions: Dict[str, ScheduledTransaction] = {}
    scheduled_records: Dict[str, Transaction] = {}

    def __init__(self) -> None:
        smaple_data_path = os.path.join(os.path.realpath(working_dir + '/tests/fixtures'), 'sample_data.gnucash')
        book: Book = piecash.open_book(smaple_data_path, open_if_lock=True)

        scheduled = book.query(
            ScheduledTransaction
        ).all()

        for acc in book.accounts:
            self.accounts[acc.fullname] = acc;

        for tr in book.transactions:
            if tr.scheduled_transaction is None:
                self.recorded_transactions[tr.description] = tr
            else:
                self.scheduled_records[tr.description] = tr

        for tr in scheduled:
            self.scheduled_transactions[tr.name] = tr


    def get_record_previously_scheduled(self):
        return self.scheduled_records["ScheduledSplit1"]

    def get_expense_record(self):
        return self.recorded_transactions["CheckingsExpenseFood1"]
    
    def get_income_record(self):
        return self.recorded_transactions["CheckingsSalary1"]

    def get_credit_card_record(self):
        return self.recorded_transactions["CheckingsExpenseCreditCard"]

    def get_scheduled_only(self):
        return self.scheduled_transactions["ScheduledNeverCreated"]

    def get_scheduled_already_recorded(self):
        return self.scheduled_transactions["SampledScheduled"]

    def get_scheduled_income(self):
        return self.scheduled_transactions["ScheduledIncome"]
    
    def get_recorded_transfer(self):
        return self.recorded_transactions["CheckingsTransfer"]

    def get_scheduled_transfer(self):
        return self.scheduled_transactions["ScheduledTransfer"]

    def get_scheduled_expense(self):
        return self.scheduled_transactions["SampledScheduled"]

    def get_recorded_liability(self):
        return self.recorded_transactions["ExpenseLiability"]

    def get_checkings_account(self):
        return self.accounts["Assets:Checkings"]

TestPiecashHelper.__test__ = False