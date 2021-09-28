from datetime import date
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

app = dash.Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

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


if __name__ == "__main__":
    # execute only if run as a script
    # app.run_server(debug=True)
    piecash_test()