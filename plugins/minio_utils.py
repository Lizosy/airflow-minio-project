"""
Utility functions for MinIO operations in Airflow DAGs
"""

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from io import StringIO, BytesIO
import json
from typing import Optional, List, Dict, Any


class MinIOHelper:
    """Helper class for MinIO operations"""
    
    def __init__(self, conn_id: str = 'minio_default'):
        """
        Initialize MinIO Helper
        
        Args:
            conn_id: Airflow connection ID for MinIO
        """
        self.conn_id = conn_id
        self.hook = S3Hook(aws_conn_id=conn_id)
    
    def upload_dataframe(
        self, 
        df: pd.DataFrame, 
        bucket: str, 
        key: str,
        file_format: str = 'csv'
    ) -> str:
        """
        Upload pandas DataFrame to MinIO
        
        Args:
            df: DataFrame to upload
            bucket: MinIO bucket name
            key: Object key (filename)
            file_format: File format ('csv', 'json', 'parquet')
        
        Returns:
            Full S3 path
        """
        if file_format == 'csv':
            buffer = StringIO()
            df.to_csv(buffer, index=False)
            content = buffer.getvalue()
        elif file_format == 'json':
            content = df.to_json(orient='records', indent=2)
        elif file_format == 'parquet':
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            content = buffer.getvalue()
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
        self.hook.load_string(
            string_data=content,
            key=key,
            bucket_name=bucket,
            replace=True
        )
        
        return f"s3://{bucket}/{key}"
    
    def download_dataframe(
        self, 
        bucket: str, 
        key: str,
        file_format: str = 'csv'
    ) -> pd.DataFrame:
        """
        Download file from MinIO as DataFrame
        
        Args:
            bucket: MinIO bucket name
            key: Object key (filename)
            file_format: File format ('csv', 'json', 'parquet')
        
        Returns:
            pandas DataFrame
        """
        content = self.hook.read_key(key=key, bucket_name=bucket)
        
        if file_format == 'csv':
            df = pd.read_csv(StringIO(content))
        elif file_format == 'json':
            df = pd.read_json(StringIO(content))
        elif file_format == 'parquet':
            df = pd.read_parquet(BytesIO(content))
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
        return df
    
    def upload_json(
        self, 
        data: Dict[str, Any], 
        bucket: str, 
        key: str
    ) -> str:
        """
        Upload JSON data to MinIO
        
        Args:
            data: Dictionary to upload
            bucket: MinIO bucket name
            key: Object key (filename)
        
        Returns:
            Full S3 path
        """
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        
        self.hook.load_string(
            string_data=json_content,
            key=key,
            bucket_name=bucket,
            replace=True
        )
        
        return f"s3://{bucket}/{key}"
    
    def download_json(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Download JSON file from MinIO
        
        Args:
            bucket: MinIO bucket name
            key: Object key (filename)
        
        Returns:
            Dictionary
        """
        content = self.hook.read_key(key=key, bucket_name=bucket)
        return json.loads(content)
    
    def list_files(
        self, 
        bucket: str, 
        prefix: Optional[str] = None
    ) -> List[str]:
        """
        List files in MinIO bucket
        
        Args:
            bucket: MinIO bucket name
            prefix: Filter by prefix
        
        Returns:
            List of file keys
        """
        files = self.hook.list_keys(bucket_name=bucket, prefix=prefix)
        return files if files else []
    
    def delete_file(self, bucket: str, key: str) -> None:
        """
        Delete file from MinIO
        
        Args:
            bucket: MinIO bucket name
            key: Object key (filename)
        """
        self.hook.delete_objects(bucket=bucket, keys=key)
    
    def copy_file(
        self, 
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str
    ) -> str:
        """
        Copy file within MinIO
        
        Args:
            source_bucket: Source bucket
            source_key: Source key
            dest_bucket: Destination bucket
            dest_key: Destination key
        
        Returns:
            Destination S3 path
        """
        self.hook.copy_object(
            source_bucket_key=source_key,
            source_bucket_name=source_bucket,
            dest_bucket_key=dest_key,
            dest_bucket_name=dest_bucket
        )
        
        return f"s3://{dest_bucket}/{dest_key}"
    
    def file_exists(self, bucket: str, key: str) -> bool:
        """
        Check if file exists in MinIO
        
        Args:
            bucket: MinIO bucket name
            key: Object key (filename)
        
        Returns:
            True if exists, False otherwise
        """
        return self.hook.check_for_key(key=key, bucket_name=bucket)


# Example usage functions
def example_upload(**context):
    """Example: Upload DataFrame to MinIO"""
    helper = MinIOHelper()
    
    # Create sample data
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['A', 'B', 'C'],
        'value': [100, 200, 300]
    })
    
    # Upload as CSV
    path = helper.upload_dataframe(
        df=df,
        bucket='raw-data',
        key='sample/data.csv',
        file_format='csv'
    )
    
    print(f"✅ Uploaded to: {path}")
    return path


def example_download(**context):
    """Example: Download from MinIO"""
    helper = MinIOHelper()
    
    # Download DataFrame
    df = helper.download_dataframe(
        bucket='raw-data',
        key='sample/data.csv',
        file_format='csv'
    )
    
    print(f"✅ Downloaded {len(df)} rows")
    print(df.head())
    
    return len(df)


def example_list_files(**context):
    """Example: List files in bucket"""
    helper = MinIOHelper()
    
    files = helper.list_files(
        bucket='raw-data',
        prefix='sample/'
    )
    
    print(f"✅ Found {len(files)} files:")
    for file in files:
        print(f"   - {file}")
    
    return files
