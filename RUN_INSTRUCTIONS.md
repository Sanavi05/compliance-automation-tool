# Running the Compliance Automation Tool

## Quick Start

1. **Activate Virtual Environment** (if using one):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Start the Server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the Application**:
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Features Fixed

✅ **Project Running Issues Fixed**:
- Fixed werkzeug import (replaced with FastAPI-compatible solution)
- Fixed database configuration (SQLite support added)
- Made face_recognition optional (app runs without it)
- Fixed Unicode issues in database creation script
- Added missing dependencies

✅ **KYC Logic Issues Fixed**:
- Fixed verification trigger logic in `/api/kyc/verify` endpoint
- Improved error handling in KYC service

✅ **Frontend Added**:
- Complete KYC verification portal
- Document upload interface (Photo, Aadhaar, PAN)
- Real-time status updates
- Authentication system
- Responsive design

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### KYC
- `POST /api/kyc/upload` - Upload KYC document
- `GET /api/kyc/status` - Get KYC verification status
- `GET /api/kyc/documents` - List all uploaded documents
- `POST /api/kyc/verify` - Trigger full verification
- `POST /api/kyc/resubmit/{document_id}` - Resubmit rejected document

## Usage

1. **Login**: Use any User ID and password (for development)
2. **Upload Documents**: Upload Photo, Aadhaar, and PAN card
3. **Check Status**: View verification status in real-time
4. **Trigger Verification**: Once all documents are verified, trigger full verification

## Notes

- The app uses SQLite by default (configured in database.py)
- For PostgreSQL, set `DATABASE_URL` in `.env` file
- Face recognition requires `dlib` and `face_recognition` libraries (optional)
- OCR requires Tesseract OCR to be installed
