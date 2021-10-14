from datetime import date
from enum import Enum

from piecash.core.transaction import ScheduledTransaction, Transaction

RawTransactionData = dict[date, tuple[list[Transaction], list[ScheduledTransaction]]]

class BalanceType(Enum):
    CHECKINGS = "checkings"