"""
Advanced Facebook Marketplace Scraper DAG with Details Extraction
This DAG scrapes marketplace data including product details and condition
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
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

def scrape_with_details(**context):
    """
    Scrape Facebook Marketplace with full details including condition and description
    """
    # Parameters
    keyword = context.get('params', {}).get('keyword', 'iphone')
    location = context.get('params', {}).get('location', 'bangkok')
    radius = context.get('params', {}).get('radius', 100)
    max_items = context.get('params', {}).get('max_items', 100)
    fetch_details = context.get('params', {}).get('fetch_details', True)
    
    # Get credentials from Airflow Variables (if set)
    try:
        email = Variable.get("fb_marketplace_email", default_var=None)
        password = Variable.get("fb_marketplace_password", default_var=None)
    except Exception as e:
        logger.warning(f"Could not get credentials from Variables: {e}")
        email = None
        password = None
    
    # Override with params if provided
    if context.get('params', {}).get('email'):
        email = context['params']['email']
    if context.get('params', {}).get('password'):
        password = context['params']['password']
    
    listings = []
    listing_urls = set()  # ใช้ set แทน list เพื่อเช็คซ้ำเร็วขึ้น
    
    # Build URL
    url = f"https://www.facebook.com/marketplace/{location}/search?query={keyword}"
    url += f"&sortBy=creation_time_descend&radius={radius}"
    
    logger.info("=" * 70)
    logger.info("🔍 Facebook Marketplace Advanced Scraper")
    logger.info("=" * 70)
    logger.info(f"📦 ค้นหา: {keyword}")
    logger.info(f"📍 พื้นที่: {location} (รัศมี {radius} km)")
    logger.info(f"🔢 เป้าหมาย: {max_items} รายการ")
    logger.info(f"🔍 ดึง Details: {fetch_details}")
    logger.info("=" * 70)
    
    # Setup Chrome - ปรับให้ทำงานใน Docker headless แต่โหลด content เต็มที่
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # จำเป็นสำหรับ Docker
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option('prefs', {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
    })
    chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    
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
        logger.info("✅ Chrome initialized")
    except Exception as e:
        logger.error(f"❌ Chrome error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 0
    
    try:
        # Login if credentials provided
        if email and password:
            logger.info("🔐 กำลัง login...")
            try:
                driver.get("https://www.facebook.com/login")
                time.sleep(2)
                
                from selenium.webdriver.common.by import By
                driver.find_element(By.NAME, "email").send_keys(email)
                driver.find_element(By.NAME, "pass").send_keys(password)
                driver.find_element(By.NAME, "login").click()
                time.sleep(5)
                
                if "/checkpoint/" not in driver.current_url and "/login/" not in driver.current_url:
                    logger.info("✅ Login สำเร็จ!")
                else:
                    logger.warning("⚠️  Login อาจไม่สำเร็จ")
            except Exception as e:
                logger.warning(f"⚠️  Login error: {e}")
        
        driver.get(url)
        time.sleep(8)  # รอให้โหลดเต็มที่
        
        # Close popup if exists
        try:
            from selenium.webdriver.common.by import By
            close_btns = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close"]')
            if close_btns:
                close_btns[0].click()
                time.sleep(1)
        except:
            pass
        
        # Scroll and scrape - เหมือน Colab
        logger.info("📜 กำลัง scroll และดึงข้อมูล...")
        scroll_count = 0
        items_found = 0
        no_new_items_count = 0
        last_height = 0
        max_scrolls = 200  # เพิ่มจำนวนรอบ
        
        while items_found < max_items and no_new_items_count < 5 and scroll_count < max_scrolls:
            # Scroll เหมือน Colab: 1 ครั้งต่อรอบ
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)
            scroll_count += 1
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
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
                        
                        loc_elem = parent.find('span', string=lambda t: t and any(
                            word in str(t).lower() for word in ['กรุงเทพ', 'bangkok', 'เชียงใหม่', 'ภูเก็ต']
                        ))
                        if loc_elem:
                            location_text = loc_elem.get_text(strip=True)
                    
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
                
                except Exception as e:
                    continue
            
            # Check progress
            if items_found == prev_count:
                no_new_items_count += 1
                logger.info(f"⚠️ Scroll #{scroll_count}: ไม่เจอ item ใหม่ (ครั้งที่ {no_new_items_count}/5)")
            else:
                no_new_items_count = 0
                logger.info(f"✅ Scroll #{scroll_count}: +{items_found - prev_count} items (รวม {items_found}/{max_items})")
            
            # Check scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_new_items_count += 1
            last_height = new_height
        
        # Fetch details if enabled
        if fetch_details and listings:
            logger.info(f"🔍 Fetching details for {len(listings)} items...")
            
            for idx, listing in enumerate(listings, 1):
                try:
                    logger.info(f"📄 [{idx}/{len(listings)}] {listing['title'][:30]}")
                    
                    driver.get(listing['url'])
                    time.sleep(3)
                    
                    # Scroll เล็กน้อยเพื่อ trigger lazy loading
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
                    
                    detail_html = driver.page_source
                    detail_soup = BeautifulSoup(detail_html, 'lxml')
                    
                    # Find condition - ลองหลายวิธี
                    condition_found = "N/A"
                    
                    # วิธีที่ 1: หาจาก label "Condition"
                    condition_labels = detail_soup.find_all('span', string=lambda t: t and 'condition' in str(t).lower())
                    for label in condition_labels:
                        parent = label.find_parent(['div', 'span'])
                        if parent:
                            next_span = parent.find_next('span')
                            if next_span and next_span != label:
                                condition_found = next_span.get_text(strip=True)
                                break
                    
                    # วิธีที่ 2: หาจากคำสำคัญ
                    if condition_found == "N/A":
                        condition_keywords = [
                            'new', 'used - like new', 'used - good', 'used - fair',
                            'brand new', 'like new', 'excellent condition', 'good condition',
                            'ใหม่', 'มือสอง', 'เหมือนใหม่', 'สภาพดี'
                        ]
                        for kw in condition_keywords:
                            elem = detail_soup.find('span', string=lambda t: t and kw.lower() in str(t).lower())
                            if elem:
                                condition_found = elem.get_text(strip=True)
                                break
                    
                    # วิธีที่ 3: หาจาก meta tag
                    if condition_found == "N/A":
                        meta_content = detail_soup.find('meta', attrs={'property': 'og:description'})
                        if meta_content:
                            content_text = meta_content.get('content', '')
                            for kw in ['New', 'Used', 'ใหม่', 'มือสอง']:
                                if kw in content_text:
                                    condition_found = kw
                                    break
                    
                    # Find description - ลองหลายวิธี
                    description_found = "N/A"
                    
                    # วิธีที่ 1: หาจาก meta description
                    meta_desc = detail_soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        desc_text = meta_desc['content'].strip()
                        if len(desc_text) > 20:
                            description_found = desc_text[:500]
                    
                    # วิธีที่ 2: หาจาก og:description
                    if description_found == "N/A":
                        og_desc = detail_soup.find('meta', attrs={'property': 'og:description'})
                        if og_desc and og_desc.get('content'):
                            desc_text = og_desc['content'].strip()
                            if len(desc_text) > 20:
                                description_found = desc_text[:500]
                    
                    # วิธีที่ 3: หาจาก div/span ที่มีข้อความยาว
                    if description_found == "N/A":
                        # หา div ที่มีข้อความยาว 50-1000 ตัวอักษร
                        all_texts = detail_soup.find_all(['div', 'span', 'p'])
                        for elem in all_texts:
                            text = elem.get_text(strip=True)
                            # เช็คว่าไม่ใช่ title, price, location
                            if (len(text) > 50 and len(text) < 1000 and
                                text not in [listing['title'], listing['price'], listing['location']] and
                                not text.startswith('฿') and
                                not any(word in text.lower() for word in ['facebook', 'marketplace', 'message', 'share'])):
                                description_found = text[:500]
                                break
                    
                    listing['condition'] = condition_found
                    listing['description'] = description_found
                    
                    logger.info(f"   ✓ Condition: {condition_found}")
                    logger.info(f"   ✓ Description: {len(description_found)} chars")
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"   ⚠️  Detail fetch error: {str(e)[:50]}")
                    continue
            
            logger.info("✅ Details fetched")
    
    finally:
        driver.quit()
        logger.info("🔒 Browser closed")
    
    # Create DataFrame
    df = pd.DataFrame(listings)
    logger.info(f"✅ Scraped {len(df)} items with details")
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    context['ti'].xcom_push(key='marketplace_data_detailed', value=csv_content)
    return len(df)

def upload_detailed_data(**context):
    """Upload detailed marketplace data to MinIO with hourly and daily files"""
    csv_content = context['ti'].xcom_pull(key='marketplace_data_detailed', task_ids='scrape_with_details')
    
    if not csv_content:
        logger.warning("No data to upload")
        return None
    
    # Parse new data
    new_df = pd.read_csv(StringIO(csv_content))
    
    s3_hook = S3Hook(aws_conn_id='minio_default')
    bucket_name = 'marketplace-data'
    ensure_bucket_exists(bucket_name, s3_hook)
    
    current_time = datetime.now()
    date_str = current_time.strftime("%Y%m%d")
    hour_str = current_time.strftime("%Y%m%d_%H")
    
    # Statistics
    stats = {
        'new_items': 0,
        'updated_items': 0,
        'unchanged_items': 0,
        'total_scraped': len(new_df)
    }
    
    # --- HOURLY FILE (Replace if exists in same hour) ---
    hourly_key = f'hourly/marketplace_{hour_str}.csv'
    
    try:
        # Check if hourly file exists
        if s3_hook.check_for_key(key=hourly_key, bucket_name=bucket_name):
            logger.info(f"⚠️  Hourly file exists, replacing: {hourly_key}")
        
        # Upload/Replace hourly file
        s3_hook.load_string(
            string_data=csv_content,
            key=hourly_key,
            bucket_name=bucket_name,
            replace=True
        )
        logger.info(f"✅ Hourly file saved: s3://{bucket_name}/{hourly_key}")
    except Exception as e:
        logger.error(f"❌ Error saving hourly file: {e}")
    
    # --- DAILY FILE (Smart update: Insert new, Update changed, Skip unchanged) ---
    daily_key = f'daily/marketplace_{date_str}.csv'
    
    try:
        if s3_hook.check_for_key(key=daily_key, bucket_name=bucket_name):
            # Read existing daily file
            existing_csv = s3_hook.read_key(key=daily_key, bucket_name=bucket_name)
            existing_df = pd.read_csv(StringIO(existing_csv))
            logger.info(f"📊 Existing daily file has {len(existing_df)} rows")
            
            # Create a copy for comparison
            updated_df = existing_df.copy()
            
            # Process each new row
            for idx, new_row in new_df.iterrows():
                new_url = new_row['url']
                
                # Check if URL exists in existing data
                existing_mask = existing_df['url'] == new_url
                
                if existing_mask.any():
                    # URL exists - check if data changed
                    existing_row = existing_df[existing_mask].iloc[0]
                    
                    # Compare key fields (excluding scraped_at timestamp)
                    compare_fields = ['title', 'price', 'location', 'condition', 'description', 'image_url']
                    has_changes = False
                    
                    for field in compare_fields:
                        if field in new_row and field in existing_row:
                            new_val = str(new_row[field])
                            old_val = str(existing_row[field])
                            if new_val != old_val and new_val != 'N/A':
                                has_changes = True
                                break
                    
                    if has_changes:
                        # Update existing row with new data - ใช้ index ที่ถูกต้อง
                        idx_to_update = updated_df[updated_df['url'] == new_url].index[0]
                        updated_df.loc[idx_to_update] = new_row.values
                        stats['updated_items'] += 1
                        logger.info(f"   🔄 Updated: {new_row['title'][:40]}...")
                    else:
                        # No changes - skip
                        stats['unchanged_items'] += 1
                        logger.debug(f"   ⏭️  Unchanged: {new_row['title'][:40]}...")
                else:
                    # New URL - append to dataframe
                    updated_df = pd.concat([updated_df, pd.DataFrame([new_row])], ignore_index=True)
                    stats['new_items'] += 1
                    logger.info(f"   ➕ New: {new_row['title'][:40]}...")
            
            combined_df = updated_df
            
        else:
            # First time today - all rows are new
            combined_df = new_df
            stats['new_items'] = len(new_df)
            logger.info(f"📊 Creating new daily file with {len(combined_df)} rows")
        
        # Save updated daily file
        daily_csv_buffer = StringIO()
        combined_df.to_csv(daily_csv_buffer, index=False)
        daily_csv_content = daily_csv_buffer.getvalue()
        
        s3_hook.load_string(
            string_data=daily_csv_content,
            key=daily_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Log statistics
        logger.info("\n" + "="*60)
        logger.info("📊 Daily File Update Summary:")
        logger.info("="*60)
        logger.info(f"   ➕ New items inserted:      {stats['new_items']}")
        logger.info(f"   🔄 Existing items updated:  {stats['updated_items']}")
        logger.info(f"   ⏭️  Unchanged items skipped: {stats['unchanged_items']}")
        logger.info(f"   📦 Total items in daily:    {len(combined_df)}")
        logger.info("="*60)
        
        logger.info(f"✅ Daily file saved: s3://{bucket_name}/{daily_key}")
        
    except Exception as e:
        logger.error(f"❌ Error saving daily file: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return {
        'hourly_file': hourly_key,
        'daily_file': daily_key,
        'total_scraped': stats['total_scraped'],
        'new_items': stats['new_items'],
        'updated_items': stats['updated_items'],
        'unchanged_items': stats['unchanged_items'],
        'daily_total': len(combined_df) if 'combined_df' in locals() else len(new_df)
    }

def analyze_detailed_data(**context):
    """Analyze the detailed scraped data"""
    csv_content = context['ti'].xcom_pull(key='marketplace_data_detailed', task_ids='scrape_with_details')
    upload_result = context['ti'].xcom_pull(task_ids='upload_detailed_data')
    
    if not csv_content:
        return None
    
    df = pd.read_csv(StringIO(csv_content))
    
    analysis = {
        'total_items_scraped': len(df),
        'with_condition': len(df[df['condition'] != 'N/A']),
        'with_description': len(df[df['description'] != 'N/A']),
        'locations': df['location'].unique().tolist(),
        'timestamp': datetime.now().isoformat()
    }
    
    if upload_result:
        analysis.update({
            'hourly_file': upload_result.get('hourly_file'),
            'daily_file': upload_result.get('daily_file'),
            'new_items': upload_result.get('new_items'),
            'updated_items': upload_result.get('updated_items'),
            'unchanged_items': upload_result.get('unchanged_items'),
            'daily_total_rows': upload_result.get('daily_total')
        })
    
    logger.info("\n" + "="*70)
    logger.info("📊 FINAL REPORT - Facebook Marketplace Scraper")
    logger.info("="*70)
    logger.info(f"   📦 Items scraped this run:  {analysis['total_items_scraped']}")
    logger.info(f"   🏷️  With condition info:    {analysis['with_condition']}")
    logger.info(f"   📝 With description:        {analysis['with_description']}")
    logger.info(f"   📍 Locations found:         {', '.join(analysis['locations'][:5])}")
    
    if upload_result:
        logger.info(f"\n   📁 Hourly file:             {analysis['hourly_file']}")
        logger.info(f"   📁 Daily file:              {analysis['daily_file']}")
        logger.info(f"\n   ➕ New items inserted:      {analysis['new_items']}")
        logger.info(f"   🔄 Items updated:           {analysis['updated_items']}")
        logger.info(f"   ⏭️  Items unchanged:         {analysis['unchanged_items']}")
        logger.info(f"   📊 Daily file total rows:   {analysis['daily_total_rows']}")
    
    logger.info("="*70 + "\n")
    
    return analysis

# Define DAG
with DAG(
    'marketplace_scraper_with_details',
    default_args=default_args,
    description='Scrape Facebook Marketplace with deduplication (hourly replace, daily append)',
    schedule_interval='0 * * * *',  # Run every hour
    catchup=False,
    tags=['marketplace', 'scraping', 'selenium', 'detailed', 'dedup'],
    params={
        'keyword': 'iphone 13',
        'location': 'bangkok',
        'radius': 20,
        'max_items': 10,
        'fetch_details': True
    }
) as dag:
    
    task_scrape = PythonOperator(
        task_id='scrape_with_details',
        python_callable=scrape_with_details,
    )
    
    task_upload = PythonOperator(
        task_id='upload_detailed_data',
        python_callable=upload_detailed_data,
    )
    
    task_analyze = PythonOperator(
        task_id='analyze_data',
        python_callable=analyze_detailed_data,
    )
    
    task_scrape >> task_upload >> task_analyze
