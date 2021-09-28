from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from piecash.core.account import Account

from piecash.core.transaction import ScheduledTransaction, Split, Transaction

class TransactionType(Enum):
    EXPENSE = 1
    INCOME = 2
    TRANSFER = 0

@dataclass
class SimpleTransaction:
    value: Decimal
    from_account: str
    from_account_guid: str
    to_account: str
    to_account_guid: str
    transaction_type: TransactionType

    @classmethod
    def simplify_record(cls, tr: Transaction):
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
        if to_account.type == "LIABILITY" or to_account.type == "EXPENSE":
            transaction_type = TransactionType.EXPENSE
        elif to_account.type == "BANK" or to_account.type == "ASSET":
            if from_account.type == "BANK" or from_account.type == "ASSET":
                transaction_type = TransactionType.TRANSFER
            else:
                transaction_type = TransactionType.INCOME

        return cls(
            value = value,
            from_account = from_account.fullname,
            from_account_guid = from_account.guid,
            to_account = to_account.fullname,
            to_account_guid = to_account.guid,
            transaction_type = transaction_type
        )

    @classmethod
    def simplify_scheduled_record(cls, tr: ScheduledTransaction):
        value: Decimal
        from_account: Account
        to_account: Account
        split: Split
        for split in tr.template_account.splits:
            slots = split["sched-xaction"]
            if slots["debit-formula"].value != "":
                to_account = slots["account"].value
                value = slots["debit-numeric"].value
            elif slots["credit-formula"].value != "":
                from_account = slots["account"].value
        
        transaction_type: TransactionType
        if to_account.type == "LIABILITY" or to_account.type == "EXPENSE":
            transaction_type = TransactionType.EXPENSE
        elif to_account.type == "BANK" or to_account.type == "ASSET":
            if from_account.type == "BANK" or from_account.type == "ASSET":
                transaction_type = TransactionType.TRANSFER
            else:
                transaction_type = TransactionType.INCOME

        return cls(
            value = value,
            from_account = from_account.fullname,
            from_account_guid = from_account.guid,
            to_account = to_account.fullname,
            to_account_guid = to_account.guid,
            transaction_type = transaction_type
        )