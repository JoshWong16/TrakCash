from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CategoryGroup:
    category: str
    subcategories: List[str]


@dataclass
class UserCategories:
    user_id: str
    categories: List[CategoryGroup]
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'UserCategories':
        user_id = item['userId']
        raw_categories = item.get('categories', [])
        
        # Convert flattened categories to grouped format
        category_groups = {}
        for cat_item in raw_categories:
            category = cat_item['category']
            subcategory = cat_item['subcategory']
            
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(subcategory)
        
        categories = [
            CategoryGroup(category=cat, subcategories=subcats)
            for cat, subcats in category_groups.items()
        ]
        
        return cls(user_id=user_id, categories=categories)
    
    def to_formatted_string(self) -> str:
        """Format categories for LLM consumption"""
        formatted = ""
        for category_group in self.categories:
            formatted += f"\n{category_group.category}:\n"
            for subcategory in category_group.subcategories:
                formatted += f"  - {subcategory}\n"
        return formatted.strip()