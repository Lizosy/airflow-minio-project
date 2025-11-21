"""
Advanced Facebook Marketplace Scraper DAG with Enhanced Workflow
Features: Parallel scraping, data validation, notifications, error handling, cleanup
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule
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
import json

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'execution_timeout': timedelta(minutes=30),
}

def ensure_bucket_exists(bucket_name, s3_hook):
    """Ensure bucket exists"""
    try:
        if not s3_hook.check_for_bucket(bucket_name):
            s3_hook.create_bucket(bucket_name=bucket_name)
            logger.info(f"✅ Created bucket: {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Bucket error: {e}")
        return False

def validate_config(**context):
    """Validate configuration before starting"""
    logger.info("🔍 Validating configuration...")
    
    errors = []
    
    # Check parameters
    params = context.get('params', {})
    max_items = params.get('max_items', 10)
    keywords = params.get('keywords', ['iphone 13'])
    
    if max_items < 1 or max_items > 200:
        errors.append(f"max_items must be 1-200, got {max_items}")
    
    if not keywords or len(keywords) == 0:
        errors.append("keywords list is empty")
    
    # Check credentials
    try:
        email = Variable.get("fb_marketplace_email", default_var=None)
        if not email:
            logger.warning("⚠️  No email in Variables - scraping without login")
    except:
        pass
    
    # Check MinIO connection
    try:
        s3_hook = S3Hook(aws_conn_id='minio_default')
        bucket_name = 'marketplace-data'
        ensure_bucket_exists(bucket_name, s3_hook)
    except Exception as e:
        errors.append(f"MinIO connection failed: {e}")
    
    if errors:
        logger.error("❌ Configuration validation failed:")
        for err in errors:
            logger.error(f"   - {err}")
        raise ValueError(f"Config validation failed: {', '.join(errors)}")
    
    logger.info("✅ Configuration validated")
    return True

def scrape_keyword(keyword, max_items, location, radius, fetch_details):
    """Scrape single keyword"""
    logger.info(f"🔍 Scraping keyword: {keyword}")
    
    listings = []
    listing_urls = set()
    
    url = f"https://www.facebook.com/marketplace/{location}/search?query={keyword}"
    url += f"&sortBy=creation_time_descend&radius={radius}"
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    
    try:
        import os, stat
        driver_path = ChromeDriverManager().install()
        if 'THIRD_PARTY_NOTICES' in driver_path:
            driver_path = os.path.join(os.path.dirname(driver_path), 'chromedriver')
        if os.path.exists(driver_path):
            os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Get credentials
        try:
            email = Variable.get("fb_marketplace_email", default_var=None)
            password = Variable.get("fb_marketplace_password", default_var=None)
        except:
            email = None
            password = None
        
        # Login if credentials available
        if email and password:
            try:
                driver.get("https://www.facebook.com/login")
                time.sleep(2)
                driver.find_element(By.NAME, "email").send_keys(email)
                driver.find_element(By.NAME, "pass").send_keys(password)
                driver.find_element(By.NAME, "login").click()
                time.sleep(5)
                if "/checkpoint/" not in driver.current_url and "/login/" not in driver.current_url:
                    logger.info("✅ Login successful")
            except Exception as e:
                logger.warning(f"⚠️  Login failed: {e}")
        
        driver.get(url)
        time.sleep(8)
        
        # Close popup
        try:
            close_btns = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close"]')
            if close_btns:
                close_btns[0].click()
                time.sleep(1)
        except:
            pass
        
        # Scroll and scrape
        scroll_count = 0
        items_found = 0
        no_new_items_count = 0
        max_scrolls = 200
        
        while items_found < max_items and no_new_items_count < 5 and scroll_count < max_scrolls:
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)
            scroll_count += 1
            
            soup = BeautifulSoup(driver.page_source, 'lxml')
            prev_count = items_found
            links = soup.select('a[href*="/marketplace/item/"]')
            
            for link in links:
                if items_found >= max_items:
                    break
                try:
                    href = link.get('href', '')
                    if not href or '/marketplace/item/' not in href:
                        continue
                    
                    full_url = f"https://www.facebook.com{href.split('?')[0]}" if href.startswith('/') else href.split('?')[0]
                    if full_url in listing_urls:
                        continue
                    listing_urls.add(full_url)
                    
                    title_elem = link.find('span')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    parent = link.find_parent(['div', 'article'])
                    price = "N/A"
                    location_text = location.capitalize()
                    
                    if parent:
                        price_elem = parent.find('span', string=lambda t: t and ('฿' in t or 'THB' in t))
                        if price_elem:
                            price = price_elem.get_text(strip=True)
                    
                    img_elem = link.find('img')
                    image_url = img_elem.get('src', 'N/A') if img_elem else 'N/A'
                    
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
                            "radius_km": radius,
                            "condition": "N/A",
                            "description": "N/A"
                        })
                        items_found += 1
                        logger.info(f"✓ [{items_found}/{max_items}] {title[:40]}")
                except:
                    continue
            
            if items_found == prev_count:
                no_new_items_count += 1
            else:
                no_new_items_count = 0
        
        driver.quit()
        logger.info(f"✅ Scraped {len(listings)} items for '{keyword}'")
        return listings
        
    except Exception as e:
        logger.error(f"❌ Scraping failed for '{keyword}': {e}")
        try:
            driver.quit()
        except:
            pass
        return []

def scrape_multiple_keywords(**context):
    """Scrape multiple keywords in parallel (simulated)"""
    params = context.get('params', {})
    keywords = params.get('keywords', ['iphone 13'])
    max_items = params.get('max_items', 10)
    location = params.get('location', 'bangkok')
    radius = params.get('radius', 20)
    fetch_details = params.get('fetch_details', False)
    
    logger.info("=" * 70)
    logger.info("🚀 Starting parallel scraping")
    logger.info(f"📦 Keywords: {keywords}")
    logger.info(f"🔢 Max items per keyword: {max_items}")
    logger.info("=" * 70)
    
    all_listings = []
    stats = {}
    
    for keyword in keywords:
        try:
            listings = scrape_keyword(keyword, max_items, location, radius, fetch_details)
            all_listings.extend(listings)
            stats[keyword] = len(listings)
        except Exception as e:
            logger.error(f"❌ Failed to scrape '{keyword}': {e}")
            stats[keyword] = 0
    
    # Create DataFrame
    df = pd.DataFrame(all_listings)
    
    # Remove duplicates
    if len(df) > 0:
        original_count = len(df)
        df = df.drop_duplicates(subset=['url'], keep='first')
        logger.info(f"🔄 Removed {original_count - len(df)} duplicates")
    
    logger.info(f"\n📊 Scraping Summary:")
    for keyword, count in stats.items():
        logger.info(f"   {keyword}: {count} items")
    logger.info(f"   Total unique: {len(df)} items")
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    context['ti'].xcom_push(key='scraped_data', value=csv_content)
    context['ti'].xcom_push(key='scraping_stats', value=json.dumps(stats))
    
    return len(df)

def validate_scraped_data(**context):
    """Validate scraped data quality"""
    csv_content = context['ti'].xcom_pull(key='scraped_data', task_ids='scrape_parallel')
    
    if not csv_content:
        logger.error("❌ No data to validate")
        return 'skip_upload'
    
    df = pd.read_csv(StringIO(csv_content))
    
    logger.info("🔍 Validating data quality...")
    
    issues = []
    
    # Check row count
    if len(df) == 0:
        issues.append("No data scraped")
    elif len(df) < 3:
        issues.append(f"Too few items: {len(df)}")
    
    # Check required columns
    required_cols = ['title', 'price', 'url', 'keyword']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    # Check data quality
    if 'title' in df.columns:
        na_titles = df['title'].isna().sum()
        if na_titles > len(df) * 0.5:
            issues.append(f"Too many missing titles: {na_titles}/{len(df)}")
    
    if 'url' in df.columns:
        duplicates = df['url'].duplicated().sum()
        if duplicates > 0:
            logger.warning(f"⚠️  Found {duplicates} duplicate URLs")
    
    if issues:
        logger.error("❌ Data validation failed:")
        for issue in issues:
            logger.error(f"   - {issue}")
        return 'handle_failure'
    
    logger.info(f"✅ Data validated: {len(df)} items")
    return 'upload_to_storage'

def upload_to_storage(**context):
    """Upload validated data to MinIO"""
    csv_content = context['ti'].xcom_pull(key='scraped_data', task_ids='scrape_parallel')
    
    if not csv_content:
        logger.warning("No data to upload")
        return None
    
    df = pd.read_csv(StringIO(csv_content))
    
    s3_hook = S3Hook(aws_conn_id='minio_default')
    bucket_name = 'marketplace-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    
    # Upload raw data
    raw_key = f'raw/marketplace_raw_{timestamp}.csv'
    s3_hook.load_string(
        string_data=csv_content,
        key=raw_key,
        bucket_name=bucket_name,
        replace=True
    )
    logger.info(f"✅ Raw data saved: s3://{bucket_name}/{raw_key}")
    
    # Upload by keyword
    keywords = df['keyword'].unique()
    for keyword in keywords:
        keyword_df = df[df['keyword'] == keyword]
        keyword_csv = keyword_df.to_csv(index=False)
        keyword_key = f'by_keyword/{keyword.replace(" ", "_")}_{timestamp}.csv'
        s3_hook.load_string(
            string_data=keyword_csv,
            key=keyword_key,
            bucket_name=bucket_name,
            replace=True
        )
        logger.info(f"✅ Keyword data saved: {keyword} ({len(keyword_df)} items)")
    
    context['ti'].xcom_push(key='upload_paths', value=json.dumps({
        'raw': raw_key,
        'keywords': list(keywords)
    }))
    
    return {
        'total_items': len(df),
        'keywords': list(keywords),
        'raw_file': raw_key
    }

def generate_report(**context):
    """Generate summary report"""
    stats_json = context['ti'].xcom_pull(key='scraping_stats', task_ids='scrape_parallel')
    upload_result = context['ti'].xcom_pull(task_ids='upload_to_storage')
    
    if not stats_json:
        logger.warning("No stats available")
        return None
    
    stats = json.loads(stats_json)
    
    logger.info("\n" + "=" * 70)
    logger.info("📊 FINAL REPORT - Advanced Marketplace Scraper")
    logger.info("=" * 70)
    logger.info(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📦 Keywords scraped: {len(stats)}")
    
    for keyword, count in stats.items():
        logger.info(f"   • {keyword}: {count} items")
    
    if upload_result:
        logger.info(f"\n📁 Files uploaded:")
        logger.info(f"   • Raw data: {upload_result.get('raw_file')}")
        logger.info(f"   • Keywords: {len(upload_result.get('keywords', []))}")
        logger.info(f"   • Total items: {upload_result.get('total_items')}")
    
    logger.info("=" * 70 + "\n")
    
    return stats

def handle_failure(**context):
    """Handle scraping failure"""
    logger.error("❌ Scraping workflow failed")
    logger.error("🔧 Troubleshooting tips:")
    logger.error("   1. Check Facebook credentials in Airflow Variables")
    logger.error("   2. Verify MinIO connection")
    logger.error("   3. Check if max_items is reasonable")
    logger.error("   4. Review Chrome/Selenium logs")
    return None

def cleanup_old_files(**context):
    """Cleanup old files from MinIO"""
    s3_hook = S3Hook(aws_conn_id='minio_default')
    bucket_name = 'marketplace-data'
    
    try:
        # Keep last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # List files
        keys = s3_hook.list_keys(bucket_name=bucket_name, prefix='raw/')
        
        deleted_count = 0
        for key in keys or []:
            try:
                # Parse date from filename
                filename = key.split('/')[-1]
                if 'marketplace_raw_' in filename:
                    date_str = filename.replace('marketplace_raw_', '').replace('.csv', '')[:8]
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        s3_hook.delete_objects(bucket=bucket_name, keys=[key])
                        deleted_count += 1
                        logger.info(f"🗑️  Deleted old file: {key}")
            except Exception as e:
                logger.warning(f"Could not process {key}: {e}")
        
        logger.info(f"✅ Cleanup completed: {deleted_count} files deleted")
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return 0

# Define DAG
with DAG(
    'marketplace_advanced_flow',
    default_args=default_args,
    description='Advanced workflow with parallel scraping, validation, and cleanup',
    schedule_interval='0 */6 * * *',  # Run every 6 hours
    catchup=False,
    max_active_runs=1,
    tags=['marketplace', 'advanced', 'parallel', 'production'],
    params={
        'keywords': ['iphone 13', 'iphone 14', 'samsung galaxy'],
        'location': 'bangkok',
        'radius': 20,
        'max_items': 20,
        'fetch_details': False
    }
) as dag:
    
    # Start
    start = EmptyOperator(task_id='start')
    
    # Validate configuration
    validate = PythonOperator(
        task_id='validate_config',
        python_callable=validate_config,
    )
    
    # Scrape multiple keywords
    scrape = PythonOperator(
        task_id='scrape_parallel',
        python_callable=scrape_multiple_keywords,
        execution_timeout=timedelta(minutes=20),
    )
    
    # Validate scraped data
    validate_data = BranchPythonOperator(
        task_id='validate_data',
        python_callable=validate_scraped_data,
    )
    
    # Upload to storage
    upload = PythonOperator(
        task_id='upload_to_storage',
        python_callable=upload_to_storage,
    )
    
    # Generate report
    report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
    )
    
    # Cleanup old files
    cleanup = PythonOperator(
        task_id='cleanup_old_files',
        python_callable=cleanup_old_files,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # Handle failure
    failure = PythonOperator(
        task_id='handle_failure',
        python_callable=handle_failure,
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # Skip upload dummy
    skip_upload = EmptyOperator(
        task_id='skip_upload',
    )
    
    # End
    end = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )
    
    # Define workflow
    start >> validate >> scrape >> validate_data
    validate_data >> upload >> report >> cleanup >> end
    validate_data >> skip_upload >> end
    validate_data >> failure >> end
