"""
TransactionData
"""
from typing import List
from core.transaction_data_item import TransactionDataItem
from dataclasses import dataclass

@dataclass
class TransactionData:
    items: List[TransactionDataItem] = []