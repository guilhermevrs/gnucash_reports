from datetime import date
from core.transaction_journal import TransactionJournal, TransactionJournalConfig
import piecash

import dash
from dash import html, dcc, dash_table as dt
import plotly.graph_objects as go
import pandas as pd

from components import ForecastComponent, ForecastComponentInput
from core.typings import BalanceType


def dash_test():

    app = dash.Dash(__name__)

    book = piecash.open_book(
        "/mnt/c/Users/guilh/Documents/Gnucash/test_sqllite/test_sqllite.gnucash", open_if_lock=True)
    config = TransactionJournalConfig(
        checkings_parent_guid="3838edd7804247868ebed2d2404d4c26",
        liabilities_parent_guid="44a238b52fdd44c6bad26b9eb5efc219"
    )
    journal = TransactionJournal(book=book, config=config)

    transaction_data = journal.get_transaction_data(date(2021, 11, 20), date(2022, 5, 26))
    df = transaction_data.get_balance_data()

    c = ForecastComponent(app=app, input=ForecastComponentInput(data=df))
    app.layout = html.Div([
            html.Div(id="graph-container")
        ]
    )

    app.layout["graph-container"] = c.layout

    app.run_server(debug=True)


def component_test():
    app = dash.Dash(__name__)

    d = {
        'date': [1, 2, 3, 4, 5, 6, 7],
        'balance': [100, 120, 130, 150, 175, 183, 196],
        'scheduled': [False, False, True, False, True, True, True]
    }
    data = pd.DataFrame(data=d)

    # c = ForecastComponent(app=app, input=ForecastComponentInput(data=data))
    app.layout = html.Div([
            html.Div(id="graph-container"),
            dt.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in data.columns],
                data=data.to_dict(orient='records'),
            )
        ]
    )

    # app.layout["graph-container"] = c.layout

    app.run_server(debug=True)


if __name__ == "__main__":
    # execute only if run as a script
    dash_test()
    # piecash_test()
    # component_test()
