"""
TransactionData
"""
from datetime import date
from core.transaction_data_item import TransactionDataItem
from dataclasses import dataclass

from core.typings import RawTransactionData

@dataclass
class TransactionData:
    items: list[TransactionDataItem]

    def __init__(self, data: RawTransactionData) -> None:
        self.items = []
        for item in data.items():
            self.items.append(TransactionDataItem(
                date = item[0],
                recorded = item[1][0],
                scheduled = item[1][1]
            ))
    
    def filter_by_date(self, start_date: date, end_date: date):
        return [tr for tr in self.items if tr.date >= start_date and tr.date <= end_date]