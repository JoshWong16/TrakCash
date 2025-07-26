import os
import boto3
from typing import Optional
from models.category import UserCategories


class CategoryDAO:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('CATEGORIES_TABLE', 'trakcash-categories')
        self.table = self.dynamodb.Table(self.table_name)
    
    def get_user_categories(self, user_id: str) -> Optional[UserCategories]:
        """Get categories for a specific user"""
        try:
            print(f"Getting categories for user {user_id}")
            
            response = self.table.get_item(Key={'userId': user_id})
            item = response.get('Item')
            
            if not item or not item.get('categories'):
                return None
            
            user_categories = UserCategories.from_dynamodb_item(item)
            print(f"Found {len(user_categories.categories)} category groups for user {user_id}")
            
            return user_categories
            
        except Exception as e:
            print(f"Error getting categories for user {user_id}: {str(e)}")
            raise