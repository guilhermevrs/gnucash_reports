from datetime import datetime
from decimal import Decimal
import pandas as pd
import pytest
from components.transactions_table_block import TransactionTableComponent, TransactionTableInput


class TestTransactionTableComponent:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        self.component = TransactionTableComponent(input=TransactionTableInput(store_name="", graph_name=""))
        self.dataframe = pd.DataFrame(data={
            'date': [
                datetime(2021, 10, 12),
                datetime(2021, 5, 13)
            ],
            "value": [
                Decimal(3000),
                Decimal(6000)
            ]
        })
        yield  # this is where the testing happens
        # Teardown

    def test_get_filtered_data_none_filter(self):
        """Should return the dataframe as it is when no filter (None) is applied"""
        actual = self.component.get_filtered_data(df=self.dataframe, relayout=None)
        assert actual.size == self.dataframe.size

    def test_get_filtered_data_simple_date_filter(self):
        """Should filter the dataframe, based on Date column, for the ranges"""
        """
        Example: 'xaxis.range[0]': '2022-02-27 11:40:36.7688', 'xaxis.range[1]': '2022-04-18 13:32:55.4874', 'yaxis.range[0]': -43392.49814814815, 'yaxis.range[1]': 12394.12637860082
        """
        relayout = {
            "xaxis.range[0]": "2021-08-10 12:40:36.7886",
            "xaxis.range[1]": "2021-11-10 12:40:36.7886"
        }
        actual = self.component.get_filtered_data(df=self.dataframe, relayout=relayout)
        assert actual.size != self.dataframe.size
        assert len(actual) == 1

    def test_get_filtered_data_invalid_date_filter(self):
        """Should ignore if the relayout doesnt contain valid data
        """
        # Empty relayout
        actual = self.component.get_filtered_data(df=self.dataframe, relayout={})
        assert actual.size == self.dataframe.size

        # Invalid relayout
        actual = self.component.get_filtered_data(df=self.dataframe, relayout={"autosize": True})
        assert actual.size == self.dataframe.size
