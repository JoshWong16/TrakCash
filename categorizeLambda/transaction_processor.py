import json
import os
import csv
import uuid
import boto3
import datetime
from io import StringIO
from typing import Dict, List, Any
from bedrock_categorizer import BedrockCategorizer

class TransactionProcessor:
    def __init__(self):
        """Initialize the TransactionProcessor with AWS clients and environment variables."""
        self.s3_client = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        
        self.TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE', 'trakcash-transactions')
        self.CATEGORIES_TABLE = os.environ.get('CATEGORIES_TABLE', 'trakcash-categories')
        self.TRANSACTION_BUCKET = os.environ.get('TRANSACTION_BUCKET', 'trakcash-transaction-uploads')
        self.BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
        self.transactions_table = self.dynamodb.Table(self.TRANSACTIONS_TABLE)
        self.categories_table = self.dynamodb.Table(self.CATEGORIES_TABLE)
        
        # Initialize the Bedrock categorizer
        self.bedrock_categorizer = BedrockCategorizer(self.BEDROCK_MODEL_ID)

    def process_csv_file(self, bucket: str, key: str, user_id: str):
        """Process a CSV file containing transactions."""
        try:
            print(f"Processing CSV file: s3://{bucket}/{key} for user {user_id}")
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            csv_content = response['Body'].read().decode('utf-8')
            
            csv_reader = csv.DictReader(StringIO(csv_content))
            transactions = list(csv_reader)
            
            if not transactions:
                print("No transactions found in CSV file")
                return
            
            print(f"Found {len(transactions)} transactions in CSV file")
            
            self.batch_write_transactions(transactions, user_id)
            
            categories = self.get_user_categories(user_id)
            
            if not categories:
                print(f"No categories found for user {user_id}")
                return
            
            categorized_transactions = self.categorize_transactions(transactions, categories)
            
            self.update_transactions_with_categories(categorized_transactions, user_id)
            
            print(f"Successfully processed {len(transactions)} transactions for user {user_id}")
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            raise

    def batch_write_transactions(self, transactions: List[Dict[str, Any]], user_id: str):
        """Write transactions to DynamoDB with status "PENDING"."""
        try:
            print(f"Writing {len(transactions)} transactions to DynamoDB")
            
            timestamp = datetime.datetime.now().isoformat()
            
            with self.transactions_table.batch_writer() as batch:
                for transaction in transactions:
                    transaction_id = str(uuid.uuid4())
                    
                    item = {
                        'transactionId': transaction_id,
                        'processingDate': timestamp,
                        'userId': user_id,
                        'status': 'PENDING',
                        'pendingValidation': 'true',
                        'amount': transaction.get('amount', '0'),
                        'date': transaction.get('date', ''),
                        'description': transaction.get('description', ''),
                        'originalData': json.dumps(transaction)
                    }
                    
                    batch.put_item(Item=item)
            
            print(f"Successfully wrote {len(transactions)} transactions to DynamoDB")
        except Exception as e:
            print(f"Error writing transactions to DynamoDB: {str(e)}")
            raise

    def get_user_categories(self, user_id: str) -> List[str]:
        """Get categories for a user from DynamoDB."""
        try:
            print(f"Getting categories for user {user_id}")
            
            response = self.categories_table.get_item(Key={'userId': user_id})
            
            categories = response.get('Item', {}).get('categories', [])
            
            if not categories:
                categories = [
                    "Housing", "Transportation", "Food", "Utilities", 
                    "Insurance", "Healthcare", "Savings", "Personal", 
                    "Entertainment", "Miscellaneous"
                ]
            
            print(f"Found {len(categories)} categories for user {user_id}")
            return categories
        except Exception as e:
            print(f"Error getting categories for user {user_id}: {str(e)}")
            return [
                "Housing", "Transportation", "Food", "Utilities", 
                "Insurance", "Healthcare", "Savings", "Personal", 
                "Entertainment", "Miscellaneous"
            ]

    def categorize_transactions(self, transactions: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
        """Categorize transactions using Amazon Bedrock via the BedrockCategorizer."""
        return self.bedrock_categorizer.categorize_transactions(transactions, categories)

    def update_transactions_with_categories(self, transactions: List[Dict[str, Any]], user_id: str):
        """Update transactions in DynamoDB with categories and status "COMPLETE"."""
        try:
            print(f"Updating {len(transactions)} transactions with categories")
            
            response = self.transactions_table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='userId = :userId',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':userId': user_id, ':status': 'PENDING'}
            )
            
            pending_transactions = response.get('Items', [])
            
            description_to_id = {
                item.get('description', ''): item.get('transactionId')
                for item in pending_transactions
            }
            
            for transaction in transactions:
                description = transaction.get('description', '')
                transaction_id = description_to_id.get(description)
                
                if not transaction_id:
                    print(f"No pending transaction found for description: {description}")
                    continue
                
                self.transactions_table.update_item(
                    Key={
                        'transactionId': transaction_id,
                        'processingDate': pending_transactions[0].get('processingDate')
                    },
                    UpdateExpression='SET #category = :category, #confidence = :confidence, #status = :status, #pendingValidation = :pendingValidation',
                    ExpressionAttributeNames={
                        '#category': 'category',
                        '#confidence': 'confidence',
                        '#status': 'status',
                        '#pendingValidation': 'pendingValidation'
                    },
                    ExpressionAttributeValues={
                        ':category': transaction.get('category', 'Miscellaneous'),
                        ':confidence': transaction.get('confidence', 0.0),
                        ':status': 'COMPLETE',
                        ':pendingValidation': 'false'
                    }
                )
            
            print(f"Successfully updated {len(transactions)} transactions with categories")
        except Exception as e:
            print(f"Error updating transactions with categories: {str(e)}")
            raise
