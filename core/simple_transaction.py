from decimal import Decimal
from dataclasses import dataclass
from typing import Dict
import pandas as pd
from piecash.core.account import Account

from piecash.core.transaction import ScheduledTransaction, Split, Transaction

from core.typings import TransactionType


@dataclass
class SimpleTransaction:
    """
    Describes a simplified transaction
    """
    value: Decimal
    description: str = ""
    from_account: str = ""
    from_account_guid: str = ""
    to_account: str = ""
    to_account_guid: str = ""
    transaction_type: TransactionType = TransactionType.OPENING_BALANCE
    is_scheduled: bool = False

    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe with the current data
        """
        df_dict = {
            'value': self.value,
            'is_scheduled': self.is_scheduled
        }
        if self.transaction_type != TransactionType.OPENING_BALANCE:
            df_dict.update({
                'description': self.description,
                'from_account': self.from_account,
                'from_account_guid': self.from_account_guid,
                'to_account': self.to_account,
                'to_account_guid': self.to_account_guid,
                'transaction_type': self.transaction_type
            })
        return pd.DataFrame([df_dict])

    @classmethod
    def get_transaction_type(cls, to_account: Account, from_account: Account) -> TransactionType:
        transaction_type: TransactionType
        if to_account.type == "LIABILITY":
            transaction_type = TransactionType.QUITTANCE
        elif to_account.type == "EXPENSE":
            if from_account.type == "LIABILITY":
                transaction_type = TransactionType.LIABILITY
            else:
                transaction_type = TransactionType.EXPENSE
        elif to_account.type == "BANK" or to_account.type == "ASSET":
            if from_account.type == "BANK" or from_account.type == "ASSET":
                transaction_type = TransactionType.TRANSFER
            else:
                transaction_type = TransactionType.INCOME
        return transaction_type

    @classmethod
    def simplify_record(cls, tr: Transaction):
        """
        Simplify a Transaction object into SimpleTransaction
        """
        split: Split

        trx = {}
        for split in tr.splits:
            value = abs(split.value)
            if value not in trx:
                trx[value] = {}
            if split.is_debit:
                trx[value]["to_account"] = split.account
            elif split.is_credit:
                trx[value]["from_account"] = split.account

        simplified_transactions = []
        for value in trx.keys():
            if "to_account" not in trx[value]:
                raise AttributeError("Can't find to_account for transaction {}".format(tr.guid))

            to_account = trx[value]["to_account"]
            from_account = trx[value]["from_account"]
            
            try:
                transaction_type = SimpleTransaction.get_transaction_type(to_account=to_account, from_account=from_account)
            except:
                transaction_type = TransactionType.EXPENSE
                print("{} -> {} ({})".format(from_account.fullname, to_account.fullname, tr.description))

            simplified_transactions.append(cls(
                value=value,
                description=tr.description,
                from_account=from_account.fullname,
                from_account_guid=from_account.guid,
                to_account=to_account.fullname,
                to_account_guid=to_account.guid,
                transaction_type=transaction_type
            ))

        return simplified_transactions

    @classmethod
    def simplify_scheduled_record(cls, tr: ScheduledTransaction):
        """
        Simplify a ScheduledTransaction object into SimpleTransaction
        """
        split: Split
        trx = {}
        if tr.guid == "05a8aacc72a447e4b385a52972ccce25":
            # TODO: Handle formulas
            splitFromAccount = tr.template_account.splits[0]
            splitToAccount = tr.template_account.splits[2]
            trx[Decimal(830.04)] = {
                "from_account": splitFromAccount["sched-xaction"]["account"].value,
                "to_account": splitToAccount["sched-xaction"]["account"].value
            }
        else:
            for split in tr.template_account.splits:
                slots = split["sched-xaction"]
                debit_value = slots["debit-numeric"].value
                credit_value = slots["credit-numeric"].value
                value = abs(debit_value if debit_value > 0 else credit_value)
                if value not in trx:
                    trx[value] = {}
                if debit_value > 0:
                    trx[value]["to_account"] = slots["account"].value
                elif credit_value > 0:
                    trx[value]["from_account"] = slots["account"].value

        simplified_transactions = []
        for value in trx.keys():
            to_account = trx[value]["to_account"]
            from_account = trx[value]["from_account"]
            transaction_type = SimpleTransaction.get_transaction_type(to_account=to_account, from_account=from_account)

            if to_account is None:
                raise AttributeError("Can't find to_account for transaction {}".format(tr.guid))

            simplified_transactions.append(cls(
                value=value,
                description=tr.name,
                from_account=from_account.fullname,
                from_account_guid=from_account.guid,
                to_account=to_account.fullname,
                to_account_guid=to_account.guid,
                transaction_type=transaction_type,
                is_scheduled=True
            ))

        return simplified_transactions

    @classmethod
    def from_series(cls, series: pd.Series):

        raw_type = series["transaction_type"]
        if isinstance(raw_type, Dict):
            raw_type = TransactionType[raw_type["name"]]

        return cls(
            value=Decimal(series["value"]),
            description=series["description"],
            from_account=series["from_account"],
            from_account_guid=series["from_account_guid"],
            to_account=series["to_account"],
            to_account_guid=series["to_account_guid"],
            transaction_type=raw_type,
            is_scheduled=series["is_scheduled"]
        )
