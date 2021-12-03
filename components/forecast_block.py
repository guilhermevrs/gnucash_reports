from dataclasses import dataclass
from dash.dash import Dash
from dash.dependencies import Input, Output
from dash.development.base_component import Component
from plotly.missing_ipywidgets import FigureWidget
from dash.exceptions import PreventUpdate
from components.transaction_store_block import TransactionStore

from core.typings import BalanceType
from .base_block import BaseComponent, BaseComponentConfig
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd


@dataclass
class ForecastComponentInput():
    store_name: str


class ForecastComponent(BaseComponent):

    layout: Component

    def __init__(self, input: ForecastComponentInput, app: Dash = None, config: BaseComponentConfig = None) -> None:
        self.input = input
        super().__init__(app=app, config=config)

    def render(self):
        """Initializes the component layout"""
        return html.Div(children=[
            dcc.Graph(
                id=self.prefix('graph')
            )
        ])

    def callbacks(self, app: Dash) -> None:
        @app.callback(
            Output(self.prefix('graph'), 'figure'),
            Input(self.input.store_name, "data")
        )
        def load_data(data) -> FigureWidget:
            if data is None:
                raise PreventUpdate

            trx_data = TransactionStore.load_data(data)
            balance_data = trx_data.get_balance_data()

            fig = go.Figure()

            def add_trace(data: pd.DataFrame, name: str, scheduled: bool = False):
                nonlocal fig
                fig.add_trace(
                    go.Scatter(x=data["date"],
                               y=data["balance"],
                               name=name,
                               line=go.scatter.Line(
                        dash="dash" if scheduled is True else "solid"
                    )))

            add_trace(self.get_recorded_checkings(balance_data), "Checkings")
            add_trace(self.get_scheduled_checkings(balance_data), "Checkings (scheduled)", True)
            add_trace(self.get_recorded_liabilities(balance_data), "Liabilities")
            add_trace(self.get_scheduled_liabilities(balance_data), "Liabilities (scheduled)", True)

            return fig

    def _get_scheduled(self, data: pd.DataFrame, scheduled_value: bool):
        """Filter data based on the scheduled value"""
        return data[data["scheduled"] == scheduled_value]

    def _get_type(self, data: pd.DataFrame, type: BalanceType):
        """Filter data based on the type value"""
        return data[data["type"] == type]

    def get_recorded_checkings(self, data: pd.DataFrame):
        """Filter data for only recorded checkings"""
        all_recorded = self._get_scheduled(data, False)
        return self._get_type(all_recorded, BalanceType.CHECKINGS)

    def get_scheduled_checkings(self, data: pd.DataFrame):
        """Filter data for only scheduled checkings"""
        all_scheduled = self._get_scheduled(data, True)
        return self._get_type(all_scheduled, BalanceType.CHECKINGS)

    def get_recorded_liabilities(self, data: pd.DataFrame):
        """Filter data for only recorded liabilities"""
        all_recorded = self._get_scheduled(data, False)
        return self._get_type(all_recorded, BalanceType.LIABILITIES)

    def get_scheduled_liabilities(self, data: pd.DataFrame):
        """Filter data for only scheduled liabilities"""
        all_scheduled = self._get_scheduled(data, True)
        return self._get_type(all_scheduled, BalanceType.LIABILITIES)
