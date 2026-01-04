# Compliance Automation Tool

A comprehensive compliance automation system featuring AML (Anti-Money Laundering) and KYC (Know Your Customer) capabilities with document processing, facial recognition, and risk assessment.

## Table of Contents
- [Prerequisites (System Dependencies)](#prerequisites-system-dependencies)
- [Installation Steps](#installation-steps)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing AML Features](#testing-aml-features)
- [Testing KYC Features](#testing-kyc-features)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites (System Dependencies)

Before installing the application, ensure you have the following system dependencies installed:

### 1. Python 3.8 or higher
```bash
python --version  # Should be 3.8+
```

### 2. Tesseract OCR
Tesseract is required for document text extraction.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
- Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your system PATH

**Verify installation:**
```bash
tesseract --version
```

### 3. CMake
CMake is required for building dlib.

**Ubuntu/Debian:**
```bash
sudo apt-get install cmake
```

**macOS:**
```bash
brew install cmake
```

**Windows:**
- Download from: https://cmake.org/download/
- Or use: `pip install cmake`

### 4. dlib Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

**macOS:**
```bash
brew install openblas
brew install lapack
```

### 5. PostgreSQL (Recommended) or SQLite
**PostgreSQL (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install libpq-dev
```

**PostgreSQL (macOS):**
```bash
brew install postgresql
```

---

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/Sanavi05/compliance-automation-tool.git
cd compliance-automation-tool
git checkout aml-model-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If you encounter issues installing dlib:**
```bash
# Try installing dlib separately first
pip install dlib

# If that fails, install with specific flags:
pip install dlib --verbose
```

### 4. Create Required Directories
```bash
mkdir -p uploads/documents
mkdir -p uploads/photos
mkdir -p logs
```

### 5. Set Up Environment Variables
Create a `.env` file in the root directory:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database Configuration
# For SQLite (Development):
DATABASE_URL=sqlite:///compliance.db

# For PostgreSQL (Production):
# DATABASE_URL=postgresql://username:password@localhost:5432/compliance_db

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size

# Tesseract Configuration (if not in PATH)
# TESSERACT_CMD=/usr/bin/tesseract  # Linux/macOS
# TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows

# Application Configuration
DEBUG=True
PORT=5000
HOST=0.0.0.0
```

**Important:** Generate secure secret keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Setup

### 1. Initialize the Database
```bash
# Initialize Flask app and create tables
flask db init  # If using Flask-Migrate

# Or run the initialization script
python init_db.py
```

### 2. Run Database Migrations
```bash
# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 3. Verify Database Setup
```bash
# For SQLite:
sqlite3 compliance.db ".tables"

# For PostgreSQL:
psql -U username -d compliance_db -c "\dt"
```

### 4. Seed Initial Data (Optional)
```bash
python seed_data.py
```

---

## Running the Application

### 1. Start the Application
```bash
# Development mode
python app.py

# Or using Flask CLI
flask run

# Production mode (using gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. Access the Application
- Application URL: `http://localhost:5000`
- API Base URL: `http://localhost:5000/api`

### 3. Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T09:19:25Z"
}
```

---

## Testing AML Features

### 1. User Registration and Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Login to get JWT token:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Save the returned `access_token` for subsequent requests.

### 2. AML Transaction Screening

**Screen a single transaction:**
```bash
curl -X POST http://localhost:5000/api/aml/screen \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST12345",
    "transaction_amount": 15000.00,
    "transaction_type": "wire_transfer",
    "country": "US",
    "currency": "USD",
    "sender_name": "John Doe",
    "receiver_name": "Jane Smith"
  }'
```

**Expected response:**
```json
{
  "transaction_id": "TXN-1234567890",
  "risk_score": 0.65,
  "risk_level": "MEDIUM",
  "flags": ["high_amount", "international_transfer"],
  "requires_review": true,
  "recommendations": ["Verify source of funds", "Enhanced due diligence recommended"]
}
```

### 3. Batch Transaction Screening

**Screen multiple transactions:**
```bash
curl -X POST http://localhost:5000/api/aml/screen/batch \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "customer_id": "CUST001",
        "transaction_amount": 5000.00,
        "transaction_type": "deposit",
        "country": "US"
      },
      {
        "customer_id": "CUST002",
        "transaction_amount": 25000.00,
        "transaction_type": "wire_transfer",
        "country": "CN"
      }
    ]
  }'
