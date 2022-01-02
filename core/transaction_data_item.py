import dataclasses
import pandas as pd
from core.simple_transaction import SimpleTransaction
from core.typings import TransactionType, Balance, BalanceData
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from piecash.core.transaction import ScheduledTransaction, Transaction


@dataclass
class TransactionDataItem:
    """
    Contains all the transactions (recorded or scheduled) for a given date
    """
    date: datetime
    transactions: list[SimpleTransaction] = dataclasses.field(default_factory=list)

    def get_balance(self, checkings_parent: str = None) -> BalanceData:
        """
        Returns the balance information for the date
        """
        checkings_balance = None
        liability_balance = None

        def add_checkings(val: Decimal, scheduled: bool):
            nonlocal checkings_balance

            if checkings_balance is None:
                checkings_balance = Balance(Decimal(0), Decimal(0))
            checkings_balance.scheduled = checkings_balance.scheduled + val
            if not scheduled:
                checkings_balance.recorded = checkings_balance.recorded + val

        def add_liability(val: Decimal, scheduled: bool):
            nonlocal liability_balance

            if liability_balance is None:
                liability_balance = Balance(Decimal(0), Decimal(0))
            liability_balance.scheduled = liability_balance.scheduled + val
            if not scheduled:
                liability_balance.recorded = liability_balance.recorded + val

        for tr in self.transactions:
            if tr.transaction_type == TransactionType.LIABILITY:
                add_liability(tr.value, tr.is_scheduled)
            if tr.transaction_type == TransactionType.QUITTANCE:
                add_liability(-tr.value, tr.is_scheduled)
                add_checkings(-tr.value, tr.is_scheduled)
            elif tr.transaction_type == TransactionType.EXPENSE:
                add_checkings(-tr.value, tr.is_scheduled)
            elif tr.transaction_type == TransactionType.INCOME:
                add_checkings(tr.value, tr.is_scheduled)
            elif (tr.transaction_type == TransactionType.TRANSFER
                    and checkings_parent is not None):
                relevant_from = tr.from_account.startswith(checkings_parent)
                relevant_to = tr.to_account.startswith(checkings_parent)
                if relevant_from and not relevant_to:
                    add_checkings(-tr.value, tr.is_scheduled)
                elif relevant_to and not relevant_from:
                    add_checkings(tr.value, tr.is_scheduled)

        return BalanceData(
            checkings=checkings_balance,
            liability=liability_balance)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe containing all the information present
        """
        if len(self.transactions) == 0:
            return pd.DataFrame()
        else:
            temp_dfs = [tr.get_dataframe() for tr in self.transactions]
            df = pd.concat(temp_dfs, ignore_index=True).assign(
                date=lambda _: self.date)
            return df

    @classmethod
    def from_dataframe(cls, date: datetime, df: pd.DataFrame) -> None:
        """
        Loads a TransactionDataItem using a dataframe
        """
        transactions = []
        for index, row in df.iterrows():
            transactions.append(SimpleTransaction.from_series(row))

        return cls(date=date, transactions=transactions)

    @classmethod
    def from_transactions(cls,
                          date: datetime,
                          recorded: list[Transaction] = [],
                          scheduled: list[ScheduledTransaction] = []):
        """
        Loads a TransactionDataItem using a GnuCash transaction objects
        """
        transactions = []
        # Get all the guids from scheduled recorded
        sch_guids = []
        for rec in recorded:
            if rec.scheduled_transaction is not None:
                sch_guids.append(rec.scheduled_transaction.guid)
            try:
                transactions.append(SimpleTransaction.simplify_record(rec))
            except AttributeError as e:
                print(e)

        for sch in scheduled:
            if sch.guid in sch_guids:
                sch_guids.remove(sch.guid)
            else:
                transactions.append(
                    SimpleTransaction.simplify_scheduled_record(sch))

        return cls(date=date, transactions=transactions)
