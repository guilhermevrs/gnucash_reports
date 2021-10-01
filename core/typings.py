from datetime import date

from piecash.core.transaction import ScheduledTransaction, Transaction

RawTransactionData = dict[date, tuple[list[Transaction], list[ScheduledTransaction]]]