from dataclasses import dataclass
from dash import dcc, html
from dash.dash import Dash
from dash.dependencies import Output
from dash.development.base_component import Component

from core.transaction_data import TransactionData
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
                data=self.input.data.get_dataframe().to_json(orient="split")
            )
        ])

    def get_name(self) -> str:
        return self.prefix('transaction-store')
