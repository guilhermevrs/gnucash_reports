from dataclasses import dataclass
import json
from typing import List, Tuple
from dash.dependencies import Output, Input
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate

from components.transaction_store_block import TransactionStore
from core.typings import TransactionType
from .base_block import BaseComponent, BaseComponentConfig
from dash import Dash, html, dash_table as dt
import pandas as pd


@dataclass
class TransactionTableInput():
    store_name: str


class TransactionTableComponent(BaseComponent):

    layout: Component

    def __init__(self, input: TransactionTableInput, app: Dash = None, config: BaseComponentConfig = None) -> None:
        self.input = input
        super().__init__(app=app, config=config)

    def render(self):
        return html.Div(children=[
            dt.DataTable(
                id=self.get_name(),
                columns=[
                    {'name': 'Date', 'id': 'date', 'type': 'datetime', 'editable': False},
                    {'name': 'Description', 'id': 'description', 'editable': False},
                    {'name': 'From', 'id': 'from_account', 'editable': False},
                    {'name': 'To', 'id': 'to_account', 'editable': False},
                    {'name': 'Type', 'id': 'transaction_type', 'editable': False},
                    {'name': 'Scheduled', 'id': 'is_scheduled', 'editable': False},
                    {'name': 'Value', 'id': 'value', 'editable': False}
                ]
            )
        ])

    def get_name(self) -> str:
        return self.prefix("transaction-table")

    def callbacks(self, app: Dash) -> None:
        @app.callback(
            # Output(self.get_name(), "columns"),
            Output(self.get_name(), "data"),
            Input(self.input.store_name, "data")
        )
        def load_data(data) -> Tuple[List[str], pd.DataFrame]:
            if data is None:
                raise PreventUpdate

            trx_data = TransactionStore.load_data(data)
            df = trx_data.get_dataframe()

            df["value"] = df["value"].astype(float)

            df['transaction_type'] = df['transaction_type'].map({
                TransactionType.EXPENSE: 'Expense',
                TransactionType.INCOME: 'Income',
                TransactionType.LIABILITY: 'Liability',
                TransactionType.OPENING_BALANCE: 'Opening Balance',
                TransactionType.QUITTANCE: 'Quittance',
                TransactionType.TRANSFER: 'Transfer'
            })

            df['date'] = df["date"].dt.strftime('%d-%m-%Y')

            return df.to_dict(orient='records')
