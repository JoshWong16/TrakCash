import os
import boto3
from typing import List
from models.transaction import Transaction


class TransactionDAO:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('TRANSACTIONS_TABLE', 'trakcash-transactions')
        self.table = self.dynamodb.Table(self.table_name)
    
    def batch_create_transactions(self, transactions: List[Transaction]) -> None:
        """Batch write transactions to DynamoDB"""
        try:
            print(f"Writing {len(transactions)} transactions to DynamoDB")
            
            with self.table.batch_writer() as batch:
                for transaction in transactions:
                    batch.put_item(Item=transaction.to_dynamodb_item())
            
            print(f"Successfully wrote {len(transactions)} transactions to DynamoDB")
            
        except Exception as e:
            print(f"Error writing transactions to DynamoDB: {str(e)}")
            raise
    
    def get_pending_transactions_by_user(self, user_id: str) -> List[dict]:
        """Get all pending transactions for a user"""
        try:
            response = self.table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='userId = :userId',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':userId': user_id, ':status': 'PENDING'}
            )
            return response.get('Items', [])
            
        except Exception as e:
            print(f"Error getting pending transactions: {str(e)}")
            raise