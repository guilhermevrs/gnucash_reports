"""
TransactionDataItem
"""
import pandas as pd
from core.simple_transaction import SimpleTransaction, TransactionType
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from piecash.core.transaction import ScheduledTransaction, Transaction

@dataclass
class Balance:
    recorded: Decimal
    scheduled: Decimal

@dataclass
class TransactionDataItem:
    date: datetime
    transactions: list[SimpleTransaction]

    def __init__(self, date: datetime, recorded: list[Transaction], scheduled: list[ScheduledTransaction]) -> None:
        self.date = date
        self.transactions = []
        # Get all the guids from scheduled recorded
        sch_guids = []
        for rec in recorded:
            if rec.scheduled_transaction is not None:
                sch_guids.append(rec.scheduled_transaction.guid)
            self.transactions.append(SimpleTransaction.simplify_record(rec))

        for sch in scheduled:
            if sch.guid in sch_guids:
                sch_guids.remove(sch.guid)
            else:
                self.transactions.append(SimpleTransaction.simplify_scheduled_record(sch))

    def get_balance(self) -> Balance:
        expenses_balance: Decimal = Decimal('0')
        income_balance: Decimal = Decimal('0')
        scheduled_expenses = Decimal(0)
        scheduled_income = Decimal(0)

        for tr in self.transactions:
            if tr.transaction_type == TransactionType.EXPENSE:
                scheduled_expenses = scheduled_expenses + tr.value
                if not tr.is_scheduled:
                    expenses_balance = expenses_balance + tr.value
            elif tr.transaction_type == TransactionType.INCOME:
                scheduled_income = scheduled_income + tr.value
                if not tr.is_scheduled:
                    income_balance = income_balance + tr.value

        # TODO: Handle transfers
        recorded = income_balance-expenses_balance
        scheduled = scheduled_income - scheduled_expenses
        return Balance(recorded=recorded, scheduled=scheduled)

    def get_dataframe(self) -> pd.DataFrame:
        if len(self.transactions) == 0:
            return pd.DataFrame()
        else:
            temp_dfs = [tr.get_dataframe() for tr in self.transactions]
            df = pd.concat(temp_dfs, ignore_index=True).assign(date=lambda _: self.date)
            return df