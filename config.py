import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# KYC Configuration
KYC_UPLOAD_FOLDER = 'uploads/kyc'
KYC_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
KYC_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# OCR Configuration
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

# Face Recognition Configuration
FACE_MATCH_THRESHOLD = 0.6

# Validation thresholds
AADHAAR_VALIDATION_THRESHOLD = 75.0
PAN_VALIDATION_THRESHOLD = 75.0
NAME_SIMILARITY_THRESHOLD = 0.8
