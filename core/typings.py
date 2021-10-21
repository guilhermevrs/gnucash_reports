"""
typings.py
General and utility typings used through all the apps
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from piecash.core.transaction import ScheduledTransaction, Transaction

"""
Describes the raw data needed to create a TransactionData
"""
RawTransactionData = dict[date, tuple[list[Transaction], list[ScheduledTransaction]]]

class BalanceType(Enum):
    """
    Indicates the type referent to the balance (useful for multi accounts)
    """
    CHECKINGS = "checkings"
    LIABILITIES = "liabilities"

class TransactionType(Enum):
    """
    Indicates the type of the transaction
    """
    EXPENSE = "expense"
    LIABILITY = "liability"
    QUITTANCE = "quittance"
    INCOME = "income"
    TRANSFER = "transfer"
    OPENING_BALANCE = "opening_balance"

@dataclass
class Balance:
    """
    Represents a recorded and scheduled (forecasted) balance
    """
    recorded: Decimal
    scheduled: Decimal

@dataclass
class BalanceData:
    """
    Balance info for different types of accounts
    """
    checkings: Balance = None
    liability: Balance = None