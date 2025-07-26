import json
import boto3
from typing import Dict, List, Any

class BedrockCategorizer:
    def __init__(self, model_id: str = None):
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.model_id = model_id or 'anthropic.claude-3-haiku-20240307-v1:0'
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
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
                
                transaction_map = {t.get('transaction_id', ''): t for t in transactions}
                
                for cat_transaction in categorized_data.get('categorizedTransactions', []):
                    transaction_id = cat_transaction.get('transaction_id', '')
                    if transaction_id in transaction_map:
                        transaction_map[transaction_id]['category'] = cat_transaction.get('category')
                        transaction_map[transaction_id]['subcategory'] = cat_transaction.get('subcategory')
                        transaction_map[transaction_id]['confidence'] = cat_transaction.get('confidence')
                
                print(f"Successfully categorized {len(categorized_data.get('categorizedTransactions', []))} transactions")
                print(list(transaction_map.values()))
                return list(transaction_map.values())
            else:
                print(f"Failed to extract JSON from Bedrock response: {text_content}")
                raise Exception(f"Failed to extract JSON from Bedrock response: {text_content}")
        except Exception as e:
            print(f"Error categorizing transactions: {str(e)}")
            raise

    def create_bedrock_prompt(self, transactions: List[Dict[str, Any]], categories: List[str]) -> str:
        transactions_str = json.dumps(transactions, indent=2)
        categories_str = json.dumps(categories, indent=2)
        
        prompt = f"""
        You are a financial transaction categorization expert. Your task is to categorize transactions into the provided categories and subcategories.

        AVAILABLE CATEGORIES AND SUBCATEGORIES:
        {categories_str}

        IMPORTANT INSTRUCTIONS:
        - You MUST assign both a category AND a subcategory for each transaction
        - The subcategory must be one of the options listed under the chosen category
        - If unsure, set the category and subcategory to be blank set confidence to 0

        Return ONLY a JSON object with this exact structure:
        {{
        "categorizedTransactions": [
            {{
            "transaction_id": "transaction_id",
            "date": "Transaction date",
            "category": "Food",
            "subcategory": "Groceries",
            "confidence": 0.95
            }}
        ]
        }}

        TRANSACTIONS TO CATEGORIZE:
        {transactions_str}
        """
        
        return prompt
