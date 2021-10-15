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
    opening_liability: Decimal = None

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
        checkings = 0
        scheduled_checkings = 0
        liability = 0
        scheduled_liability = 0
        checkings_list = []
        liabilities_list = []
        checkings_parent = None

        def newline(
            date: datetime,
            balance: Decimal,
            scheduled: bool = False,
            diff: Decimal = Decimal(0),
            type: BalanceType = BalanceType.CHECKINGS
            ):

            return {
                'type': type,
                'date': date,
                'diff': diff,
                'balance': balance,
                'scheduled': scheduled
            }

        if self.config is not None:
            checkings_parent = self.config.checkings_parent
            checkings = self.config.opening_balance
            scheduled_checkings = self.config.opening_balance
            checkings_list.append(newline(
                date=self.config.opening_date,
                balance=self.config.opening_balance
            ))
            if self.config.opening_liability is not None:
                liabilities_list.append(newline(
                    date=self.config.opening_date,
                    balance=self.config.opening_liability,
                    type=BalanceType.LIABILITIES
                ))
            
        for tr in self.items:
            balance_data = tr.get_balance(checkings_parent=checkings_parent)
            checkings_data = balance_data.checkings
            liabilities_data = balance_data.liability

            if checkings_data is not None:

                checkings = checkings + checkings_data.recorded
                scheduled_checkings = scheduled_checkings + checkings_data.recorded
                checkings_list.append(newline(
                    date=tr.date,
                    balance=checkings,
                    diff=checkings_data.recorded
                ))

                if checkings_data.scheduled != checkings_data.recorded:
                    scheduled_checkings = scheduled_checkings + checkings_data.scheduled

                if scheduled_checkings != checkings:
                    checkings_list.append(newline(
                        date=tr.date,
                        balance=scheduled_checkings,
                        diff=checkings_data.scheduled,
                        scheduled=True
                    ))

            if liabilities_data is not None:

                liability = liability + liabilities_data.recorded
                scheduled_liability = scheduled_liability + liabilities_data.recorded
                liabilities_list.append(newline(
                    date=tr.date,
                    balance=liability,
                    diff=liabilities_data.recorded,
                    type=BalanceType.LIABILITIES
                ))

                if liabilities_data.scheduled != liabilities_data.recorded:
                    scheduled_liability = scheduled_liability + liabilities_data.scheduled

                if scheduled_liability != liability:
                    liabilities_list.append(newline(
                        date=tr.date,
                        balance=scheduled_liability,
                        diff=liabilities_data.scheduled,
                        scheduled=True,
                        type=BalanceType.LIABILITIES
                    ))

        return pd.DataFrame(checkings_list + liabilities_list)
