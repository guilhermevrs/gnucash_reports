from dataclasses import dataclass
import json
from dash import dcc, html
from dash.dash import Dash
from dash.dependencies import Output
from dash.development.base_component import Component
import pandas as pd

from core.account_data import AccountData

from .base_block import BaseComponent, BaseComponentConfig


@dataclass
class AccountStoreInput():
    data: AccountData


class AccountStore(BaseComponent):
    layout: Component

    def __init__(self, input: AccountStoreInput, app: Dash = None, config: BaseComponentConfig = None) -> None:
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
        return self.prefix('account-store')

    def get_data(self) -> str:
        df_json = self.input.data.get_dataframe().to_json(orient="split")
        data = {
            "items": df_json,
        }
        return json.dumps(data)

    @classmethod
    def load_data(cls, data: str) -> AccountData:
        decoded = json.loads(data)
        df = pd.read_json(decoded["items"], orient='split')
        return AccountData.from_dataframe(df=df)
