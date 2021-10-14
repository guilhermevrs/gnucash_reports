"""
TransactionData
"""
from datetime import datetime
from decimal import Decimal

import pandas as pd
from core.transaction_data_item import TransactionDataItem
from dataclasses import dataclass

from core.typings import BalanceType, RawTransactionData

@dataclass
class TransactionDataConfig:
    opening_balance: Decimal
    opening_date: datetime
    checkings_parent: str = None

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
        balance = 0
        scheduled_balance = 0
        data_list = []
        checkings_parent = None

        def newline(
            date: datetime,
            balance: Decimal,
            scheduled: bool = False,
            diff: Decimal = Decimal(0),
            type: BalanceType = BalanceType.CHECKINGS
            ):

            nonlocal data_list
            data_list.append({
                'type': type,
                'date': date,
                'diff': diff,
                'balance': balance,
                'scheduled': scheduled
            })

        if self.config is not None:
            checkings_parent = self.config.checkings_parent
            balance = self.config.opening_balance
            scheduled_balance = self.config.opening_balance
            newline(
                date=self.config.opening_date,
                balance=self.config.opening_balance
            )
            
        for tr in self.items:
            data = tr.get_balance(checkings_parent=checkings_parent).checkings
            balance = balance + data.recorded
            scheduled_balance = scheduled_balance + data.recorded
            newline(
                date=tr.date,
                balance=balance,
                diff=data.recorded
            )

            if data.scheduled != data.recorded:
                scheduled_balance = scheduled_balance + data.scheduled

            if scheduled_balance != balance:
                newline(
                    date=tr.date,
                    balance=scheduled_balance,
                    diff=data.scheduled,
                    scheduled=True
                )
        return pd.DataFrame(data_list)
