"""
TransactionData
"""
from datetime import datetime
from decimal import Decimal

import pandas as pd
from core.transaction_data_item import TransactionDataItem
from dataclasses import dataclass

from core.typings import RawTransactionData

@dataclass
class TransactionDataConfig:
    opening_balance: Decimal
    opening_date: datetime

@dataclass
class TransactionData:
    items: list[TransactionDataItem]
    config: TransactionDataConfig

    def __init__(self, data: RawTransactionData, config: TransactionDataConfig = None) -> None:
        self.config = config
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
            return pd.concat([tr.get_dataframe for tr in self.items], ignore_index=True)

    def get_balance_data(self) -> pd.DataFrame:
        # TODO: Implement the filtering by scheduled
        # TODO: Implement the filtering by accounts
        balance = 0
        data_list = []
        if self.config is not None:
            balance = self.config.opening_balance
            data_list.append({
                'diff': Decimal(0),
                'balance': balance,
                'date': self.config.opening_date
            })
        for tr in self.items:
            diff = tr.get_balance()
            balance = balance + diff
            data_list.append({
                'diff': diff,
                'balance': balance,
                'date': tr.date
            })
        return pd.DataFrame(data_list)