```

### 4. Risk Assessment Queries

**Get customer risk profile:**
```bash
curl -X GET "http://localhost:5000/api/aml/customer/CUST12345/risk" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Get transaction history:**
```bash
curl -X GET "http://localhost:5000/api/aml/transactions?customer_id=CUST12345&limit=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Watchlist and Sanctions Screening

**Check against watchlists:**
```bash
curl -X POST http://localhost:5000/api/aml/watchlist/check \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1980-01-15",
    "country": "US"
  }'
```

---

## Testing KYC Features

### 1. Document Upload and Verification

**Upload identity document:**
```bash
curl -X POST http://localhost:5000/api/kyc/document/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "document=@/path/to/passport.jpg" \
  -F "document_type=passport" \
  -F "customer_id=CUST12345"
```

**Expected response:**
```json
{
  "document_id": "DOC-1234567890",
  "status": "processing",
  "extracted_data": {
    "document_type": "passport",
    "document_number": "AB1234567",
    "full_name": "JOHN DOE",
    "date_of_birth": "1980-01-15",
    "expiry_date": "2030-01-15",
    "nationality": "US"
  },
  "confidence_score": 0.95
}
```

### 2. Facial Recognition and Liveness Detection

**Upload selfie for verification:**
```bash
curl -X POST http://localhost:5000/api/kyc/face/verify \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "photo=@/path/to/selfie.jpg" \
  -F "document_id=DOC-1234567890" \
  -F "customer_id=CUST12345"
```

**Expected response:**
```json
{
  "verification_id": "VERIFY-1234567890",
  "face_match": true,
  "match_confidence": 0.92,
  "liveness_score": 0.88,
  "liveness_passed": true,
  "status": "verified"
}
```

### 3. Complete KYC Submission

**Submit complete KYC application:**
```bash
curl -X POST http://localhost:5000/api/kyc/submit \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST12345",
    "personal_info": {
      "full_name": "John Doe",
      "date_of_birth": "1980-01-15",
      "nationality": "US",
      "address": "123 Main St, New York, NY 10001"
    },
    "document_id": "DOC-1234567890",
    "verification_id": "VERIFY-1234567890"
  }'
```

### 4. KYC Status Check

**Check KYC verification status:**
```bash
curl -X GET "http://localhost:5000/api/kyc/status/CUST12345" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected response:**
```json
{
  "customer_id": "CUST12345",
  "kyc_status": "approved",
  "verification_level": "enhanced",
  "completed_at": "2026-01-04T09:19:25Z",
  "documents_verified": true,
  "face_verified": true,
  "risk_level": "LOW"
}
```

### 5. Document Text Extraction Test

**Test OCR capabilities:**
```bash
curl -X POST http://localhost:5000/api/kyc/document/extract \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "document=@/path/to/document.jpg"
```

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout user |

### AML Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/aml/screen` | Screen single transaction |
| POST | `/api/aml/screen/batch` | Screen multiple transactions |
| GET | `/api/aml/customer/{id}/risk` | Get customer risk profile |
| GET | `/api/aml/transactions` | Get transaction history |
| POST | `/api/aml/watchlist/check` | Check against watchlists |
| GET | `/api/aml/reports/suspicious` | Get suspicious activity reports |

