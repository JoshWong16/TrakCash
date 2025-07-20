import json
import boto3
from typing import Dict, List, Any

class BedrockCategorizer:
    """Class for handling transaction categorization using Amazon Bedrock."""
    
    def __init__(self, model_id: str = None):
        """Initialize the BedrockCategorizer with AWS Bedrock client and model ID."""
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.model_id = model_id or 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
        """Categorize transactions using Amazon Bedrock."""
        try:
            print(f"Categorizing {len(transactions)} transactions")
            
            prompt = self.create_bedrock_prompt(transactions, categories)
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read().decode())
            content = response_body.get('content', [])
            
            text_content = ""
            for block in content:
                if block.get('type') == 'text':
                    text_content += block.get('text', '')
            
            json_start = text_content.find('{')
            json_end = text_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text_content[json_start:json_end]
                categorized_data = json.loads(json_str)
                
                transaction_map = {t.get('description', ''): t for t in transactions}
                
                for cat_transaction in categorized_data.get('categorizedTransactions', []):
                    description = cat_transaction.get('description', '')
                    if description in transaction_map:
                        transaction_map[description]['category'] = cat_transaction.get('category', 'Miscellaneous')
                        transaction_map[description]['confidence'] = cat_transaction.get('confidence', 0.0)
                
                print(f"Successfully categorized {len(categorized_data.get('categorizedTransactions', []))} transactions")
                return list(transaction_map.values())
            else:
                print(f"Failed to extract JSON from Bedrock response: {text_content}")
                for transaction in transactions:
                    transaction['category'] = 'Miscellaneous'
                    transaction['confidence'] = 0.0
                return transactions
        except Exception as e:
            print(f"Error categorizing transactions: {str(e)}")
            for transaction in transactions:
                transaction['category'] = 'Miscellaneous'
                transaction['confidence'] = 0.0
            return transactions

    def create_bedrock_prompt(self, transactions: List[Dict[str, Any]], categories: List[str]) -> str:
        """Create a prompt for Amazon Bedrock to categorize transactions."""
        transactions_str = json.dumps(transactions, indent=2)
        categories_str = json.dumps(categories, indent=2)
        
        prompt = f"""
        You are a financial transaction categorization expert. Your task is to categorize the following transactions into the provided categories.

        CATEGORIES:
        {categories_str}

        TRANSACTIONS:
        {transactions_str}

        For each transaction, analyze the description, amount, and date to determine the most appropriate category.
        Return your categorization as a JSON object with the following structure:
        {{
          "categorizedTransactions": [
            {{
              "description": "Transaction description",
              "amount": "Transaction amount",
              "date": "Transaction date",
              "category": "Assigned category",
              "confidence": 0.95
            }},
            ...
          ]
        }}

        The confidence score should be between 0 and 1, indicating how confident you are in the categorization.
        Only return the JSON object, no additional text.
        """
        
        return prompt
