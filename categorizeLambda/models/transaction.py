from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    date: str
    amount: str
    merchant: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence: Optional[float] = None
    
    @classmethod
    def from_csv_row(cls, row: dict, transaction_id: str, user_id: str) -> 'Transaction':
        return cls(
            transaction_id=transaction_id,
            user_id=user_id,
            date=row.get('date', ''),
            amount=row.get('amount', '0'),
            merchant=row.get('merchant', ''),
            description=row.get('description', '')
        )
    
    def to_dynamodb_item(self) -> dict:
        return {
            'userId': self.user_id,
            'transactionDateId': f"{self.date}#{self.transaction_id}",
            'transactionId': self.transaction_id,
            'nonTerminalStatus': 'PENDING',
            'pendingValidation': 'true',
            'amount': self.amount,
            'date': self.date,
            'merchant': self.merchant,
            'description': self.description,
        }
    
    def to_bedrock_dict(self) -> dict:
        return {
            'transaction_id': self.transaction_id,
            'date': self.date,
            'amount': self.amount,
            'merchant': self.merchant,
            'description': self.description
        }