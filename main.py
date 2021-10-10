from datetime import date
from core.simple_transaction import SimpleTransaction, TransactionType
from core.transaction_journal import TransactionJournal
import piecash
from piecash.core.transaction import ScheduledTransaction

import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Scheduled: credit is when you lose, debit is when you receive

def piecash_test():
    print('# Opening file')
    book = piecash.open_book("/mnt/c/Users/guilh/Documents/Gnucash/test_sqllite/test_sqllite.gnucash")
    journal = TransactionJournal(book)
    transactions = journal.get_recorded_transactions(date(2021, 10, 1), date(2021, 10, 30))
    scheduled_transactions = journal.get_scheduled_transactions(date(2021, 10, 1), date(2021, 10, 30))
    for acc in book.root_account.children:
        print(acc)
    scheduled = book.get(ScheduledTransaction)
    for tr in scheduled.all():
        print(tr)

def dash_test():

    app = dash.Dash(__name__)

    book = piecash.open_book("/mnt/c/Users/guilh/Documents/Gnucash/test_sqllite/test_sqllite.gnucash")
    journal = TransactionJournal(book)

    transaction_data = journal.get_transaction_data(date(2021, 10, 1), date(2021, 10, 30))
    df = transaction_data.get_dataframe()

    fig = px.line(df.sort_values(by="date"), x="date", y="value", color="transaction_type", symbol="transaction_type", markers=True)

    app.layout = html.Div(children=[
        html.H1(children='Test'),

        html.Div(children='''
            Dash: A web application framework for your data.
        '''),

        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ])
    app.run_server(debug=True)
 

if __name__ == "__main__":
    # execute only if run as a script
    dash_test()
    # piecash_test()