from dataclasses import dataclass
import json
from dash import dcc, html
from dash.dash import Dash
from dash.dependencies import Output
from dash.development.base_component import Component
import pandas as pd

from core.transaction_data import TransactionData, TransactionDataConfig
from .base_block import BaseComponent, BaseComponentConfig


@dataclass
class TransactionStoreInput():
    data: TransactionData


class TransactionStore(BaseComponent):
    layout: Component

    def __init__(self, input: TransactionStoreInput, app: Dash = None, config: BaseComponentConfig = None) -> None:
        self.input = input
        super().__init__(app=app, config=config)

    def render(self):
        return html.Div(children=[
            dcc.Store(
                id=self.get_name(),
                data=self.get_data()
            )
        ])

    def get_name(self) -> str:
        return self.prefix('transaction-store')

    def get_data(self) -> str:
        df_json = self.input.data.get_dataframe().to_json(orient="split")
        data = {
            "items": df_json,
            "config": self.input.data.config.to_json()
        }
        return json.dumps(data)

    @classmethod
    def load_data(cls, data: str) -> TransactionData:
        decoded = json.loads(data)
        df = pd.read_json(decoded["items"], orient='split')
        config = TransactionDataConfig.from_dict(decoded["config"])
        return TransactionData.from_dataframe(df=df, config=config)
