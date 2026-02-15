"""S3 utility functions for video storage."""

import logging
from typing import Optional
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Client:
    """Enhanced S3 client with error handling."""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """Initialize S3 client."""
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region)
        self.s3_resource = boto3.resource('s3', region_name=region)
    
    def generate_presigned_upload_url(
        self, 
        object_key: str, 
        content_type: str,
        expires_in: int = 3600,
        max_file_size: int = 2_147_483_648  # 2GB
    ) -> Optional[str]:
        """Generate presigned URL for direct upload."""
        try:
            conditions = [
                {"acl": "private"},
                ["content-length-range", 1, max_file_size],
                ["starts-with", "$Content-Type", content_type.split('/')[0] + '/']
            ]
            
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=object_key,
                Fields={
                    "acl": "private",
                    "Content-Type": content_type
                },
                Conditions=conditions,
                ExpiresIn=expires_in
            )
            
            logger.debug(f"Generated presigned upload URL for: {object_key}")
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned upload URL: {e}")
            return None
    
    def generate_presigned_download_url(
        self, 
        object_key: str, 
        expires_in: int = 3600
    ) -> Optional[str]:
        """Generate presigned URL for download."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expires_in
            )
            
            logger.debug(f"Generated presigned download URL for: {object_key}")
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned download URL: {e}")
            return None
    
    def object_exists(self, object_key: str) -> bool:
        """Check if object exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking object existence: {e}")
            return False
    
    def delete_object(self, object_key: str) -> bool:
        """Delete object from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.debug(f"Successfully deleted object: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting object {object_key}: {e}")
            return False
    
    def get_object_metadata(self, object_key: str) -> Optional[dict]:
        """Get object metadata."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return {
                'size': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            logger.error(f"Error getting object metadata {object_key}: {e}")
            return None


def generate_video_key(user_id: str, project_id: str, video_id: str, filename: str) -> str:
    """Generate S3 key for video storage."""
    # Format: videos/{user_id}/{project_id}/{video_id}/{filename}
    safe_filename = quote(filename, safe='')
    return f"videos/{user_id}/{project_id}/{video_id}/{safe_filename}"


def generate_transcript_key(user_id: str, project_id: str, video_id: str) -> str:
    """Generate S3 key for transcript storage."""
    return f"transcripts/{user_id}/{project_id}/{video_id}.json"


# Bucket name constants
VIDEOS_BUCKET = "content-forge-videos"
TRANSCRIPTS_BUCKET = "content-forge-transcripts"
