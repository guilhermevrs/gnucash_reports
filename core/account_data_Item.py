from dataclasses import dataclass
import pandas as pd


@dataclass
class AccountDataItem:
    name: str

    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe with the current data
        """
        df_dict = {
            'name': self.name,
        }
        return pd.DataFrame([df_dict])
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> None:
        """
        Loads a TransactionDataItem using a dataframe
        """
        row = df.iloc[0]
        return cls(
            name=row["name"]
        )