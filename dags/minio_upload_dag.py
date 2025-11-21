"""
Example DAG: Upload data to MinIO
This DAG demonstrates how to upload files to MinIO object storage
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import json
from io import StringIO, BytesIO
import logging

logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def ensure_bucket_exists(bucket_name, s3_hook):
    """Ensure bucket exists, create if not"""
    try:
        if not s3_hook.check_for_bucket(bucket_name):
            logger.info(f"Creating bucket: {bucket_name}")
            s3_hook.create_bucket(bucket_name=bucket_name)
            logger.info(f"✅ Bucket {bucket_name} created")
        else:
            logger.info(f"✅ Bucket {bucket_name} exists")
    except Exception as e:
        logger.warning(f"⚠️  Could not verify/create bucket {bucket_name}: {e}")

def create_sample_data(**context):
    """Create sample data"""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'price': [100, 200, 300, 400, 500],
        'category': ['Electronics', 'Fashion', 'Home', 'Sports', 'Books'],
        'timestamp': [datetime.now().isoformat()] * 5
    }
    
    df = pd.DataFrame(data)
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Push to XCom
    context['ti'].xcom_push(key='csv_data', value=csv_content)
    print(f"✅ Created sample data with {len(df)} rows")
    return len(df)

def upload_to_minio(**context):
    """Upload data to MinIO"""
    # Get data from XCom
    csv_content = context['ti'].xcom_pull(key='csv_data', task_ids='create_data')
    
    # Initialize S3 Hook (MinIO uses S3-compatible API)
    s3_hook = S3Hook(aws_conn_id='minio_default')
    
    # Upload to MinIO
    bucket_name = 'raw-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    file_key = f'sample_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    s3_hook.load_string(
        string_data=csv_content,
        key=file_key,
        bucket_name=bucket_name,
        replace=True
    )
    
    print(f"✅ Uploaded to MinIO: s3://{bucket_name}/{file_key}")
    return file_key

def upload_json_to_minio(**context):
    """Upload JSON data to MinIO"""
    # Create sample JSON
    data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'source': 'airflow_dag',
            'version': '1.0'
        },
        'items': [
            {'id': i, 'value': f'Item {i}'} 
            for i in range(1, 11)
        ]
    }
    
    json_content = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Upload to MinIO
    s3_hook = S3Hook(aws_conn_id='minio_default')
    bucket_name = 'processed-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    file_key = f'metadata_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    s3_hook.load_string(
        string_data=json_content,
        key=file_key,
        bucket_name=bucket_name,
        replace=True
    )
    
    print(f"✅ Uploaded JSON to MinIO: s3://{bucket_name}/{file_key}")
    return file_key

def list_minio_files(**context):
    """List all files in MinIO bucket"""
    s3_hook = S3Hook(aws_conn_id='minio_default')
    
    buckets = ['raw-data', 'processed-data']
    
    for bucket in buckets:
        try:
            files = s3_hook.list_keys(bucket_name=bucket)
            if files:
                print(f"\n📁 Bucket: {bucket}")
                for file in files[:10]:  # Show first 10 files
                    print(f"   - {file}")
            else:
                print(f"\n📁 Bucket: {bucket} (empty)")
        except Exception as e:
            print(f"⚠️  Error listing bucket {bucket}: {e}")

# Define DAG
with DAG(
    'minio_upload_example',
    default_args=default_args,
    description='Upload data to MinIO object storage',
    schedule_interval='@daily',
    catchup=False,
    tags=['minio', 'storage', 'example'],
) as dag:
    
    # Task 1: Create sample data
    task_create_data = PythonOperator(
        task_id='create_data',
        python_callable=create_sample_data,
    )
    
    # Task 2: Upload CSV to MinIO
    task_upload_csv = PythonOperator(
        task_id='upload_csv_to_minio',
        python_callable=upload_to_minio,
    )
    
    # Task 3: Upload JSON to MinIO
    task_upload_json = PythonOperator(
        task_id='upload_json_to_minio',
        python_callable=upload_json_to_minio,
    )
    
    # Task 4: List files in MinIO
    task_list_files = PythonOperator(
        task_id='list_minio_files',
        python_callable=list_minio_files,
    )
    
    # Define task dependencies
    task_create_data >> task_upload_csv >> task_list_files
    task_create_data >> task_upload_json >> task_list_files
