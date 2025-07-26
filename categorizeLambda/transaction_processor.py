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
        self.s3_client = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        
        self.TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE', 'trakcash-transactions')
        self.CATEGORIES_TABLE = os.environ.get('CATEGORIES_TABLE', 'trakcash-categories')
        self.TRANSACTION_BUCKET = os.environ.get('TRANSACTION_BUCKET', 'trakcash-transaction-uploads')
        self.BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        
        self.transactions_table = self.dynamodb.Table(self.TRANSACTIONS_TABLE)
        self.categories_table = self.dynamodb.Table(self.CATEGORIES_TABLE)
        
        self.bedrock_categorizer = BedrockCategorizer(self.BEDROCK_MODEL_ID)

    def process_csv_file(self, bucket: str, key: str, user_id: str):
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
            
            transactions_with_ids = self.batch_write_transactions(transactions, user_id)
            
            categories = self.get_user_categories(user_id)
            
            categorized_transactions = self.categorize_transactions(transactions_with_ids, categories)
            
            # self.update_transactions_with_categories(categorized_transactions, user_id)
            
            print(f"Successfully processed {len(transactions)} transactions for user {user_id}")
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            raise

    def batch_write_transactions(self, transactions: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        try:
            print(f"Writing {len(transactions)} transactions to DynamoDB")
            
            transactions_with_ids = []
        
            with self.transactions_table.batch_writer() as batch:
                for transaction in transactions:
                    transaction_id = str(uuid.uuid4())
                    
                    item = {
                        'userId': user_id,
                        'transactionDateId': transaction.get('date', '') + '#' + transaction_id,
                        'transactionId': transaction_id,
                        'nonTerminalStatus': 'PENDING',
                        'pendingValidation': 'true',
                        'amount': transaction.get('amount', '0'),
                        'date': transaction.get('date', ''),
                        'merchant': transaction.get('merchant', ''),
                        'description': transaction.get('description', ''),
                    }
                    
                    batch.put_item(Item=item)
                    
                    # Add transaction_id to the original transaction data
                    transaction_with_id = transaction.copy()
                    transaction_with_id['transaction_id'] = transaction_id
                    transactions_with_ids.append(transaction_with_id)
            
            print(f"Successfully wrote {len(transactions)} transactions to DynamoDB")
            return transactions_with_ids
        except Exception as e:
            print(f"Error writing transactions to DynamoDB: {str(e)}")
            raise

    def get_user_categories(self, user_id: str) -> str:
        try:
            print(f"Getting categories for user {user_id}")
            
            response = self.categories_table.get_item(Key={'userId': user_id})
            
            categories = response.get('Item', {}).get('categories', [])
            if not categories:
                raise ValueError(f"No categories found for user {user_id}. User must set up categories before processing transactions.")
            
            print(f"Found {len(categories)} categories for user {user_id}")
            
            # Convert flattened categories to readable format
            category_groups = {}
            for item in categories:
                category = item['category']
                subcategory = item['subcategory']
                
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(subcategory)
            
            # Format for LLM
            formatted_categories = ""
            for category, subcategories in category_groups.items():
                formatted_categories += f"\n{category}:\n"
                for subcategory in subcategories:
                    formatted_categories += f"  - {subcategory}\n"
            
            print(f"Formatted categories:\n{formatted_categories}")
            return formatted_categories.strip()
            
        except Exception as e:
            print(f"Error getting categories for user {user_id}: {str(e)}")
            raise

    def categorize_transactions(self, transactions: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
        return self.bedrock_categorizer.categorize_transactions(transactions, categories)

    def update_transactions_with_categories(self, transactions: List[Dict[str, Any]], user_id: str):
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
