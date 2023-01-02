from dataclasses import dataclass
import dataclasses
import json
import pandas as pd

from core.account_data_Item import AccountDataItem

@dataclass
class AccountData(json.JSONEncoder):
    items: list[AccountDataItem] = dataclasses.field(default_factory=list)

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