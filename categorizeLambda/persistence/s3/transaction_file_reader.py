import csv
import boto3
from io import StringIO
from typing import List, Dict, Any


class TransactionFileReader:
    def __init__(self):
        self.s3_client = boto3.client('s3')
    
    def read_csv_transactions(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """Read and parse CSV file from S3"""
        try:
            print(f"Reading CSV file: s3://{bucket}/{key}")
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            csv_content = response['Body'].read().decode('utf-8')
            
            csv_reader = csv.DictReader(StringIO(csv_content))
            transactions = list(csv_reader)
            
            print(f"Found {len(transactions)} transactions in CSV file")
            return transactions
            
        except Exception as e:
            print(f"Error reading CSV file from S3: {str(e)}")
            raise