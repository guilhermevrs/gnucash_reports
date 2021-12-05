from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
from dash.dependencies import Output, Input
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate

from components.transaction_store_block import TransactionStore
from core.typings import TransactionType
from .base_block import BaseComponent, BaseComponentConfig
from dash import Dash, html, dash_table as dt
import pandas as pd
import json


@dataclass
class TransactionTableInput():
    store_name: str
    graph_name: str


class TransactionTableComponent(BaseComponent):

    layout: Component
    _has_loaded_once = False

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
            Input(self.input.store_name, "data"),
            Input(self.input.graph_name, "relayoutData")
        )
        def load_data(data, relayoutData) -> Tuple[List[str], pd.DataFrame]:
            if data is None:
                raise PreventUpdate

            if self._has_loaded_once and "autosize" in relayoutData:
                raise PreventUpdate

            self._has_loaded_once = True

            trx_data = TransactionStore.load_data(data)
            df = self.get_filtered_data(trx_data.get_dataframe(), relayoutData)

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

    def get_filtered_data(self, df: pd.DataFrame, relayout: Dict) -> pd.DataFrame:
        if relayout is None:
            return df

        if "xaxis.range[0]" in relayout:
            date_lower, _sep, _tail = relayout["xaxis.range[0]"].partition('.')
            date_upper, _sep, _tail = relayout["xaxis.range[1]"].partition('.')

            date_lower = datetime.strptime(date_lower, "%Y-%m-%d %H:%M:%S")
            date_lower = date_lower.replace(hour=0, minute=0, second=0)
            
            date_upper = datetime.strptime(date_upper, "%Y-%m-%d %H:%M:%S")
            date_upper = date_upper.replace(hour=23, minute=59, second=59)

            df = df[df["date"] >= date_lower]
            df = df[df["date"] <= date_upper]

        return df
