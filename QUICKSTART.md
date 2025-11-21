# Quick Start Guide - Airflow + MinIO

## 🚀 เริ่มต้นใช้งาน (Quick Start)

### สำหรับ Windows:

1. **เปิด Command Prompt หรือ PowerShell:**
   ```cmd
   cd e:\01\dowload\34\airflow-minio-project
   ```cd

2. **เริ่มต้น services:**
   ```cmd
   scripts\start.bat
   ```

3. **เข้าใช้งาน:**
   - Airflow: http://localhost:8080 (airflow/airflow)
   - MinIO: http://localhost:9001 (minioadmin/minioadmin)

4. **หยุด services:**
   ```cmd
   scripts\stop.bat
   ```

### สำหรับ Linux/Mac:

1. **เปิด Terminal:**
   ```bash
   cd /path/to/airflow-minio-project
   ```

2. **เริ่มต้น services:**
   ```bash
   chmod +x scripts/start.sh
   ./scripts/start.sh
   ```

3. **หยุด services:**
   ```bash
   docker-compose down
   ```

## 📊 ทดสอบ DAG แรก

1. เข้า Airflow UI: http://localhost:8080
2. เปิด DAG `minio_upload_example`
3. คลิก "Trigger DAG" (ปุ่ม ▶️)
4. ดูผลลัพธ์ใน Graph หรือ Logs
5. ตรวจสอบไฟล์ใน MinIO: http://localhost:9001

## 🔧 คำสั่งที่ใช้บ่อย

```bash
# ดูสถานะ services
docker-compose ps

# ดู logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f minio

# Restart services
docker-compose restart

# หยุดและลบทุกอย่าง (รวม data!)
docker-compose down -v
```

## 📁 สร้าง DAG ใหม่

1. สร้างไฟล์ Python ใน `dags/`
2. รอ 30 วินาที (Airflow จะ scan อัตโนมัติ)
3. Refresh Airflow UI

## ⚠️ แก้ปัญหาเบื้องต้น

**ปัญหา: Port ถูกใช้แล้ว**
```bash
# หา process ที่ใช้ port
netstat -ano | findstr :8080
netstat -ano | findstr :9000

# หยุด process หรือเปลี่ยน port ใน docker-compose.yml
```

**ปัญหา: DAG ไม่ปรากฏ**
- เช็คว่าไฟล์อยู่ใน `dags/` folder
- ดู logs: `docker-compose logs airflow-scheduler`
- เช็ค syntax error ในไฟล์ DAG

**ปัญหา: MinIO connection ไม่ทำงาน**
- ตรวจสอบ Connection ใน Airflow Admin > Connections
- Conn Id: `minio_default`
- Extra: `{"endpoint_url": "http://minio:9000"}`

## 📚 เอกสารเพิ่มเติม

ดูใน `README.md` สำหรับข้อมูลเพิ่มเติม
