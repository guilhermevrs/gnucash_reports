from datetime import date


class MockRecurrence():

    def __init__(self) -> None:
        self.recurrence_mult = 1
        self.recurrence_period_type = "month"
        self.recurrence_period_start = date(2020, 1, 1)
        self.recurrence_weekend_adjust = "none"
