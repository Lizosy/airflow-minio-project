"""
Facebook Marketplace Scraper DAG
This DAG scrapes data from Facebook Marketplace using Selenium and stores in MinIO
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from io import StringIO
import logging

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

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
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def scrape_marketplace(**context):
    """
    Scrape Facebook Marketplace data using Selenium
    """
    # Get parameters from context or use defaults
    keyword = context.get('params', {}).get('keyword', 'iphone')
    location = context.get('params', {}).get('location', 'bangkok')
    radius = context.get('params', {}).get('radius', 200)
    max_items = context.get('params', {}).get('max_items', 100)
    
    listings = []
    
    # Build URL
    url = f"https://www.facebook.com/marketplace/{location}/search?query={keyword}"
    url += f"&sortBy=creation_time_descend&radius={radius}"
    
    logger.info("=" * 70)
    logger.info("🔍 Facebook Marketplace Scraper (Selenium)")
    logger.info("=" * 70)
    logger.info(f"📦 ค้นหา: {keyword}")
    logger.info(f"📍 พื้นที่: {location} (รัศมี {radius} km)")
    logger.info(f"🔢 เป้าหมาย: {max_items} รายการ")
    logger.info("=" * 70)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    
    # Initialize driver
    logger.info("🚀 กำลังเปิด Chrome...")
    try:
        import os
        import stat
        
        # Use ChromeDriverManager with proper configuration
        driver_path = ChromeDriverManager().install()
        
        # Fix: Get the actual chromedriver path, not THIRD_PARTY_NOTICES
        if 'THIRD_PARTY_NOTICES' in driver_path:
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, 'chromedriver')
        
        # Fix permissions
        if os.path.exists(driver_path):
            os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            logger.info(f"✅ ChromeDriver permissions set: {driver_path}")
        else:
            logger.error(f"❌ ChromeDriver not found at: {driver_path}")
            return 0
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✅ Chrome เปิดสำเร็จ")
    except Exception as e:
        logger.error(f"❌ Error initializing Chrome: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 0
    
    try:
        # Go to Marketplace
        logger.info("🌐 กำลังโหลดหน้า Marketplace...")
        driver.get(url)
        time.sleep(5)
        
        # Close popup if any
        try:
            close_btns = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close"]')
            if close_btns:
                close_btns[0].click()
                time.sleep(1)
        except:
            pass
        
        logger.info("✅ โหลดหน้าสำเร็จ")
        
        # Scroll and scrape
        logger.info("📜 กำลัง scroll และดึงข้อมูล...")
        scroll_count = 0
        items_found = 0
        no_new_items_count = 0
        last_height = 0
        
        while items_found < max_items and no_new_items_count < 3:
            # Scroll down
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)
            scroll_count += 1
            
            # Get page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            prev_count = items_found
            
            # Find listing links
            links = soup.select('a[href*="/marketplace/item/"]')
            
            for link in links:
                if items_found >= max_items:
                    break
                
                try:
                    href = link.get('href', '')
                    if not href or '/marketplace/item/' not in href:
                        continue
                    
                    # Full URL
                    if href.startswith('/'):
                        full_url = f"https://www.facebook.com{href.split('?')[0]}"
                    else:
                        full_url = href.split('?')[0]
                    
                    # Check duplicate
                    if any(item['url'] == full_url for item in listings):
                        continue
                    
                    # Extract title
                    title_elem = link.find('span')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    # Find price from parent
                    parent = link.find_parent(['div', 'article'])
                    price = "N/A"
                    location_text = location.capitalize()
                    
                    if parent:
                        # Price
                        price_elem = parent.find('span', string=lambda t: t and ('฿' in t or 'THB' in t))
                        if price_elem:
                            price = price_elem.get_text(strip=True)
                        
                        # Location
                        loc_elem = parent.find('span', string=lambda t: t and any(
                            word in str(t).lower() for word in ['กรุงเทพ', 'bangkok', 'เชียงใหม่', 'ภูเก็ต', 'chiangmai', 'phuket']
                        ))
                        if loc_elem:
                            location_text = loc_elem.get_text(strip=True)
                    
                    # Image
                    img_elem = link.find('img')
                    image_url = img_elem.get('src', 'N/A') if img_elem else 'N/A'
                    
                    # Add to list
                    if title != "N/A" and len(title) > 3:
                        listings.append({
                            "title": title,
                            "price": price,
                            "location": location_text,
                            "url": full_url,
                            "image_url": image_url,
                            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "keyword": keyword,
                            "search_location": location,
                            "radius_km": radius
                        })
                        items_found += 1
                        logger.info(f"✓ [{items_found}/{max_items}] {title[:45]}... | {price}")
                
                except Exception as e:
                    continue
            
            # Check for new items
            if items_found == prev_count:
                no_new_items_count += 1
            else:
                no_new_items_count = 0
            
            # Check scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_new_items_count += 1
            last_height = new_height
            
            if scroll_count % 5 == 0:
                logger.info(f"📊 Scroll: {scroll_count} | Found: {items_found}/{max_items}")
    
    finally:
        driver.quit()
        logger.info("🔒 ปิด browser แล้ว")
    
    # Create DataFrame
    df = pd.DataFrame(listings)
    
    logger.info("=" * 70)
    logger.info(f"✅ เสร็จสิ้น! ได้ข้อมูล {len(df)} รายการ")
    logger.info("=" * 70)
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    context['ti'].xcom_push(key='marketplace_data', value=csv_content)
    logger.info(f"✅ Scraped {len(df)} items from marketplace")
    return len(df)

def upload_marketplace_data(**context):
    """Upload scraped data to MinIO"""
    csv_content = context['ti'].xcom_pull(key='marketplace_data', task_ids='scrape_data')
    
    s3_hook = S3Hook(aws_conn_id='minio_default')
    
    bucket_name = 'marketplace-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    file_key = f'marketplace_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    s3_hook.load_string(
        string_data=csv_content,
        key=file_key,
        bucket_name=bucket_name,
        replace=True
    )
    
    print(f"✅ Uploaded to MinIO: s3://{bucket_name}/{file_key}")
    return file_key

def process_and_analyze(**context):
    """Process and analyze the scraped data"""
    csv_content = context['ti'].xcom_pull(key='marketplace_data', task_ids='scrape_data')
    
    df = pd.read_csv(StringIO(csv_content))
    
    # Simple analysis
    print(f"\n📊 Data Analysis:")
    print(f"   Total items: {len(df)}")
    print(f"   Locations: {df['location'].unique().tolist()}")
    print(f"   Price range: {df['price'].min()} - {df['price'].max()}")
    
    return {
        'total_items': len(df),
        'locations': df['location'].unique().tolist(),
        'timestamp': datetime.now().isoformat()
    }

# Define DAG
with DAG(
    'facebook_marketplace_scraper',
    default_args=default_args,
    description='Scrape Facebook Marketplace and store in MinIO',
    schedule_interval='0 */6 * * *',  # Run every 6 hours
    catchup=False,
    tags=['marketplace', 'scraping', 'minio'],
) as dag:
    
    # Task 1: Scrape data
    task_scrape = PythonOperator(
        task_id='scrape_data',
        python_callable=scrape_marketplace,
    )
    
    # Task 2: Upload to MinIO
    task_upload = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_marketplace_data,
    )
    
    # Task 3: Process and analyze
    task_process = PythonOperator(
        task_id='process_data',
        python_callable=process_and_analyze,
    )
    
    # Define dependencies
    task_scrape >> task_upload >> task_process
