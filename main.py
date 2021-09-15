import piecash
from piecash.core.transaction import ScheduledTransaction

def main():
    print('# Opening file')

    book = piecash.open_book("/mnt/c/Users/guilh/Documents/Gnucash/test_sqllite/test_sqllite.gnucash")

    print(book.root_account)

    for acc in book.root_account.children:
        print(acc)

    scheduled = book.get(ScheduledTransaction)

    for tr in scheduled.all():
        print(tr)


if __name__ == "__main__":
    # execute only if run as a script
    main()