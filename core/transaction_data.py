import dataclasses
from datetime import datetime
from decimal import Decimal
import json

import pandas as pd
from core.transaction_data_item import TransactionDataItem
from core.typings import BalanceType, RawTransactionData
from dataclasses import dataclass


@dataclass
class TransactionDataConfig:
    """
    Configurations related to the transaction data
    """
    opening_balance: Decimal
    opening_date: datetime
    checkings_parent: str = None
    opening_liability: Decimal = None

    def to_json(self):
        return {
            "opening_balance": float(self.opening_balance),
            "opening_date": self.opening_date.__str__(),
            "checkings_parent": self.checkings_parent,
            "opening_liability": float(self.opening_liability)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            opening_balance=Decimal(data["opening_balance"]),
            opening_liability=Decimal(data["opening_liability"]),
            checkings_parent=data["checkings_parent"],
            opening_date=datetime.fromisoformat(data["opening_date"])
        )


@dataclass
class TransactionData(json.JSONEncoder):
    """
    Data related to the transaction itself
    """
    items: list[TransactionDataItem] = dataclasses.field(default_factory=list)
    config: TransactionDataConfig = None

    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns the dataframe with the whole data
        """
        if len(self.items) == 0:
            return pd.DataFrame()
        else:
            return pd.concat(
                [tr.get_dataframe() for tr in self.items],
                ignore_index=True)

    def get_balance_data(self) -> pd.DataFrame:
        """
        Returns a dataframe containing the balance per dates
        """
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

    @classmethod
    def from_rawdata(cls, data: RawTransactionData, config: TransactionDataConfig = None):
        sorted_keys = sorted(data)
        items = []
        for key in sorted_keys:
            item = data[key]
            items.append(TransactionDataItem.from_transactions(
                date=key,
                recorded=item[0],
                scheduled=item[1]
            ))

        return cls(
            items=items,
            config=config
        )

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, config: TransactionDataConfig = None):
        items = []

        unique_dates = df["date"].unique()
        if unique_dates is not None and len(unique_dates) > 0:
            unique_dates.sort()
            for date in unique_dates:
                items.append(TransactionDataItem.from_dataframe(date=date, df=df[df["date"] == date]))

        return cls(
            items=items,
            config=config
        )
