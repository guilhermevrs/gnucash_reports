from decimal import Decimal
from core.simple_transaction import SimpleTransaction, TransactionType
from tests.test_piecash_helper import TestPiecashHelper
import pytest

@pytest.fixture(scope="class")
def piecash_helper():
    return TestPiecashHelper()

class TestSimpleTransaction:
    def test_simplify_expense_record(self, piecash_helper):
        expense = piecash_helper.get_expense_record()
        result = SimpleTransaction.simplify_record(expense)
        assert result.value == Decimal('50')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Expenses:Food'
        assert result.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.is_scheduled == False
        assert result.description == "CheckingsExpenseFood1"

    def test_simplify_income_record(self, piecash_helper):
        income = piecash_helper.get_income_record()
        result = SimpleTransaction.simplify_record(income)
        assert result.value == Decimal('400')
        assert result.from_account == 'Incomes:Salary'
        assert result.from_account_guid == '251a9aba30024394b196074e2c4f1630'
        assert result.to_account == 'Assets:Checkings'
        assert result.to_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.transaction_type == TransactionType.INCOME
        assert result.is_scheduled == False
        assert result.description == "CheckingsSalary1"

    def test_simplify_transfer_record(self, piecash_helper):
        transfer = piecash_helper.get_recorded_transfer()
        result = SimpleTransaction.simplify_record(transfer)
        assert result.value == Decimal('666')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Assets:Savings'
        assert result.to_account_guid == 'd4295e1f81ce43ad8bdfa31ec5f38f88'
        assert result.transaction_type == TransactionType.TRANSFER
        assert result.is_scheduled == False
        assert result.description == "CheckingsTransfer"

    def test_simplify_expense_scheduled(self, piecash_helper):
        expense = piecash_helper.get_scheduled_expense()
        result = SimpleTransaction.simplify_scheduled_record(expense)
        assert result.value == Decimal('10')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Expenses:Food'
        assert result.to_account_guid == 'f0071228d4e34548be65bf42f1bcf0fa'
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.is_scheduled == True
        assert result.description == "SampledScheduled"

    def test_simplify_income_scheduled(self, piecash_helper):
        income = piecash_helper.get_scheduled_income()
        result = SimpleTransaction.simplify_scheduled_record(income)
        assert result.value == Decimal('123')
        assert result.from_account == 'Incomes:Salary'
        assert result.from_account_guid == '251a9aba30024394b196074e2c4f1630'
        assert result.to_account == 'Assets:Checkings'
        assert result.to_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.transaction_type == TransactionType.INCOME
        assert result.is_scheduled == True
        assert result.description == "ScheduledIncome"

    def test_simplify_transfer_scheduled(self, piecash_helper):
        transfer = piecash_helper.get_scheduled_transfer()
        result = SimpleTransaction.simplify_scheduled_record(transfer)
        assert result.value == Decimal('546')
        assert result.from_account == 'Assets:Checkings'
        assert result.from_account_guid == '24b92fc00a9440c2856281f6eb093536'
        assert result.to_account == 'Assets:Savings'
        assert result.to_account_guid == 'd4295e1f81ce43ad8bdfa31ec5f38f88'
        assert result.transaction_type == TransactionType.TRANSFER
        assert result.is_scheduled == True
        assert result.description == "ScheduledTransfer"

    def test_get_dataframe(self):
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