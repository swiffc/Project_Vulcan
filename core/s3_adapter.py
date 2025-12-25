"""
S3 Adapter - Cloud Storage Integration
Upload and download files from AWS S3 or S3-compatible storage.

Path B - Infrastructure Adapter
Enables:
- "Upload this file to S3"
- "Download CAD files from cloud storage"
- "List all files in bucket"
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("core.s3_adapter")


class S3Adapter:
    """
    AWS S3 storage adapter with boto3 integration.
    Supports AWS S3 and S3-compatible services (MinIO, DigitalOcean Spaces, etc.).
    """
    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None
    ):
        """
        Initialize S3 adapter.
        
        Args:
            aws_access_key_id: AWS access key (or from env AWS_ACCESS_KEY_ID)
            aws_secret_access_key: AWS secret key (or from env AWS_SECRET_ACCESS_KEY)
            region_name: AWS region
            endpoint_url: S3-compatible endpoint URL (for MinIO, Spaces, etc.)
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.ClientError = ClientError
            
            # Get credentials from params or environment
            access_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
            
            if not access_key or not secret_key:
                raise ValueError(
                    "AWS credentials not provided. Set AWS_ACCESS_KEY_ID and "
                    "AWS_SECRET_ACCESS_KEY environment variables or pass to constructor."
                )
            
            # Create S3 client
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name,
                endpoint_url=endpoint_url
            )
            
            logger.info(f"S3 adapter initialized (region: {region_name})")
            
        except ImportError:
            raise ImportError(
                "boto3 not installed. Install with: pip install boto3"
            )
    
    def upload_file(
        self,
        local_path: str,
        bucket: str,
        key: Optional[str] = None,
        metadata: Optional[Dict] = None,
        public: bool = False
    ) -> str:
        """
        Upload file to S3.
        
        Args:
            local_path: Path to local file
            bucket: S3 bucket name
            key: S3 object key (defaults to filename)
            metadata: Optional metadata dictionary
            public: Make file publicly readable
        
        Returns:
            S3 URL of uploaded file
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File not found: {local_path}")
        
        # Default key to filename if not provided
        if not key:
            key = Path(local_path).name
        
        # Upload arguments
        extra_args = {}
        
        if metadata:
            extra_args['Metadata'] = metadata
        
        if public:
            extra_args['ACL'] = 'public-read'
        
        try:
            self.s3.upload_file(local_path, bucket, key, ExtraArgs=extra_args)
            
            # Generate URL
            url = f"https://{bucket}.s3.amazonaws.com/{key}"
            
            logger.info(f"Uploaded {local_path} to s3://{bucket}/{key}")
            return url
            
        except self.ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise RuntimeError(f"Failed to upload to S3: {e}")
    
    def download_file(
        self,
        bucket: str,
        key: str,
        local_path: str
    ) -> str:
        """
        Download file from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Local destination path
        
        Returns:
            Path to downloaded file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.s3.download_file(bucket, key, local_path)
            logger.info(f"Downloaded s3://{bucket}/{key} to {local_path}")
            return local_path
            
        except self.ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise RuntimeError(f"Failed to download from S3: {e}")
    
    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict]:
        """
        List objects in S3 bucket.
        
        Args:
            bucket: S3 bucket name
            prefix: Key prefix filter
            max_keys: Maximum number of keys to return
        
        Returns:
            List of object metadata dictionaries
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"')
                    })
            
            logger.info(f"Listed {len(objects)} objects in s3://{bucket}/{prefix}")
            return objects
            
        except self.ClientError as e:
            logger.error(f"S3 list failed: {e}")
            raise RuntimeError(f"Failed to list S3 objects: {e}")
    
    def delete_object(self, bucket: str, key: str) -> bool:
        """
        Delete object from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
        
        Returns:
            True if deleted successfully
        """
        try:
            self.s3.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Deleted s3://{bucket}/{key}")
            return True
            
        except self.ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            raise RuntimeError(f"Failed to delete from S3: {e}")
    
    def get_object_metadata(self, bucket: str, key: str) -> Dict:
        """
        Get object metadata without downloading.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
        
        Returns:
            Object metadata dictionary
        """
        try:
            response = self.s3.head_object(Bucket=bucket, Key=key)
            
            return {
                'key': key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'content_type': response.get('ContentType', 'unknown'),
                'etag': response['ETag'].strip('"'),
                'metadata': response.get('Metadata', {})
            }
            
        except self.ClientError as e:
            logger.error(f"S3 head object failed: {e}")
            raise RuntimeError(f"Failed to get S3 object metadata: {e}")
    
    def create_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for temporary access.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Presigned URL string
        """
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for s3://{bucket}/{key} (expires in {expiration}s)")
            return url
            
        except self.ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise RuntimeError(f"Failed to generate presigned URL: {e}")
    
    def upload_directory(
        self,
        local_dir: str,
        bucket: str,
        prefix: str = "",
        file_pattern: str = "*"
    ) -> List[str]:
        """
        Upload entire directory to S3.
        
        Args:
            local_dir: Local directory path
            bucket: S3 bucket name
            prefix: S3 key prefix
            file_pattern: Glob pattern for files to upload
        
        Returns:
            List of uploaded S3 keys
        """
        if not os.path.isdir(local_dir):
            raise NotADirectoryError(f"Not a directory: {local_dir}")
        
        uploaded_keys = []
        local_path = Path(local_dir)
        
        # Find all matching files
        for file_path in local_path.rglob(file_pattern):
            if file_path.is_file():
                # Calculate relative path for S3 key
                rel_path = file_path.relative_to(local_path)
                s3_key = os.path.join(prefix, str(rel_path)).replace("\\", "/")
                
                # Upload file
                self.upload_file(str(file_path), bucket, s3_key)
                uploaded_keys.append(s3_key)
        
        logger.info(f"Uploaded {len(uploaded_keys)} files from {local_dir} to s3://{bucket}/{prefix}")
        return uploaded_keys
    
    def download_directory(
        self,
        bucket: str,
        prefix: str,
        local_dir: str
    ) -> List[str]:
        """
        Download all objects with prefix to local directory.
        
        Args:
            bucket: S3 bucket name
            prefix: S3 key prefix
            local_dir: Local destination directory
        
        Returns:
            List of downloaded file paths
        """
        # List all objects with prefix
        objects = self.list_objects(bucket, prefix)
        
        downloaded_files = []
        
        for obj in objects:
            key = obj['key']
            # Remove prefix to get relative path
            rel_path = key[len(prefix):].lstrip('/')
            local_path = os.path.join(local_dir, rel_path)
            
            # Download file
            self.download_file(bucket, key, local_path)
            downloaded_files.append(local_path)
        
        logger.info(f"Downloaded {len(downloaded_files)} files from s3://{bucket}/{prefix} to {local_dir}")
        return downloaded_files
    
    def sync_to_s3(
        self,
        local_dir: str,
        bucket: str,
        prefix: str = "",
        delete: bool = False
    ) -> Dict:
        """
        Sync local directory to S3 (upload only changed files).
        
        Args:
            local_dir: Local directory path
            bucket: S3 bucket name
            prefix: S3 key prefix
            delete: Delete S3 files not in local directory
        
        Returns:
            Sync statistics dictionary
        """
        stats = {
            'uploaded': 0,
            'skipped': 0,
            'deleted': 0
        }
        
        # Get local files
        local_path = Path(local_dir)
        local_files = {}
        
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(local_path)
                s3_key = os.path.join(prefix, str(rel_path)).replace("\\", "/")
                local_files[s3_key] = file_path
        
        # Get S3 files
        s3_objects = self.list_objects(bucket, prefix)
        s3_keys = {obj['key']: obj for obj in s3_objects}
        
        # Upload new/modified files
        for s3_key, local_file in local_files.items():
            should_upload = False
            
            if s3_key not in s3_keys:
                # New file
                should_upload = True
            else:
                # Check if modified
                local_mtime = datetime.fromtimestamp(local_file.stat().st_mtime)
                s3_mtime = datetime.fromisoformat(s3_keys[s3_key]['last_modified'])
                
                if local_mtime > s3_mtime:
                    should_upload = True
            
            if should_upload:
                self.upload_file(str(local_file), bucket, s3_key)
                stats['uploaded'] += 1
            else:
                stats['skipped'] += 1
        
        # Delete S3 files not in local directory
        if delete:
            for s3_key in s3_keys:
                if s3_key not in local_files:
                    self.delete_object(bucket, s3_key)
                    stats['deleted'] += 1
        
        logger.info(f"Sync complete: {stats}")
        return stats


# Singleton instance
_s3_adapter: Optional[S3Adapter] = None


def get_s3_adapter(
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = "us-east-1",
    endpoint_url: Optional[str] = None
) -> S3Adapter:
    """
    Get or create S3 adapter singleton.
    
    Args:
        aws_access_key_id: AWS access key
        aws_secret_access_key: AWS secret key
        region_name: AWS region
        endpoint_url: S3-compatible endpoint
    
    Returns:
        S3Adapter instance
    """
    global _s3_adapter
    
    if _s3_adapter is None:
        _s3_adapter = S3Adapter(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )
    
    return _s3_adapter
