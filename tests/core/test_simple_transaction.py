from decimal import Decimal

import pandas as pd
from core.simple_transaction import SimpleTransaction
from core.typings import TransactionType
from tests.test_piecash_helper import TestPiecashHelper
import pytest


@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()


class TestSimpleTransaction:
    def test_simplify_expense_record(self, piecash_helper):
        """
        should correctly simplify an expense record
        """
        expense = piecash_helper.get_expense_record()
        result = SimpleTransaction.simplify_record(expense)[0]
        assert result.value == Decimal('50')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Expenses:Food'
        assert result.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.is_scheduled is False
        assert result.description == "CheckingsExpenseFood1"

    def test_simplify_income_record(self, piecash_helper):
        """
        should correctly simplify an income record
        """
        income = piecash_helper.get_income_record()
        result = SimpleTransaction.simplify_record(income)[0]
        assert result.value == Decimal('400')
        assert result.from_account == 'Incomes:Salary'
        assert result.from_account_guid == '251a9aba30024394b196074e2c4f1630'
        assert result.to_account == 'Assets:Checkings'
        assert result.to_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.transaction_type == TransactionType.INCOME
        assert result.is_scheduled is False
        assert result.description == "CheckingsSalary1"

    def test_simplify_transfer_record(self, piecash_helper):
        """
        should correctly simplify a transfer record
        """
        transfer = piecash_helper.get_recorded_transfer()
        result = SimpleTransaction.simplify_record(transfer)[0]
        assert result.value == Decimal('666')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Assets:Savings'
        assert result.to_account_guid == 'd4295e1f81ce43ad8bdfa31ec5f38f88'
        assert result.transaction_type == TransactionType.TRANSFER
        assert result.is_scheduled is False
        assert result.description == "CheckingsTransfer"

    def test_simplify_expense_scheduled(self, piecash_helper):
        """
        should correctly simplify a scheduled expense
        """
        expense = piecash_helper.get_scheduled_expense()
        result = SimpleTransaction.simplify_scheduled_record(expense)[0]
        assert result.value == Decimal('10')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Expenses:Food'
        assert result.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.is_scheduled is True
        assert result.description == "SampledScheduled"

    def test_simplify_income_scheduled(self, piecash_helper):
        """
        should correctly simplify a scheduled income
        """
        income = piecash_helper.get_scheduled_income()
        result = SimpleTransaction.simplify_scheduled_record(income)[0]
        assert result.value == Decimal('123')
        assert result.from_account == 'Incomes:Salary'
        assert result.from_account_guid == '251a9aba30024394b196074e2c4f1630'
        assert result.to_account == 'Assets:Checkings'
        assert result.to_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.transaction_type == TransactionType.INCOME
        assert result.is_scheduled is True
        assert result.description == "ScheduledIncome"

    def test_simplify_transfer_scheduled(self, piecash_helper):
        """
        should correctly simplify a scheduled transfer
        """
        transfer = piecash_helper.get_scheduled_transfer()
        result = SimpleTransaction.simplify_scheduled_record(transfer)[0]
        assert result.value == Decimal('546')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Assets:Savings'
        assert result.to_account_guid == 'd4295e1f81ce43ad8bdfa31ec5f38f88'
        assert result.transaction_type == TransactionType.TRANSFER
        assert result.is_scheduled is True
        assert result.description == "ScheduledTransfer"

    def test_simplify_liability(self, piecash_helper: TestPiecashHelper):
        """
        should correctly simplify a liability record
        """
        transfer = piecash_helper.get_recorded_liability()
        result = SimpleTransaction.simplify_record(transfer)[0]
        assert result.value == Decimal('100')
        assert result.from_account == 'Liabilities:Credit card'
        assert result.from_account_guid == '755b41d407b94745aa463749cf462f23'
        assert result.to_account == 'Expenses:Food'
        assert result.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert result.transaction_type == TransactionType.LIABILITY
        assert result.is_scheduled is False
        assert result.description == "ExpenseLiability"

    def test_simplify_quittance(self, piecash_helper: TestPiecashHelper):
        """
        should correctly simplify a quittance record
        """
        transfer = piecash_helper.get_credit_card_record()
        result = SimpleTransaction.simplify_record(transfer)[0]
        assert result.value == Decimal('50')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Liabilities:Credit card'
        assert result.to_account_guid == '755b41d407b94745aa463749cf462f23'
        assert result.transaction_type == TransactionType.QUITTANCE
        assert result.is_scheduled is False
        assert result.description == "CheckingsExpenseCreditCard"

    def test_simplify_split_record(self, piecash_helper: TestPiecashHelper):
        split_transfer = piecash_helper.get_split_transaction()
        result = SimpleTransaction.simplify_record(split_transfer)

        item1 = result[0]
        assert item1.value == Decimal('50')
        assert item1.from_account == 'Assets:Checkings'
        assert item1.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert item1.to_account == 'Expenses:Food'
        assert item1.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert item1.transaction_type == TransactionType.EXPENSE
        assert item1.is_scheduled is False
        assert item1.description == "SplitTransferName1"

        item2 = result[1]
        assert item2.value == Decimal('60')
        assert item2.from_account == 'Assets:Checkings'
        assert item2.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert item2.to_account == 'Expenses:Food'
        assert item2.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert item2.transaction_type == TransactionType.EXPENSE
        assert item2.is_scheduled is False
        assert item2.description == "SplitTransferName1"
        pass

    def test_get_dataframe(self):
        """
        should correctly returns a dataframe row
        """
        transaction = SimpleTransaction(
            value=0,
            description="Example",
            from_account="Account1",
            from_account_guid="Account1Guid",
            to_account="Account2",
            to_account_guid="Account2Guid",
            transaction_type=TransactionType.EXPENSE,
            is_scheduled=False)

        df = transaction.get_dataframe()

        assert len(df.columns) == 8

    def test_get_dataframe_balance(self):
        """
        should correctly set the value and is_scheduled columns
        """
        transaction = SimpleTransaction(value=12)

        df = transaction.get_dataframe()

        assert len(df.columns) == 2
        assert df["value"][0] == 12
        assert not df["is_scheduled"][0]

    def test_from_series(self):
        """
        should load a SimpleTransaction from a Series
        """
        series = pd.Series(data={
            "description": "My trx description",
            "value": Decimal(432),
            "is_scheduled": True,
            "from_account": "Payment account",
            "from_account_guid": "123456",
            "to_account": "Expense account",
            "to_account_guid": "654321",
            "transaction_type": TransactionType.EXPENSE
        })
        transaction = SimpleTransaction.from_series(series)

        assert transaction.description == "My trx description"
        assert transaction.from_account == "Payment account"
        assert transaction.from_account_guid == "123456"
        assert transaction.to_account == "Expense account"
        assert transaction.to_account_guid == "654321"
        assert transaction.transaction_type == TransactionType.EXPENSE
        assert transaction.value == Decimal(432)
        assert transaction.is_scheduled == True  # noqa E712
