# 🔐 Airflow Variables Setup Guide

คู่มือการตั้งค่า Variables สำหรับเก็บ Email และ Password อย่างปลอดภัย

## 📋 วิธีที่ 1: ผ่าน Airflow Web UI (แนะนำ)

### 1. เข้า Airflow Web UI
```
http://localhost:8080
Login: airflow / airflow
```

### 2. ไปที่ Admin Menu
```
Admin → Variables
```

### 3. เพิ่ม Variable ใหม่
คลิก **"+"** หรือ **"Add a new record"**

#### Variable 1: Email
```
Key: fb_marketplace_email
Val: your_email@gmail.com
Description: Facebook email for marketplace scraper
```

#### Variable 2: Password (แบบปลอดภัย)
```
Key: fb_marketplace_password
Val: your_password_here
Description: Facebook password for marketplace scraper
```

✅ Airflow จะ **เข้ารหัส** password โดยอัตโนมัติ

### 4. Save
คลิก **Save**

---

## 📋 วิธีที่ 2: ผ่าน Airflow CLI (ใน Container)

### 1. เข้าไปใน Airflow Container
```cmd
docker exec -it airflow-minio-project-airflow-webserver-1 bash
```

### 2. ตั้งค่า Variables
```bash
# Set Email
airflow variables set fb_marketplace_email "your_email@gmail.com"

# Set Password
airflow variables set fb_marketplace_password "your_password_here"
```

### 3. ตรวจสอบ Variables
```bash
# List all variables
airflow variables list

# Get specific variable
airflow variables get fb_marketplace_email
```

### 4. ออกจาก Container
```bash
exit
```

---

## 📋 วิธีที่ 3: ผ่าน JSON File (Bulk Import)

### 1. สร้างไฟล์ JSON
สร้างไฟล์ `variables.json`:
```json
{
  "fb_marketplace_email": "your_email@gmail.com",
  "fb_marketplace_password": "your_password_here"
}
```

### 2. Import ผ่าน Web UI
```
Admin → Variables → Import Variables
เลือกไฟล์ variables.json
```

### 3. หรือ Import ผ่าน CLI
```bash
docker exec -it airflow-minio-project-airflow-webserver-1 bash
airflow variables import /path/to/variables.json
exit
```

---

## 📋 วิธีที่ 4: ผ่าน Environment Variables (Docker)

### 1. แก้ไขไฟล์ `.env`
```env
# เพิ่มบรรทัดนี้
AIRFLOW_VAR_FB_MARKETPLACE_EMAIL=your_email@gmail.com
AIRFLOW_VAR_FB_MARKETPLACE_PASSWORD=your_password_here
```

### 2. Restart Services
```cmd
cd e:\01\dowload\34\airflow-minio-project
docker-compose restart
```

---

## 🔍 ตรวจสอบว่าตั้งค่าสำเร็จ

### ผ่าน Web UI:
```
Admin → Variables
ควรเห็น:
- fb_marketplace_email
- fb_marketplace_password
```

### ผ่าน CLI:
```bash
docker exec -it airflow-minio-project-airflow-webserver-1 \
  airflow variables get fb_marketplace_email
```

---

## 🎯 วิธีใช้งานใน DAG

DAG จะดึง Variables โดยอัตโนมัติ:

```python
# ใน scrape_with_details() function
email = Variable.get("fb_marketplace_email", default_var=None)
password = Variable.get("fb_marketplace_password", default_var=None)
```

### ลำดับความสำคัญ (Priority):
1. **DAG params** (ถ้าส่งมาตอน Trigger)
2. **Airflow Variables** (ถ้าไม่มี params)
3. **None** (ถ้าไม่มีทั้งสองอย่าง = ไม่ login)

---

## 🚀 ทดสอบ

### Test 1: Run DAG โดยใช้ Variables
```
1. Trigger DAG: marketplace_scraper_with_details
2. ไม่ต้องใส่ email/password ใน params
3. DAG จะใช้ค่าจาก Variables
```

### Test 2: Run DAG โดย Override Variables
```
1. Trigger DAG with config
2. ใส่ params:
{
  "keyword": "iphone 13",
  "email": "another_email@gmail.com",
  "password": "another_password"
}
3. DAG จะใช้ค่าจาก params แทน Variables
```

---

## 🗑️ ลบ Variables

### ผ่าน Web UI:
```
Admin → Variables
เลือก Variable → Delete
```

### ผ่าน CLI:
```bash
docker exec -it airflow-minio-project-airflow-webserver-1 bash
airflow variables delete fb_marketplace_email
airflow variables delete fb_marketplace_password
exit
```

---

## 🔐 Best Practices

### ✅ ควรทำ:
- ใช้ Airflow Variables สำหรับข้อมูลที่เป็นความลับ
- ใช้ Admin → Variables ผ่าน Web UI (ง่ายที่สุด)
- ตรวจสอบว่าตั้งค่าถูกต้องก่อนรัน DAG

### ❌ ไม่ควรทำ:
- ❌ เขียน email/password ใน DAG code โดยตรง
- ❌ Commit ไฟล์ที่มี credentials ลง Git
- ❌ Share password ผ่านช่องทาง public

---

## 🆘 แก้ปัญหา

### ปัญหา: DAG ไม่เจอ Variables
```python
# เช็คใน DAG logs:
Could not get credentials from Variables
```

**วิธีแก้:**
1. ตรวจสอบว่าตั้ง Variables แล้ว (Admin → Variables)
2. Restart Airflow Scheduler:
   ```cmd
   docker-compose restart airflow-scheduler
   ```

### ปัญหา: Login ไม่สำเร็จ
```python
# เช็คใน DAG logs:
⚠️ Login อาจไม่สำเร็จ
```

**วิธีแก้:**
1. ตรวจสอบ email/password ถูกต้อง
2. Facebook อาจบล็อก login จาก bot
3. ลองใช้ App Password แทน password ธรรมดา

---

## 📚 เอกสารเพิ่มเติม

- [Airflow Variables Documentation](https://airflow.apache.org/docs/apache-airflow/stable/concepts/variables.html)
- [Airflow Security Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/security/index.html)

---

**Updated:** November 22, 2025
**DAG:** `marketplace_scraper_with_details`
