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

### 1. `complete_etl_pipeline` ⭐ **Main Project**
**Schedule:** Every 6 hours | **Purpose:** Complete ETL pipeline for course requirements

**Pipeline:** Scrape → Store Raw → Clean/Transform → Store Processed → Verify → Report

**Features:**
- ✅ Full ETL lifecycle with 8-step data cleaning
- ✅ Multi-format storage (CSV, Parquet, PostgreSQL)
- ✅ Price outlier detection & phone model extraction
- ✅ Quality verification & error handling

**Best For:** Production use, course submission

---

### 2. `marketplace_advanced_flow`
**Schedule:** Every 6 hours | **Purpose:** Parallel scraping workflow

**Features:**
- 🔄 Parallel keyword scraping
- 🌲 Branching logic (auto skip bad data)
- 🧹 Auto cleanup (30-day retention)
- 📁 Organized by keyword

**Best For:** Large-scale scraping, multiple categories

---

### 3. `marketplace_scraper_with_details`
**Schedule:** Hourly | **Purpose:** Detailed scraper with deduplication

**Features:**
- 🔐 Login support (Airflow Variables)
- 📝 Detailed info (condition, description)
- 🔍 Smart dedup (insert/update/skip)
- ⏰ Hourly + daily snapshots

**Best For:** Price tracking, detailed analysis

---

### 4. `marketplace_scraper` (Basic)
**Schedule:** Every 6 hours | **Purpose:** Simple scraper for learning

**Features:**
- 📱 Basic info (title, price, location)
- 🚀 Fast execution, clean code

**Best For:** Learning, testing

---

### 5. `etl_pipeline_minio` (Legacy)
**Schedule:** Hourly | **Purpose:** ETL reference

**Pipeline:** Extract → Transform → Load → Report

**Best For:** Learning ETL concepts

---

### 6. `minio_upload_example`
**Schedule:** Daily | **Purpose:** Test MinIO connection

**Best For:** Testing setup

---

## 📊 Quick Comparison

| DAG | Complexity | Speed | Best For |
|-----|-----------|-------|----------|
| `complete_etl_pipeline` ⭐ | High | Medium | Production, Submission |
| `marketplace_advanced_flow` | High | Fast | Large-scale, Multi-keyword |
| `marketplace_scraper_with_details` | Medium | Medium | Tracking, Details |
| `marketplace_scraper` | Low | Fast | Learning, Testing |
| `etl_pipeline_minio` | Low | Fast | ETL Learning |
| `minio_upload_example` | Very Low | Very Fast | Testing |

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

## 📊 Project Statistics

- **Lines of Code:** ~2,000+ Python
- **DAGs:** 6 different workflow patterns
- **Data Quality Steps:** 8-stage cleaning pipeline
- **Storage Formats:** 3 (CSV, Parquet, PostgreSQL)
- **Docker Services:** 7 containers
- **Technologies:** 10+ frameworks/tools

---

**Created:** November 2025  
**Team:** Cheesedip  
**Course:** Data Engineering
