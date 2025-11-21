"""
ETL Pipeline DAG: Extract from MinIO, Transform, Load back
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from io import StringIO, BytesIO
import logging

logger = logging.getLogger(__name__)

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

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_from_minio(**context):
    """Extract data from MinIO"""
    s3_hook = S3Hook(aws_conn_id='minio_default')
    
    bucket_name = 'raw-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    
    # List all CSV files
    files = s3_hook.list_keys(bucket_name=bucket_name, prefix='sample_data')
    
    if not files:
        print("⚠️  No files found in raw-data bucket")
        return None
    
    # Get the latest file
    latest_file = sorted(files)[-1]
    print(f"📥 Extracting: {latest_file}")
    
    # Read file from MinIO
    file_content = s3_hook.read_key(key=latest_file, bucket_name=bucket_name)
    
    context['ti'].xcom_push(key='raw_data', value=file_content)
    context['ti'].xcom_push(key='source_file', value=latest_file)
    
    return latest_file

def transform_data(**context):
    """Transform the data"""
    raw_data = context['ti'].xcom_pull(key='raw_data', task_ids='extract')
    
    if not raw_data:
        print("⚠️  No data to transform")
        return None
    
    # Load into DataFrame
    df = pd.read_csv(StringIO(raw_data))
    
    print(f"📊 Original data: {len(df)} rows")
    
    # Transformation examples:
    # 1. Add calculated column
    df['price_with_tax'] = df['price'] * 1.07
    
    # 2. Add discount column
    df['discount_price'] = df['price'] * 0.9
    
    # 3. Add processing timestamp
    df['processed_at'] = datetime.now().isoformat()
    
    # 4. Clean data
    df = df.dropna()
    
    print(f"✅ Transformed data: {len(df)} rows")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Convert back to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    context['ti'].xcom_push(key='transformed_data', value=csv_content)
    
    return len(df)

def load_to_minio(**context):
    """Load transformed data back to MinIO"""
    transformed_data = context['ti'].xcom_pull(key='transformed_data', task_ids='transform')
    source_file = context['ti'].xcom_pull(key='source_file', task_ids='extract')
    
    if not transformed_data:
        print("⚠️  No data to load")
        return None
    
    s3_hook = S3Hook(aws_conn_id='minio_default')
    
    bucket_name = 'processed-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    file_key = f'processed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    s3_hook.load_string(
        string_data=transformed_data,
        key=file_key,
        bucket_name=bucket_name,
        replace=True
    )
    
    print(f"✅ Loaded to MinIO: s3://{bucket_name}/{file_key}")
    print(f"📊 Source: {source_file}")
    print(f"📊 Destination: {file_key}")
    
    return file_key

def generate_report(**context):
    """Generate a summary report"""
    source_file = context['ti'].xcom_pull(key='source_file', task_ids='extract')
    transformed_rows = context['ti'].xcom_pull(key='return_value', task_ids='transform')
    output_file = context['ti'].xcom_pull(key='return_value', task_ids='load')
    
    report = {
        'pipeline_run': datetime.now().isoformat(),
        'source_file': source_file,
        'output_file': output_file,
        'rows_processed': transformed_rows,
        'status': 'SUCCESS'
    }
    
    print("\n" + "="*60)
    print("📄 ETL Pipeline Report")
    print("="*60)
    for key, value in report.items():
        print(f"   {key}: {value}")
    print("="*60)
    
    return report

# Define DAG
with DAG(
    'etl_pipeline_minio',
    default_args=default_args,
    description='ETL Pipeline: Extract from MinIO, Transform, Load back',
    schedule_interval='@hourly',
    catchup=False,
    tags=['etl', 'minio', 'pipeline'],
) as dag:
    
    # Extract
    task_extract = PythonOperator(
        task_id='extract',
        python_callable=extract_from_minio,
    )
    
    # Transform
    task_transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )
    
    # Load
    task_load = PythonOperator(
        task_id='load',
        python_callable=load_to_minio,
    )
    
    # Report
    task_report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
    )
    
    # Pipeline
    task_extract >> task_transform >> task_load >> task_report
