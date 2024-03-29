from datetime import date
from components.transaction_store_block import TransactionStoreInput
from components.transactions_table_block import TransactionTableComponent, TransactionTableInput
from core.transaction_journal import TransactionJournal, TransactionJournalConfig
import piecash

import dash
from dash import html, dash_table as dt
import pandas as pd

from components import ForecastComponent, ForecastComponentInput, TransactionStore
from core.typings import BalanceType


def dash_test():

    app = dash.Dash(__name__)

    book = piecash.open_book(
        "/Users/guilherme.vieiraschwade/Documents/Personal/Gnucash/personal-sqlite.gnucash", open_if_lock=True)
    config = TransactionJournalConfig(
        checkings_parent_guid="3838edd7804247868ebed2d2404d4c26",
        liabilities_parent_guid="44a238b52fdd44c6bad26b9eb5efc219"
    )
    journal = TransactionJournal(book=book, config=config)

    transaction_data = journal.get_transaction_data(date(2023, 1, 1), date(2023, 8, 1))

    transaction_store = TransactionStore(input=TransactionStoreInput(data=transaction_data))
    forecast = ForecastComponent(app=app, input=ForecastComponentInput(store_name=transaction_store.get_name()))
    table = TransactionTableComponent(app=app, input=TransactionTableInput(
        store_name=transaction_store.get_name(),
        graph_name=forecast.get_name()
    ))

    app.layout = html.Div([
        html.Div(id="store-container"),
        html.Div(id="graph-container"),
        html.Div(id="table-container")
    ])

    app.layout["graph-container"] = forecast.layout
    app.layout["table-container"] = table.layout
    app.layout["store-container"] = transaction_store.layout

    app.run_server(debug=True)


def component_test():
    app = dash.Dash(__name__)

    d = {
        'date': [1, 2],
        'balance': [100, 111],
        'scheduled': [False, True],
        'type': [BalanceType.CHECKINGS, BalanceType.LIABILITIES]
    }
    data = pd.DataFrame(data=d)

    data['type'] = data['type'].map({
        BalanceType.CHECKINGS: 'Checkings',
        BalanceType.LIABILITIES: 'Liabilities'
    })

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
