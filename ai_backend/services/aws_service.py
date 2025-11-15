"""
AWS S3 Service
==============

Manages all AWS S3 operations for file storage.
"""

import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

                                                                                    
class AWSService:
    """
    AWS S3 operations handler
    
    Provides methods for:
    - Bucket management
    - File upload/download
    - File deletion                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    - Public access configuration
    """
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1"
    ):
        """
        Initialize AWS S3 service
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.region = region
        
        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            logger.info(f"✅ AWS S3 client initialized (bucket: {bucket_name}, region: {region})")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test if AWS credentials are valid and bucket is accessible
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ Successfully connected to bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ Bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                logger.error(f"❌ Access denied to bucket '{self.bucket_name}'")
            else:
                logger.error(f"❌ Connection error: {e}")
            return False
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        make_public: bool = True
    ) -> Optional[str]:
        """
        Upload file to S3 bucket (without ACLs)
        
        Args:
            file_path: Local file path to upload
            object_name: S3 object name (defaults to filename)
            make_public: Whether to make file publicly accessible (handled by bucket policy)
            
        Returns:
            Public URL of uploaded file, or None if failed
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            # Determine content type
            content_type = 'image/jpeg'
            if file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.webp'):
                content_type = 'image/webp'
            elif file_path.endswith('.txt'):
                content_type = 'text/plain'
            
            # Upload WITHOUT ACL (relies on bucket policy)
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
            
            logger.info(f"✅ File uploaded: {url}")
            return url
            
        except FileNotFoundError:
            logger.error(f"❌ File not found: {file_path}")
            return None
        except NoCredentialsError:
            logger.error("❌ AWS credentials not available")
            return None
        except ClientError as e:
            logger.error(f"❌ Upload failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during upload: {e}")
            return None
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[str]:
        """
        List files in bucket with optional prefix filter
        
        Args:
            prefix: Filter files by prefix
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                logger.info(f"📋 Listed {len(files)} files with prefix '{prefix}'")
                return files
            else:
                logger.info(f"📋 No files found with prefix '{prefix}'")
                return []
        except ClientError as e:
            logger.error(f"❌ List failed: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error during listing: {e}")
            return []
    
    def get_file_url(self, object_name: str) -> str:
        """
        Get public URL for an object
        
        Args:
            object_name: S3 object key
            
        Returns:
            Public URL
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in bucket
        
        Args:
            object_name: S3 object key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError:
            return False


# ===================================================================
# Global Instance Management
# ===================================================================
_aws_service_instance: Optional[AWSService] = None


def init_aws_service(
    access_key: str,
    secret_key: str,
    bucket: str,
    region: str
) -> AWSService:
    """
    Initialize global AWS service instance
    
    Args:
        access_key: AWS access key ID
        secret_key: AWS secret access key
        bucket: S3 bucket name
        region: AWS region
        
    Returns:
        AWSService instance
    """
    global _aws_service_instance
    _aws_service_instance = AWSService(access_key, secret_key, bucket, region)
    return _aws_service_instance


def get_aws_service() -> AWSService:
    """
    Get global AWS service instance
    
    Returns:
        AWSService instance
        
    Raises:
        RuntimeError: If service not initialized
    """
    if _aws_service_instance is None:
        raise RuntimeError(
            "AWS service not initialized. "
            "Call init_aws_service() first or check your .env configuration."
        )
    return _aws_service_instance


def reset_aws_service():
    """Reset global AWS service instance (for testing)"""
    global _aws_service_instance
    _aws_service_instance = None