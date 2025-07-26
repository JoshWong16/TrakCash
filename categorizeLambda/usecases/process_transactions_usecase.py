import uuid
from typing import List
from models import Transaction
from persistence.s3 import TransactionFileReader
from persistence.dynamodb import TransactionDAO, CategoryDAO
from external import BedrockClient


class ProcessTransactionsUsecase:
    def __init__(self):
        self.file_reader = TransactionFileReader()
        self.transaction_dao = TransactionDAO()
        self.category_dao = CategoryDAO()
        self.bedrock_client = BedrockClient()
    
    def execute(self, bucket: str, key: str, user_id: str) -> None:
        """Main use case: process CSV file and categorize transactions"""
        try:
            print(f"Processing CSV file: s3://{bucket}/{key} for user {user_id}")
            
            # 1. Read CSV file from S3
            csv_data = self.file_reader.read_csv_transactions(bucket, key)
            
            if not csv_data:
                print("No transactions found in CSV file")
                return
            
            # 2. Convert to Transaction models with generated IDs
            transactions = []
            for row in csv_data:
                transaction_id = str(uuid.uuid4())
                transaction = Transaction.from_csv_row(row, transaction_id, user_id)
                transactions.append(transaction)
            
            print(f"Created {len(transactions)} transaction objects")
            
            # 3. Save transactions to DynamoDB
            self.transaction_dao.batch_create_transactions(transactions)
            
            # 4. Get user categories
            user_categories = self.category_dao.get_user_categories(user_id)
            if not user_categories:
                raise ValueError(f"No categories found for user {user_id}. User must set up categories before processing transactions.")
            
            # 5. Categorize transactions using Bedrock
            categorized_transactions = self.bedrock_client.categorize_transactions(
                transactions, 
                user_categories.to_formatted_string()
            )
            
            # TODO: Update transactions in DynamoDB with categories
            
            print(f"Successfully processed {len(transactions)} transactions for user {user_id}")
            
        except Exception as e:
            print(f"Error in ProcessTransactionsUsecase: {str(e)}")
            raise