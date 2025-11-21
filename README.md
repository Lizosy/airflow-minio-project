# Facebook Marketplace ETL Pipeline - Data Engineering Project

Complete end-to-end data pipeline for scraping, processing, and analyzing Facebook Marketplace data using Apache Airflow, MinIO, and PostgreSQL.

## 🎓 Course Requirements Coverage

This project fulfills all Data Engineering course requirements:

### ✅ 1. Data Acquisition
- **Method:** Web Scraping using Selenium + BeautifulSoup
- **Source:** Facebook Marketplace Thailand (https://facebook.com/marketplace)
- **Ethical Considerations:**
  - Respects rate limiting (2-second delays between requests)
  - Only scrapes publicly available data
  - No personal information collected
  - Follows robots.txt guidelines

### ✅ 2. Data Storage (Multi-tier Architecture)
- **Raw Data:** MinIO/S3 (CSV format)
  - Human-readable for debugging
  - Easy to inspect and validate
- **Processed Data:** Parquet format (MinIO/S3)
  - Column-oriented storage
  - Snappy compression
  - Optimized for analytics queries
- **Structured Data:** PostgreSQL database
  - ACID compliance
  - Complex querying support
  - Data integrity enforcement

### ✅ 3. Data Cleaning & Transformation (Pandas)
Comprehensive 8-step data quality pipeline:
1. **Missing Value Handling:** Drop critical nulls, fill non-critical fields
2. **Data Type Correction:** Parse dates, convert numeric fields
3. **Price Data Cleaning:** Extract numeric values from Thai Baht strings using regex
4. **Text Standardization:** Clean titles, standardize locations, lowercase normalization
5. **Feature Engineering:** Extract phone models, create price categories
6. **Deduplication:** Remove duplicate URLs while preserving first occurrence
7. **Outlier Detection:** Flag price outliers using quantile-based method
8. **Data Validation:** URL validation, length checks, schema enforcement

### ✅ 4. Data Loading & Verification
- **Multi-format Storage:** Parquet, CSV, PostgreSQL
- **Quality Checks:**
  - Row count validation
  - Schema verification
  - Data type consistency
  - Summary statistics generation
  - Completeness metrics
  - Outlier reporting

### ✅ 5. Reproducibility & Containerization
- **Docker Compose:** Multi-service orchestration
- **Custom Dockerfile:** Airflow with Chrome/Selenium
- **Environment Variables:** `.env` configuration
- **requirements.txt:** All Python dependencies
- **Documentation:** Comprehensive setup instructions

### ✅ 6. Advanced Components
- **Apache Airflow:** Complete DAG orchestration with error handling
- **Workflow Management:** Branching, retry logic, trigger rules
- **Production Ready:** Logging, monitoring, cleanup tasks

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Apache Airflow                           │
│  (Workflow Orchestration & Scheduling)                      │
└───────────────────┬─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐   ┌──────▼──────┐   ┌──▼─────┐
│ Scrape │   │  Transform  │   │ Verify │
│  Data  │   │  & Clean    │   │ Quality│
└───┬────┘   └──────┬──────┘   └────────┘
    │               │
    │        ┌──────┴──────┐
    │        │             │
┌───▼────┐ ┌─▼──────┐ ┌───▼────────┐
│ MinIO  │ │ MinIO  │ │ PostgreSQL │
│  (Raw) │ │(Parquet│ │  (Table)   │
└────────┘ └────────┘ └────────────┘
```

## 🗂️ Project Structure

```
airflow-minio-project/
├── dags/                                    # Airflow DAG files
│   ├── complete_etl_pipeline_dag.py        # ⭐ Main project (all requirements)
│   ├── marketplace_advanced_flow_dag.py    # Advanced parallel workflow
│   ├── marketplace_scraper_detailed_dag.py # Detailed scraper with dedup
│   └── etl_pipeline_dag.py                 # Legacy ETL example
├── logs/                                    # Airflow execution logs
├── plugins/                                 # Custom Airflow plugins
├── config/                                  # Configuration files
├── scripts/                                 # Utility scripts
│   ├── init-airflow.sh                     # Airflow initialization
│   └── test-minio.py                       # MinIO connection test
├── docker-compose.yml                       # Multi-service orchestration
├── Dockerfile                               # Custom Airflow image with Chrome
├── requirements.txt                         # Python dependencies
├── .env                                     # Environment variables
├── README.md                                # This file
├── QUICKSTART.md                            # Quick start guide
├── FILE_STRUCTURE.md                        # Detailed structure docs
└── AIRFLOW_VARIABLES_SETUP.md              # Credentials setup guide
```

## 🚀 วิธีการใช้งาน

### 1. เริ่มต้น Airflow + MinIO

```bash
# เข้าไปที่โฟลเดอร์โปรเจค
cd airflow-minio-project

# Start services
docker-compose up -d

# ดู logs
docker-compose logs -f
```

### 2. เข้าใช้งาน Web UI

**Airflow Web UI:**
- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

**MinIO Console:**
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

### 3. ตรวจสอบสถานะ

```bash
# ดูสถานะ containers
docker-compose ps

# ดู logs ของ Airflow
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# ดู logs ของ MinIO
docker-compose logs minio
```

### 4. หยุดและลบ services

```bash
# หยุด services
docker-compose down

# หยุดและลบ volumes (ข้อมูลจะหายหมด!)
docker-compose down -v
```

## 📊 Available DAGs

### 1. `complete_etl_pipeline` ⭐ **Main Project DAG**
- **Schedule:** Every 6 hours
- **Description:** Complete ETL pipeline meeting all course requirements
- **Pipeline Stages:**
  1. **Data Acquisition:** Scrape Facebook Marketplace
  2. **Store Raw Data:** Save to MinIO (CSV)
  3. **Clean & Transform:** 8-step Pandas pipeline
  4. **Store Processed:** Parquet + PostgreSQL
  5. **Verify Quality:** Statistics & validation
- **Features:**
  - Comprehensive data cleaning
  - Multi-format storage
  - Quality verification
  - Error handling & retries
  - Detailed logging

### 2. `marketplace_advanced_flow`
- **Schedule:** Every 6 hours
- **Description:** Advanced workflow with parallel scraping
- **Features:**
  - Parallel keyword scraping
  - Data validation branching
  - Smart storage (by keyword)
  - Auto cleanup (30-day retention)
  - Failure handling

### 3. `marketplace_scraper_with_details`
- **Schedule:** Hourly
- **Description:** Detailed scraper with deduplication
- **Features:**
  - Login support (Airflow Variables)
  - Detail fetching (condition, description)
  - Smart deduplication (insert/update/skip)
  - Hourly files (replace mode)
  - Daily files (append mode)

### 4. `etl_pipeline_minio` (Legacy)
- **Schedule:** Hourly
- **Description:** Basic ETL example
- **Tasks:** Extract → Transform → Load → Report

## 🗂️ MinIO Storage Structure

```
marketplace-data/
├── raw/                           # Raw scraped data (CSV)
│   └── marketplace_raw_YYYYMMDD_HHMMSS.csv
├── processed/                     # Cleaned & transformed data
│   ├── marketplace_clean_YYYYMMDD_HHMMSS.parquet  # Analytics format
│   └── marketplace_clean_YYYYMMDD_HHMMSS.csv      # Compatibility
├── hourly/                        # Hourly snapshots (replace mode)
│   └── marketplace_YYYYMMDD_HH.csv
├── daily/                         # Daily cumulative (append mode)
│   └── marketplace_YYYYMMDD.csv
└── by_keyword/                    # Organized by search keyword
    ├── iphone_13_YYYYMMDD_HHMMSS.csv
    └── samsung_galaxy_YYYYMMDD_HHMMSS.csv
```

## 📊 PostgreSQL Schema

```sql
CREATE TABLE marketplace_listings (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    title_clean TEXT,
    phone_model VARCHAR(50),
    price VARCHAR(50),
    price_numeric DECIMAL(10,2),
    price_category VARCHAR(50),
    is_price_outlier BOOLEAN,
    location TEXT,
    location_clean VARCHAR(100),
    keyword VARCHAR(100),
    search_location VARCHAR(100),
    radius_km INTEGER,
    image_url TEXT,
    scraped_at TIMESTAMP,
    days_since_scraped INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Airflow Variables (Required for Scraping with Login)

Set these in Airflow UI: Admin → Variables

```
Key: fb_marketplace_email
Value: your.email@example.com

Key: fb_marketplace_password
Value: your_password
```

See [AIRFLOW_VARIABLES_SETUP.md](AIRFLOW_VARIABLES_SETUP.md) for detailed instructions.

### MinIO Connection (Auto-configured)

Already configured in `docker-compose.yml`:
- **Conn Id:** `minio_default`
- **Conn Type:** `AWS`
- **Access Key:** `minioadmin`
- **Secret Key:** `minioadmin`
- **Endpoint:** `http://minio:9000`

### PostgreSQL Connection (Auto-configured)

Already configured in `docker-compose.yml`:
- **Conn Id:** `postgres_default`
- **Host:** `postgres`
- **Database:** `airflow`
- **User:** `airflow`
- **Password:** `airflow`
- **Port:** `5432`

## 🎯 Running the Main ETL Pipeline

### 1. Start Services

```bash
cd airflow-minio-project
docker-compose up -d
```

### 2. Access Airflow UI

Open http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### 3. Configure DAG Parameters (Optional)

Click on `complete_etl_pipeline` DAG → Trigger DAG with config:

```json
{
  "keyword": "iphone 13",
  "location": "bangkok",
  "radius": 20,
  "max_items": 50
}
```

### 4. Monitor Execution

- View logs for each task
- Check data in MinIO Console (http://localhost:9001)
- Query PostgreSQL data

### 5. View Results

**MinIO Console:** http://localhost:9001
- Browse `marketplace-data` bucket
- Download Parquet/CSV files

**PostgreSQL:**
```bash
docker exec -it airflow-minio-project-postgres-1 psql -U airflow -d airflow
```

```sql
-- View scraped data
SELECT * FROM marketplace_listings ORDER BY scraped_at DESC LIMIT 10;

-- Price statistics
SELECT 
    phone_model,
    COUNT(*) as count,
    AVG(price_numeric) as avg_price,
    MIN(price_numeric) as min_price,
    MAX(price_numeric) as max_price
FROM marketplace_listings
WHERE price_numeric IS NOT NULL
GROUP BY phone_model
ORDER BY count DESC;
```
    
    # Upload file
    s3_hook.load_string(
        string_data="Hello MinIO!",
        key="my_file.txt",
        bucket_name="raw-data"
    )
    
    print("✅ Uploaded successfully!")

with DAG(
    'my_new_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:
    
    task = PythonOperator(
        task_id='upload_task',
        python_callable=my_function,
    )
```

## 🐛 Troubleshooting

### ปัญหา: Airflow ไม่เห็น DAGs

```bash
# เช็คว่า DAG files อยู่ในโฟลเดอร์ที่ถูกต้อง
ls -la dags/

# ดู logs ของ scheduler
docker-compose logs airflow-scheduler
```

### ปัญหา: ไม่สามารถเชื่อมต่อ MinIO

```bash
# เช็ค MinIO service
docker-compose ps minio

# ทดสอบเชื่อมต่อ
curl http://localhost:9000/minio/health/live
```

### ปัญหา: Permission denied

```bash
# ตั้งค่า permissions
chmod -R 777 logs/
chmod -R 777 dags/
chmod -R 777 plugins/
```

## 📚 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [Airflow S3 Provider](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html)

## 🔐 Security Notes

**⚠️ สำคัญ:** ตัวอย่างนี้ใช้ credentials เริ่มต้นสำหรับการพัฒนาเท่านั้น

สำหรับ Production:
- เปลี่ยน passwords ทั้งหมด
- ใช้ secret management (Vault, AWS Secrets Manager)
- ตั้งค่า SSL/TLS
- กำหนด network policies
- เปิด authentication และ authorization

## 📄 License

This project is for educational purposes.

---

**Created:** November 2025
**Author:** team Cheesedip
