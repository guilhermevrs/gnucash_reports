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
class BalanceData:
    checkings: Balance = None
    liability: Balance = None

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

    def get_balance(self, checkings_parent:str = None) -> BalanceData:
        expenses_balance: Decimal = Decimal('0')
        income_balance: Decimal = Decimal('0')
        scheduled_expenses = Decimal(0)
        scheduled_income = Decimal(0)

        def add_expense(val: Decimal):
            nonlocal scheduled_expenses
            nonlocal expenses_balance
            
            scheduled_expenses = scheduled_expenses + val
            if not tr.is_scheduled:
                expenses_balance = expenses_balance + val

        def add_income(val: Decimal):
            nonlocal scheduled_income
            nonlocal income_balance

            scheduled_income = scheduled_income + val
            if not tr.is_scheduled:
                income_balance = income_balance + val

        for tr in self.transactions:
            if tr.transaction_type == TransactionType.EXPENSE:
                add_expense(tr.value)
            elif tr.transaction_type == TransactionType.INCOME:
                add_income(tr.value)
            elif tr.transaction_type == TransactionType.TRANSFER and checkings_parent is not None:
                relevant_from = tr.from_account.startswith(checkings_parent)
                relevant_to = tr.to_account.startswith(checkings_parent)
                if relevant_from and not relevant_to :
                    # Expense...
                    add_expense(tr.value)
                elif relevant_to and not relevant_from:
                    # Income...
                    add_income(tr.value)
        
        recorded = income_balance-expenses_balance
        scheduled = scheduled_income - scheduled_expenses
        checkings = Balance(recorded=recorded, scheduled=scheduled)
        return BalanceData(checkings=checkings)

    def get_dataframe(self) -> pd.DataFrame:
        if len(self.transactions) == 0:
            return pd.DataFrame()
        else:
            temp_dfs = [tr.get_dataframe() for tr in self.transactions]
            df = pd.concat(temp_dfs, ignore_index=True).assign(date=lambda _: self.date)
            return df