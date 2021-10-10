"""
TransactionData
"""
from datetime import date

import pandas as pd
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

    def get_dataframe(self) -> pd.DataFrame:
        if len(self.items) == 0:
            return pd.DataFrame()
        else:
            return pd.concat([tr.get_dataframe() for tr in self.items], ignore_index=True)