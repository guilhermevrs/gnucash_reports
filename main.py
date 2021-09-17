from datetime import date
from core.transaction_journal import TransactionJournal
import piecash
from piecash.core.transaction import ScheduledTransaction

def main():
    print('# Opening file')

    book = piecash.open_book("/mnt/c/Users/guilh/Documents/Gnucash/test_sqllite/test_sqllite.gnucash")

    journal = TransactionJournal(book)

    transactions = journal.get_recorded_transactions(date(2021, 9, 10), date(2021, 9, 20))

    scheduled_transactions = journal.get_scheduled_transactions(date(2021, 9, 10), date(2021, 10, 20))

    print(book.root_account)

    for acc in book.root_account.children:
        print(acc)

    scheduled = book.get(ScheduledTransaction)

    for tr in scheduled.all():
        print(tr)


if __name__ == "__main__":
    # execute only if run as a script
    main()