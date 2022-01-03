from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
from dash.dependencies import Output, Input, State
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate

from components.transaction_store_block import TransactionStore
from core.typings import BalanceType, TransactionType
from .base_block import BaseComponent, BaseComponentConfig
from dash import Dash, dcc, html, dash_table as dt
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

    def get_stripped_pattern(self, accent, background):
        return 'repeating-linear-gradient(45deg, {accent}, {accent} 30px, {background} 30px, {background} 60px)'.format(
            accent=accent, background=background)

    def render(self):
        # TODO: Rowspan for dates
        return html.Div(children=[
            dcc.Store(
                id=self.get_legend_store_name(),
                data=None
            ),
            dt.DataTable(
                id=self.get_name(),
                columns=[
                    {'name': 'Date', 'id': 'date', 'type': 'datetime'},
                    {'name': 'Description', 'id': 'description'},
                    {'name': 'From', 'id': 'from_account'},
                    {'name': 'To', 'id': 'to_account'},
                    {'name': 'Type', 'id': 'transaction_type'},
                    {'name': 'Value', 'id': 'value'}
                ],
                editable=False,
                style_cell_conditional=[
                    {'if': {'column_id': 'date'},
                     'width': '100px'},
                    {
                        'if': {'column_id': 'description'},
                        'minWidth': '480px', 'width': '480px', 'maxWidth': '480px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    {
                        'if': {'column_id': 'from_account'},
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    {
                        'if': {'column_id': 'to_account'},
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    {'if': {'column_id': 'transaction_type'},
                     'width': '100px',
                     'fontWeight': 'bold'
                     },
                    {'if': {'column_id': 'value'},
                     'width': '100px'},
                ],
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '({transaction_type} = Expense || {transaction_type} = Quittance) && {is_scheduled} = False',
                            'column_id': 'transaction_type'
                        },
                        'backgroundColor': '#e47777',
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '({transaction_type} = Expense || {transaction_type} = Quittance) && {is_scheduled} = True',
                            'column_id': 'transaction_type'
                        },
                        'backgroundImage': self.get_stripped_pattern('#e47777', '#f1bbbb'),
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Income && {is_scheduled} = False',
                            'column_id': 'transaction_type'
                        },
                        'backgroundColor': '#73c577',
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Income && {is_scheduled} = True',
                            'column_id': 'transaction_type'
                        },
                        'backgroundImage': self.get_stripped_pattern('#73c577', '#d0eec5'),
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Liability && {is_scheduled} = False',
                            'column_id': 'transaction_type'
                        },
                        'backgroundColor': '#ffac65',
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Liability && {is_scheduled} = True',
                            'column_id': 'transaction_type'
                        },
                        'backgroundImage': self.get_stripped_pattern('#ffac65', '#ffd1b3'),
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Transfer && {is_scheduled} = False',
                            'column_id': 'transaction_type'
                        },
                        'backgroundColor': '#31d4ff',
                        'color': 'black'
                    },
                    {
                        'if': {
                            'filter_query': '{transaction_type} = Transfer && {is_scheduled} = True',
                            'column_id': 'transaction_type'
                        },
                        'backgroundImage': self.get_stripped_pattern('#31d4ff', '#c6def4'),
                        'color': 'black'
                    }
                ]
            )
        ])

    def get_name(self) -> str:
        return self.prefix("transaction-table")

    def get_legend_store_name(self) -> str:
        return self.prefix("legend_store_name")

    def callbacks(self, app: Dash) -> None:
        @app.callback(
            Output(self.get_name(), "data"),
            Output(self.get_legend_store_name(), "data"),
            Input(self.input.store_name, "data"),
            Input(self.input.graph_name, "relayoutData"),
            Input(self.input.graph_name, "restyleData"),
            State(self.get_legend_store_name(), "data")
        )
        def load_data(data, relayoutData, restyleData, legendMemory):
            if data is None:
                raise PreventUpdate

            if self._has_loaded_once and (
                relayoutData is None and "autosize" in relayoutData
            ):
                raise PreventUpdate

            self._has_loaded_once = True

            legends = legendMemory if legendMemory is not None else [True, True, True, True]
            if restyleData is not None:
                legends[restyleData[1][0]] = restyleData[0]["visible"][0] is True

            trx_data = TransactionStore.load_data(data)
            df = self.get_filtered_data(trx_data.get_dataframe(), relayoutData, legends)

            df["value"] = df["value"].astype(float)
            df["is_scheduled"] = df["is_scheduled"].astype('str')

            df['transaction_type'] = df['transaction_type'].map({
                TransactionType.EXPENSE: 'Expense',
                TransactionType.INCOME: 'Income',
                TransactionType.LIABILITY: 'Liability',
                TransactionType.OPENING_BALANCE: 'Opening Balance',
                TransactionType.QUITTANCE: 'Quittance',
                TransactionType.TRANSFER: 'Transfer'
            })

            df['date'] = df["date"].dt.strftime('%d-%m-%Y')

            return [df.to_dict(orient='records'), legends]

    def get_filtered_data(self, df: pd.DataFrame, relayout: Dict, legends) -> pd.DataFrame:
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

        legends_type = [
            {"type": "Assets:Current:Checkings", "scheduled": False},
            {"type": "Assets:Current:Checkings", "scheduled": True},
            {"type": "Liabilities", "scheduled": False},
            {"type": "Liabilities", "scheduled": True}
        ]
        allowed_legends = []
        for i in range(len(legends)):
            if legends[i]:
                allowed_legends.append(legends_type[i])

        dataframes = []
        for allowed in allowed_legends:
            temp_df = df[df["from_account"].str.contains(allowed["type"])]
            dataframes.append(temp_df[temp_df["is_scheduled"] == allowed["scheduled"]])

        return pd.concat(dataframes)
