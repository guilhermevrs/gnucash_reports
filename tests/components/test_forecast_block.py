import pytest
import pandas as pd

from components.forecast_block import ForecastComponent, ForecastComponentInput
from core.typings import BalanceType


class TestForecastComponent:

    @pytest.fixture(autouse=True)
    def before_each(self):
        """Fixture to execute asserts before and after a test is run"""
        # Setup
        d = {
            'date': [1, 2, 3, 4, 5],
            'balance': [3, 4, 5, 6, 7],
            'type': [
                BalanceType.CHECKINGS,
                BalanceType.LIABILITIES,
                BalanceType.CHECKINGS,
                BalanceType.CHECKINGS,
                BalanceType.LIABILITIES
            ],
            'scheduled': [False, False, True, False, True]
        }
        self.data = pd.DataFrame(data=d)
        yield  # this is where the testing happens
        # Teardown

    def test_get_recorded_checkings(self):
        """Should return only the recorded tx for checkings"""

        c = ForecastComponent(input=ForecastComponentInput(data=self.data))

        result = c.get_recorded_checkings(self.data)

        assert len(result) == 2
        assert result['date'].array == [1, 4]

    def test_get_scheduled_checkings(self):
        """Should return only the scheduled tx for checkings"""

        c = ForecastComponent(input=ForecastComponentInput(data=self.data))

        result = c.get_scheduled_checkings(self.data)

        assert len(result) == 1
        assert result['date'].array == [3]

    def test_get_recorded_liabilities(self):
        """Should return only the recorded tx for liabilities"""

        c = ForecastComponent(input=ForecastComponentInput(data=self.data))

        result = c.get_recorded_liabilities(self.data)

        assert len(result) == 1
        assert result['date'].array == [2]

    def test_get_scheduled_liabilities(self):
        """Should return only the scheduled tx for liabilities"""

        c = ForecastComponent(input=ForecastComponentInput(data=self.data))

        result = c.get_scheduled_liabilities(self.data)

        assert len(result) == 1
        assert result['date'].array == [5]