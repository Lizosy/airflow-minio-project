# 🚀 Facebook Marketplace Data Pipeline - Complete ETL Project

Complete end-to-end data engineering pipeline for scraping, processing, and analyzing Facebook Marketplace data using Apache Airflow, MinIO, PostgreSQL, and advanced data transformation techniques.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Airflow](https://img.shields.io/badge/Airflow-2.7+-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![MinIO](https://img.shields.io/badge/MinIO-S3-red)

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
**DAG ID:** `complete_etl_pipeline`  
**Schedule:** Every 6 hours (`0 */6 * * *`)  
**Purpose:** Complete ETL pipeline meeting all course requirements

**Pipeline Stages:**
1. **scrape_raw_data** - Web scraping with Selenium + BeautifulSoup
2. **store_raw_data** - Save raw CSV to MinIO
3. **clean_transform_data** - 8-step data quality pipeline with Pandas
4. **store_processed_data** - Save Parquet to MinIO + load to PostgreSQL
5. **verify_data_quality** - Validate schema, types, and generate statistics
6. **generate_quality_report** - Create comprehensive quality summary

**Key Features:**
- ✅ Full ETL lifecycle (Extract → Transform → Load)
- ✅ Multi-format storage (CSV, Parquet, PostgreSQL)
- ✅ 8-step data cleaning pipeline
- ✅ Price outlier detection (quantile-based)
- ✅ Phone model extraction from titles
- ✅ Quality verification with assertions
- ✅ Automatic error handling & retries
- ✅ Detailed logging at each stage

**Best For:** Production use, course submission, complete data pipeline

---

### 2. `marketplace_advanced_flow`
**DAG ID:** `marketplace_advanced_flow`  
**Schedule:** Every 6 hours (`0 */6 * * *`)  
**Purpose:** Advanced workflow with parallel scraping

**Pipeline Stages:**
1. **start** - Initialize workflow
2. **scrape_[keyword]** - Parallel scraping for multiple keywords
3. **validate_data_quality** - Check data completeness (branching logic)
4. **store_data_[keyword]** - Save by keyword to MinIO
5. **cleanup_old_files** - Remove files older than 30 days
6. **notify_success / notify_failure** - Status notifications

**Key Features:**
- 🔄 Parallel execution (scrape multiple keywords simultaneously)
- 🌲 Branching logic (skip bad data automatically)
- 📁 Organized storage (by_keyword/ folder structure)
- 🧹 Auto cleanup (30-day retention policy)
- 🔔 Success/failure notifications
- ⚡ Optimized for high-volume scraping

**Best For:** Large-scale scraping, multiple product categories, production scalability

---

### 3. `marketplace_scraper_with_details`
**DAG ID:** `marketplace_scraper_with_details`  
**Schedule:** Hourly (`0 * * * *`)  
**Purpose:** Detailed scraper with smart deduplication

**Pipeline Stages:**
1. **scrape_marketplace_data** - Scrape with optional login (Airflow Variables)
2. **fetch_product_details** - Get detailed info (condition, description, specs)
3. **deduplicate_and_store** - Smart dedup logic (insert/update/skip)
4. **save_hourly_snapshot** - Replace mode (hourly files)
5. **save_daily_cumulative** - Append mode (daily aggregation)

**Key Features:**
- 🔐 Login support (via Airflow Variables: fb_marketplace_email, fb_marketplace_password)
- 📝 Detailed product information (condition, full description)
- 🔍 Smart deduplication:
  - **Insert** - New URLs
  - **Update** - Existing URLs with different data
  - **Skip** - Exact duplicates
- ⏰ Hourly snapshots (marketplace_YYYYMMDD_HH.csv)
- 📅 Daily cumulative (marketplace_YYYYMMDD.csv)
- 🎯 URL-based duplicate detection

**Best For:** Frequent monitoring, price tracking, detailed product analysis

---

### 4. `marketplace_scraper` (Basic Version)
**DAG ID:** `facebook_marketplace_scraper`  
**Schedule:** Every 6 hours (`0 */6 * * *`)  
**Purpose:** Simple scraper for learning

**Pipeline Stages:**
1. **scrape_marketplace** - Basic scraping (title, price, location)
2. **store_to_minio** - Save CSV to MinIO

**Key Features:**
- 📱 Basic info only (title, price, location, image)
- 💾 Simple storage (CSV to MinIO)
- 🎓 Clean, readable code
- 🚀 Fast execution

**Best For:** Learning, testing, basic scraping needs

---

### 5. `etl_pipeline_minio` (Legacy/Example)
**DAG ID:** `etl_pipeline_minio`  
**Schedule:** Hourly (`@hourly`)  
**Purpose:** ETL reference implementation

**Pipeline Stages:**
1. **extract_from_minio** - Read raw data from MinIO
2. **transform_data** - Basic cleaning and aggregation
3. **load_to_minio** - Write back to MinIO
4. **generate_report** - Create summary statistics

**Best For:** Learning ETL concepts, post-processing existing data

---

### 6. `minio_upload_example`
**DAG ID:** `minio_upload_example`  
**Schedule:** Daily (`@daily`)  
**Purpose:** Test MinIO connection

**Pipeline Stages:**
1. **test_connection** - Verify MinIO connectivity
2. **create_bucket** - Ensure bucket exists
3. **upload_test_file** - Upload sample file
4. **list_files** - Display bucket contents

**Best For:** Testing MinIO setup, debugging connection issues

---

## 📊 DAG Comparison Table

| DAG | Complexity | Speed | Detail Level | Best Use Case |
|-----|-----------|-------|-------------|---------------|
| `complete_etl_pipeline` ⭐ | ⭐⭐⭐⭐⭐ | Medium | Very High | Production, Course Submission |
| `marketplace_advanced_flow` | ⭐⭐⭐⭐ | Fast | High | Large-scale, Multi-keyword |
| `marketplace_scraper_with_details` | ⭐⭐⭐ | Medium | Very High | Price Tracking, Details |
| `marketplace_scraper` | ⭐⭐ | Fast | Medium | Learning, Basic Scraping |
| `etl_pipeline_minio` | ⭐⭐ | Fast | Low | ETL Learning, Reprocessing |
| `minio_upload_example` | ⭐ | Very Fast | N/A | Testing, Debugging |

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

### Issue: Airflow DAGs not appearing

```bash
# Check DAG files exist
ls -la dags/

# View scheduler logs
docker-compose logs airflow-scheduler | tail -50

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Issue: Cannot connect to MinIO

```bash
# Check MinIO service status
docker-compose ps minio

# Test MinIO health
curl http://localhost:9000/minio/health/live

# Restart MinIO
docker-compose restart minio
```

### Issue: Permission denied errors

```bash
# Windows (CMD/PowerShell)
icacls logs /grant Everyone:F /t
icacls dags /grant Everyone:F /t
icacls plugins /grant Everyone:F /t

# Linux/Mac
chmod -R 777 logs/
chmod -R 777 dags/
chmod -R 777 plugins/
```

### Issue: Out of memory

```bash
# Increase Docker memory limit to at least 4GB
# Docker Desktop → Settings → Resources → Memory

# Or reduce Airflow workers
# Edit docker-compose.yml:
# AIRFLOW__CELERY__WORKER_CONCURRENCY: 2
```

### Issue: Selenium/Chrome errors

```bash
# The Dockerfile already includes Chrome
# If issues persist, rebuild:
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: PostgreSQL connection failed

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Access PostgreSQL directly
docker exec -it airflow-minio-project-postgres-1 psql -U airflow

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
```

### Issue: DAG runs stuck in "running" state

```bash
# Clear task instances
docker exec -it airflow-minio-project-airflow-scheduler-1 \
  airflow tasks clear complete_etl_pipeline

# Or via UI: Browse → Task Instances → Select → Actions → Clear
```

## 🔄 Update to Latest Version

If someone cloned your repository and wants to update:

```bash
# Navigate to project folder
cd airflow-minio-project

# Pull latest changes
git pull origin main

# Restart Docker to apply changes
docker-compose down
docker-compose up -d --build
```

## 🌐 Deployment to DigitalOcean

### Requirements
- Droplet: 4GB RAM minimum (Basic $24/month)
- Ubuntu 22.04 LTS
- Volume: 50-100GB for data storage

### Setup Steps

```bash
# 1. Install Docker
sudo apt update
sudo apt install docker.io docker-compose git -y
sudo systemctl enable docker
sudo systemctl start docker

# 2. Clone repository
git clone https://github.com/Lizosy/airflow-minio-project.git
cd airflow-minio-project

# 3. Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8080/tcp  # Airflow
sudo ufw allow 9000/tcp  # MinIO API
sudo ufw allow 9001/tcp  # MinIO Console
sudo ufw enable

# 4. Update docker-compose.yml (change localhost to your IP/domain)
# Edit AIRFLOW__WEBSERVER__BASE_URL
# Edit MINIO_ENDPOINT

# 5. Start services
docker-compose up -d

# 6. Monitor logs
docker-compose logs -f
```

### Security Checklist
- [ ] Change default passwords (Airflow, MinIO, PostgreSQL)
- [ ] Use SSH keys instead of passwords
- [ ] Setup SSL/HTTPS with Nginx + Let's Encrypt
- [ ] Limit IP access to admin panels
- [ ] Enable firewall rules
- [ ] Setup automated backups

## 📚 Additional Documentation

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [Airflow S3 Provider](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🎓 Learning Resources

- **Project Files:**
  - `QUICKSTART.md` - Quick setup guide
  - `FILE_STRUCTURE.md` - Detailed file organization
  - `AIRFLOW_VARIABLES_SETUP.md` - Credentials configuration

- **Key Concepts Covered:**
  - ETL Pipeline Design
  - Web Scraping Ethics & Techniques
  - Data Quality Management
  - Workflow Orchestration
  - Container Orchestration
  - Object Storage (S3-compatible)
  - Relational Databases
  - Data Serialization Formats

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork the repository
- Submit issues
- Suggest improvements
- Share your modifications

## ⚖️ Legal & Ethical Considerations

**Web Scraping Guidelines:**
- ✅ Only scrapes publicly available data
- ✅ Respects rate limiting (2-3 second delays)
- ✅ No personal information collected
- ✅ Follows robots.txt guidelines
- ✅ Educational purpose only

**Production Use:**
- Review Facebook's Terms of Service
- Implement proper authentication
- Use official APIs when available
- Respect data privacy laws (GDPR, PDPA)

## 📊 Project Statistics

- **Lines of Code:** ~2,000+ Python
- **DAGs:** 6 different workflow patterns
- **Data Quality Steps:** 8-stage cleaning pipeline
- **Storage Formats:** 3 (CSV, Parquet, PostgreSQL)
- **Docker Services:** 7 containers
- **Technologies:** 10+ frameworks/tools

## 🏆 Course Compliance Summary

| Requirement | Implementation | Status |
|------------|----------------|--------|
| Data Acquisition | Selenium + BeautifulSoup web scraping | ✅ Complete |
| Data Storage | MinIO (S3) + PostgreSQL + Parquet | ✅ Complete |
| Data Cleaning | 8-step Pandas pipeline | ✅ Complete |
| Data Transformation | Feature engineering, normalization | ✅ Complete |
| Data Loading | Multi-format storage with verification | ✅ Complete |
| Reproducibility | Docker Compose + requirements.txt | ✅ Complete |
| Documentation | Comprehensive README + guides | ✅ Complete |
| Workflow Orchestration | Apache Airflow DAGs | ✅ Complete |

## 🔐 Security Notes

**⚠️ Important:** Default credentials are for development only!

**For Production:**
- Change all default passwords
- Use environment variables for secrets
- Implement secret management (Vault, AWS Secrets Manager)
- Enable SSL/TLS certificates
- Configure network policies
- Enable authentication & authorization
- Setup monitoring & alerts
- Implement backup strategies

## 📝 Version History

- **v1.0** (Nov 2025) - Initial release with complete ETL pipeline
- **v1.1** (Nov 2025) - Added advanced workflow patterns
- **v1.2** (Nov 2025) - Enhanced data quality checks
- **v1.3** (Nov 2025) - Fixed JSON serialization, datetime parsing

## 📧 Contact & Support

**Repository:** https://github.com/Lizosy/airflow-minio-project  
**Issues:** https://github.com/Lizosy/airflow-minio-project/issues

For questions or support:
1. Check documentation in `/docs` folder
2. Review existing issues on GitHub
3. Submit new issue with detailed description

## 📄 License

This project is for **educational purposes only**.

Use at your own risk. The authors are not responsible for any misuse or violations of third-party terms of service.

---

**Created:** November 2025  
**Team:** Cheesedip  
**Course:** Data Engineering  
**University:** [Your University Name]

---

### ⭐ If this project helped you, please give it a star!

Made with ❤️ for Data Engineering students
