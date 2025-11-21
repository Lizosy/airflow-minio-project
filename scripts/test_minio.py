#!/usr/bin/env python3
"""
Script to verify MinIO connection and setup
Run this inside Airflow container or with proper environment
"""

import sys
import os

try:
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
    import boto3
    from botocore.exceptions import ClientError
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Run: pip install apache-airflow-providers-amazon boto3")
    sys.exit(1)

def test_minio_connection():
    """Test MinIO connection and bucket operations"""
    
    print("=" * 70)
    print("🔍 Testing MinIO Connection")
    print("=" * 70)
    
    # Test 1: Connection
    try:
        print("\n1️⃣ Testing connection...")
        s3_hook = S3Hook(aws_conn_id='minio_default')
        print("   ✅ S3Hook initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize S3Hook: {e}")
        return False
    
    # Test 2: List buckets
    try:
        print("\n2️⃣ Listing buckets...")
        buckets = s3_hook.list_buckets()
        if buckets:
            print(f"   ✅ Found {len(buckets)} buckets:")
            for bucket in buckets:
                print(f"      - {bucket}")
        else:
            print("   ⚠️  No buckets found")
    except Exception as e:
        print(f"   ❌ Failed to list buckets: {e}")
        print("\n   💡 Check MinIO connection settings:")
        print("      - Endpoint: http://minio:9000")
        print("      - Access Key: minioadmin")
        print("      - Secret Key: minioadmin")
        return False
    
    # Test 3: Create test bucket
    try:
        print("\n3️⃣ Creating test bucket...")
        test_bucket = 'test-bucket-airflow'
        
        if s3_hook.check_for_bucket(test_bucket):
            print(f"   ℹ️  Bucket '{test_bucket}' already exists")
        else:
            s3_hook.create_bucket(bucket_name=test_bucket)
            print(f"   ✅ Created bucket: {test_bucket}")
    except Exception as e:
        print(f"   ❌ Failed to create bucket: {e}")
        return False
    
    # Test 4: Upload test file
    try:
        print("\n4️⃣ Uploading test file...")
        test_content = "Hello from Airflow + MinIO!"
        test_key = "test/hello.txt"
        
        s3_hook.load_string(
            string_data=test_content,
            key=test_key,
            bucket_name=test_bucket,
            replace=True
        )
        print(f"   ✅ Uploaded: s3://{test_bucket}/{test_key}")
    except Exception as e:
        print(f"   ❌ Failed to upload: {e}")
        return False
    
    # Test 5: Read test file
    try:
        print("\n5️⃣ Reading test file...")
        content = s3_hook.read_key(key=test_key, bucket_name=test_bucket)
        print(f"   ✅ Read content: {content}")
    except Exception as e:
        print(f"   ❌ Failed to read: {e}")
        return False
    
    # Test 6: List files
    try:
        print("\n6️⃣ Listing files in bucket...")
        files = s3_hook.list_keys(bucket_name=test_bucket)
        if files:
            print(f"   ✅ Found {len(files)} files:")
            for file in files:
                print(f"      - {file}")
        else:
            print("   ⚠️  No files found")
    except Exception as e:
        print(f"   ❌ Failed to list files: {e}")
        return False
    
    # Test 7: Create required buckets
    print("\n7️⃣ Creating required buckets...")
    required_buckets = [
        'airflow-data',
        'raw-data',
        'processed-data',
        'marketplace-data'
    ]
    
    for bucket in required_buckets:
        try:
            if not s3_hook.check_for_bucket(bucket):
                s3_hook.create_bucket(bucket_name=bucket)
                print(f"   ✅ Created: {bucket}")
            else:
                print(f"   ℹ️  Exists: {bucket}")
        except Exception as e:
            print(f"   ⚠️  Error with {bucket}: {e}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print("\n💡 MinIO Console: http://localhost:9001")
    print("   Username: minioadmin")
    print("   Password: minioadmin")
    print()
    
    return True

if __name__ == "__main__":
    success = test_minio_connection()
    sys.exit(0 if success else 1)
