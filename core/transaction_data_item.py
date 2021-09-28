"""
TransactionDataItem
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from piecash.core.account import Account
from piecash.core.transaction import ScheduledTransaction, Split, Transaction

@dataclass
class TransactionDataItem:
    date: date
    recorded: List[Transaction]
    scheduled: List[ScheduledTransaction]

    def __init__(self, date: date, recorded: List[Transaction], scheduled: List[ScheduledTransaction]) -> None:
        self.date = date
        self.recorded = recorded
        
        self.scheduled = []
        # Get all the guids from scheduled recorded
        sch_guids = []
        for rec in recorded:
            if rec.scheduled_transaction is not None:
                sch_guids.append(rec.scheduled_transaction.guid)

        for sch in scheduled:
            if sch.guid in sch_guids:
                sch_guids.remove(sch.guid)
            else:
                self.scheduled.append(sch)

    def get_balance(self) -> Decimal:

        expenses_balance: Decimal = Decimal('0')
        income_balance: Decimal = Decimal('0')
        for tr in self.recorded:
            split: Split
            for split in tr.splits:
                if split.is_debit:
                    account: Account = split.account
                    if account.type == "LIABILITY" or account.type == "EXPENSE":
                        expenses_balance = expenses_balance + split.value
                    elif account.type == "BANK" or account.type == "ASSET":
                        income_balance = income_balance + split.value

        for tr in self.scheduled:
            for split in tr.template_account.splits:
                slots = split["sched-xaction"]
                if slots["debit-formula"] != '':
                    account: Account = slots["account"].value
                    if account.type == "LIABILITY" or account.type == "EXPENSE":
                        expenses_balance = expenses_balance + slots["debit-numeric"].value
                    elif account.type == "BANK" or account.type == "ASSET":
                        income_balance = income_balance + slots["debit-numeric"].value
            
        return income_balance-expenses_balance
            