### KYC Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/kyc/document/upload` | Upload identity document |
| POST | `/api/kyc/document/extract` | Extract text from document |
| POST | `/api/kyc/face/verify` | Verify face against document |
| POST | `/api/kyc/submit` | Submit complete KYC application |
| GET | `/api/kyc/status/{customer_id}` | Check KYC status |
| GET | `/api/kyc/documents/{customer_id}` | Get customer documents |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/statistics` | Get system statistics |
| POST | `/api/admin/customer/{id}/approve` | Approve KYC application |
| POST | `/api/admin/customer/{id}/reject` | Reject KYC application |

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Tesseract Not Found Error
**Error:** `TesseractNotFoundError: tesseract is not installed`

**Solution:**
```bash
# Verify Tesseract installation
tesseract --version

# Set Tesseract path in .env file
TESSERACT_CMD=/usr/bin/tesseract  # Linux/macOS
# or
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows
```

#### 2. dlib Installation Fails
**Error:** `Failed building wheel for dlib`

**Solution:**
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev

# Then install dlib
pip install dlib --verbose

# Alternative: Install from conda
conda install -c conda-forge dlib
```

#### 3. Database Connection Error
**Error:** `OperationalError: unable to open database file`

**Solution:**
```bash
# Ensure directory permissions
chmod 755 .
mkdir -p instance
chmod 755 instance

# Verify DATABASE_URL in .env
# For SQLite:
DATABASE_URL=sqlite:///compliance.db

# For PostgreSQL, check credentials:
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

#### 4. File Upload Error
**Error:** `413 Request Entity Too Large`

**Solution:**
```bash
# Increase MAX_CONTENT_LENGTH in .env
MAX_CONTENT_LENGTH=16777216  # 16MB

# For larger files, adjust accordingly
MAX_CONTENT_LENGTH=52428800  # 50MB
```

#### 5. JWT Token Expired
**Error:** `401 Unauthorized: Token has expired`

**Solution:**
```bash
# Request new token using refresh endpoint
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"

# Or login again
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

#### 6. Face Detection Fails
**Error:** `No faces detected in image`

**Solution:**
- Ensure good lighting in photos
- Face should be clearly visible and front-facing
- Image resolution should be at least 640x480
- Try with different photo formats (JPG, PNG)

#### 7. OCR Extraction Poor Quality
**Issue:** Low accuracy in text extraction

**Solution:**
```bash
# Ensure high-quality document images
# - Resolution: 300 DPI or higher
# - Format: PNG or high-quality JPG
# - Lighting: Even, no shadows or glare

# Install additional Tesseract language packs
sudo apt-get install tesseract-ocr-eng  # English
sudo apt-get install tesseract-ocr-all  # All languages
```

#### 8. Permission Denied on Uploads Directory
**Error:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Set proper permissions
chmod -R 755 uploads
chown -R $USER:$USER uploads

# Verify directory exists
mkdir -p uploads/documents uploads/photos
```

#### 9. Port Already in Use
**Error:** `OSError: [Errno 98] Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000
# or
netstat -tuln | grep 5000

# Kill the process
kill -9 PID

# Or use a different port
flask run --port 5001
```

#### 10. Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify Python version
python --version  # Should be 3.8+
```

### Debug Mode

To enable detailed error logging:

```bash
# Set in .env file
DEBUG=True
FLASK_ENV=development

# View logs
tail -f logs/app.log
```

### Getting Help

- **GitHub Issues:** https://github.com/Sanavi05/compliance-automation-tool/issues
- **Documentation:** Check the `/docs` folder for detailed API documentation
- **Logs:** Check application logs in the `logs/` directory

### Performance Optimization

For better performance in production:

```bash
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:pass@localhost:5432/compliance_db

# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# Enable caching
pip install flask-caching redis

# Optimize image processing
pip install pillow-simd
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Acknowledgments

- Tesseract OCR for document text extraction
- dlib for facial recognition capabilities
- Flask framework for API development

---

**Last Updated:** 2026-01-04

For questions or support, please open an issue on GitHub.
