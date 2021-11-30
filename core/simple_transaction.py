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
                'to_account': self.from_account,
                'to_account_guid': self.from_account_guid,
                'transaction_type': self.transaction_type
            })
        return pd.DataFrame([df_dict])

    @classmethod
    def simplify_record(cls, tr: Transaction):
        """
        Simplify a Transaction object into SimpleTransaction
        """
        value: Decimal
        from_account: Account
        to_account: Account
        split: Split
        for split in tr.splits:
            if split.is_debit:
                to_account = split.account
                value = split.value
            elif split.is_credit:
                from_account = split.account

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

        return cls(
            value=value,
            description=tr.description,
            from_account=from_account.fullname,
            from_account_guid=from_account.guid,
            to_account=to_account.fullname,
            to_account_guid=to_account.guid,
            transaction_type=transaction_type
        )

    @classmethod
    def simplify_scheduled_record(cls, tr: ScheduledTransaction):
        """
        Simplify a ScheduledTransaction object into SimpleTransaction
        """
        value: Decimal
        from_account: Account
        to_account: Account
        split: Split

        if tr.guid == "05a8aacc72a447e4b385a52972ccce25":
            # TODO: Better handle this one (with debit formula and multiple splits)
            splitFromAccount = tr.template_account.splits[0]
            splitToAccount = tr.template_account.splits[2]
            from_account = splitFromAccount["sched-xaction"]["account"].value
            to_account = splitToAccount["sched-xaction"]["account"].value
            value = Decimal(830.04)
        else:
            for split in tr.template_account.splits:
                slots = split["sched-xaction"]
                if slots["debit-numeric"].value > 0:
                    to_account = slots["account"].value
                    value = slots["debit-numeric"].value
                elif slots["credit-numeric"].value > 0:
                    from_account = slots["account"].value

        transaction_type: TransactionType
        if to_account.type == "LIABILITY" or to_account.type == "EXPENSE":
            if from_account.type == "LIABILITY":
                transaction_type = TransactionType.LIABILITY
            else:
                transaction_type = TransactionType.EXPENSE
        elif to_account.type == "BANK" or to_account.type == "ASSET":
            if from_account.type == "BANK" or from_account.type == "ASSET":
                transaction_type = TransactionType.TRANSFER
            else:
                transaction_type = TransactionType.INCOME

        return cls(
            value=value,
            description=tr.name,
            from_account=from_account.fullname,
            from_account_guid=from_account.guid,
            to_account=to_account.fullname,
            to_account_guid=to_account.guid,
            transaction_type=transaction_type,
            is_scheduled=True
        )

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
