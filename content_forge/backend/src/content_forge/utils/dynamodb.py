"""DynamoDB utility functions and helpers."""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """Enhanced DynamoDB client with retry logic and error handling."""
    
    def __init__(self, table_name: str, region: str = "us-east-1"):
        """Initialize DynamoDB client."""
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.client = boto3.client('dynamodb', region_name=region)
        
    def put_item(self, item: Dict[str, Any]) -> bool:
        """Put item into DynamoDB table with retry logic."""
        try:
            self.table.put_item(Item=item)
            logger.debug(f"Successfully put item: {item.get('pk', 'unknown')}")
            return True
        except ClientError as e:
            logger.error(f"Error putting item: {e}")
            return False
    
    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB table."""
        try:
            response = self.table.get_item(
                Key={'pk': pk, 'sk': sk}
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting item {pk}/{sk}: {e}")
            return None
    
    def query_items(
        self, 
        pk: str, 
        sk_prefix: Optional[str] = None,
        limit: Optional[int] = None,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query items by partition key."""
        try:
            key_condition = 'pk = :pk'
            expression_values = {':pk': pk}
            
            if sk_prefix:
                key_condition += ' AND begins_with(sk, :sk_prefix)'
                expression_values[':sk_prefix'] = sk_prefix
            
            query_params = {
                'KeyConditionExpression': key_condition,
                'ExpressionAttributeValues': expression_values
            }
            
            if limit:
                query_params['Limit'] = limit
            if next_token:
                query_params['ExclusiveStartKey'] = json.loads(next_token)
            
            response = self.table.query(**query_params)
            
            result = {
                'items': response.get('Items', []),
                'next_token': json.dumps(response['LastEvaluatedKey']) if 'LastEvaluatedKey' in response else None
            }
            
            return result
        except ClientError as e:
            logger.error(f"Error querying items: {e}")
            return {'items': [], 'next_token': None}
    
    def update_item(
        self, 
        pk: str, 
        sk: str, 
        update_expression: str,
        expression_values: Dict[str, Any],
        expression_names: Optional[Dict[str, str]] = None
    ) -> bool:
        """Update item in DynamoDB table."""
        try:
            update_params = {
                'Key': {'pk': pk, 'sk': sk},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values
            }
            
            if expression_names:
                update_params['ExpressionAttributeNames'] = expression_names
            
            self.table.update_item(**update_params)
            logger.debug(f"Successfully updated item: {pk}/{sk}")
            return True
        except ClientError as e:
            logger.error(f"Error updating item {pk}/{sk}: {e}")
            return False
    
    def delete_item(self, pk: str, sk: str) -> bool:
        """Delete item from DynamoDB table."""
        try:
            self.table.delete_item(Key={'pk': pk, 'sk': sk})
            logger.debug(f"Successfully deleted item: {pk}/{sk}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting item {pk}/{sk}: {e}")
            return False
    
    def batch_write_items(self, items: List[Dict[str, Any]]) -> bool:
        """Batch write items to DynamoDB table."""
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            logger.debug(f"Successfully batch wrote {len(items)} items")
            return True
        except ClientError as e:
            logger.error(f"Error batch writing items: {e}")
            return False


def model_to_dynamodb_item(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to DynamoDB item format."""
    item = model.dict(exclude_none=True)
    
    # Convert datetime fields to ISO strings
    for key, value in item.items():
        if isinstance(value, datetime):
            item[key] = value.isoformat()
    
    return item


def dynamodb_item_to_model(item: Dict[str, Any], model_class: type) -> BaseModel:
    """Convert DynamoDB item to Pydantic model."""
    # Remove DynamoDB specific fields if present
    cleaned_item = {k: v for k, v in item.items() if not k.startswith('#')}
    
    return model_class(**cleaned_item)


# Table name constants
USERS_TABLE = "content-forge-users"
PROJECTS_TABLE = "content-forge-projects"
