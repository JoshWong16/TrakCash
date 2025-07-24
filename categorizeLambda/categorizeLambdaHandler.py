import json
from transaction_processor import TransactionProcessor

# Initialize the transaction processor
processor = TransactionProcessor()

def handler(event, context):
    """
    Lambda handler for processing transaction CSV files.
    
    1. Processes SQS messages containing S3 event notifications
    2. Reads CSV files from S3
    3. Writes transactions to DynamoDB with status "PENDING"
    4. Gets categories from the categories DynamoDB table
    5. Uses Amazon Bedrock to categorize transactions
    6. Updates transactions in DynamoDB with categories and status "COMPLETE"
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        for record in event.get('Records', []):
            body = json.loads(record.get('body', '{}'))
            
            for s3_record in body.get('Records', []):
                bucket = s3_record.get('s3', {}).get('bucket', {}).get('name')
                key = s3_record.get('s3', {}).get('object', {}).get('key')
                
                if not bucket or not key:
                    print(f"Invalid S3 event record: {s3_record}")
                    continue
                
                user_id = key.split('/')[0] if '/' in key else 'unknown'
                
                processor.process_csv_file(bucket, key, user_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed transactions',
            })
        }
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error processing transactions: {str(e)}',
            })
        }
