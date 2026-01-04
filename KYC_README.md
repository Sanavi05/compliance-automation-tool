# KYC Automation Module

This module provides automated Know Your Customer (KYC) verification capabilities for the Compliance Automation Tool.

## Features

- **Document Upload & Processing**: Support for Photo, Aadhaar Card, and PAN Card
- **OCR Extraction**: Automated data extraction from documents using Tesseract OCR
- **Document Validation**: 
  - Aadhaar validation with Verhoeff checksum algorithm
  - PAN card format and structure validation
- **Face Matching**: Compare uploaded photo with document photo
- **Cross-Validation**: Verify consistency of information across documents
- **JWT Authentication**: Secure API endpoints with JWT tokens
- **Complete Verification Workflow**: Track KYC status from upload to completion

## Architecture

### Database Models

#### KYCDocument
Stores information about uploaded documents:
- Document metadata (file path, size, type)
- Extracted data from OCR
- Verification status and scores
- Upload and verification timestamps

#### KYCVerification
Tracks overall KYC verification status:
- Per-document verification flags (photo, Aadhaar, PAN)
- Face matching results
- Cross-validation results
- Risk assessment
- Completion status

### OCR Processors

#### AadhaarOCR (`utils/ocr_processors/aadhaar_ocr.py`)
- Preprocesses image (grayscale, thresholding, denoising)
- Extracts: Aadhaar number, name, DOB, gender
- Uses Tesseract with English + Hindi language support

#### PANOCR (`utils/ocr_processors/pan_ocr.py`)
- Preprocesses PAN card image
- Extracts: PAN number, name, father's name, DOB
- Uses Tesseract with English language support

#### FaceDetector (`utils/ocr_processors/face_detector.py`)
- Detects faces using Haar Cascade
- Extracts face encodings using face_recognition library
- Compares faces with configurable tolerance (default: 0.6)

### Validators

#### AadhaarValidator (`utils/validators/aadhaar_validator.py`)
- Format validation (12 digits)
- Verhoeff checksum algorithm implementation
- Name validation (3+ characters, letters only)
- DOB validation (0-120 years age range)
- Complete document scoring (threshold: 75%)

#### PANValidator (`utils/validators/pan_validator.py`)
- Format validation ([A-Z]{5}[0-9]{4}[A-Z])
- Structure validation (4th character holder type)
- Name and DOB validation
- Complete document scoring (threshold: 75%)

### Service Layer

#### KYCService (`kyc_service.py`)
Orchestrates the entire KYC workflow:
- Document processing and OCR
- Validation of extracted data
- Cross-validation across documents (name matching with 80% threshold)
- Face matching between photo and Aadhaar
- KYC status updates

## API Endpoints

All endpoints require JWT authentication via Bearer token.

### POST /api/kyc/upload
Upload and process a KYC document.

**Request:**
- `file`: Document file (multipart/form-data)
- `document_type`: One of 'photo', 'aadhaar', 'pan'

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "document_type": "aadhaar",
    "verification_status": "verified",
    "extracted_data": {...},
    "validation_score": 100.0,
    ...
  }
}
```

### GET /api/kyc/status
Get current KYC verification status for authenticated user.

**Response:**
```json
{
  "success": true,
  "verification": {
    "kyc_status": "completed",
    "kyc_level": "full",
    "photo_verified": true,
    "aadhaar_verified": true,
    "pan_verified": true,
    "face_match_verified": true,
    "cross_validation_result": {...}
  },
  "documents": [...]
}
```

### GET /api/kyc/documents
List all uploaded documents for authenticated user.

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "id": 1,
      "document_type": "photo",
      "verification_status": "verified",
      ...
    }
  ]
}
```

### POST /api/kyc/verify
Manually trigger full verification process.

**Requirements:**
- All three documents (photo, Aadhaar, PAN) must be uploaded and verified

**Response:**
```json
{
  "message": "Verification process completed",
  "status": {...}
}
```

### POST /api/kyc/resubmit/{document_id}
Resubmit a rejected or failed document.

**Request:**
- `document_id`: ID of document to replace (path parameter)
- `file`: New document file (multipart/form-data)

## Configuration

Configuration options in `config.py`:

```python
# KYC Configuration
KYC_UPLOAD_FOLDER = 'uploads/kyc'
KYC_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
KYC_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# OCR Configuration
TESSERACT_PATH = '/usr/bin/tesseract'

# Face Recognition Configuration
FACE_MATCH_THRESHOLD = 0.6

# Validation thresholds
AADHAAR_VALIDATION_THRESHOLD = 75.0
PAN_VALIDATION_THRESHOLD = 75.0
NAME_SIMILARITY_THRESHOLD = 0.8
```

## Installation

### Prerequisites

1. **Tesseract OCR**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin
   
   # macOS
   brew install tesseract tesseract-lang
   ```

2. **CMake and dlib dependencies** (for face_recognition)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install cmake libboost-all-dev
   
   # macOS
   brew install cmake boost
   ```

### Python Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- pytesseract==0.3.10
- Pillow==10.0.0
- opencv-python==4.8.0.74
- face-recognition==1.3.0
- dlib==19.24.0
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4

## Database Setup

Run the migration script to create KYC tables:

```bash
python create_kyc_tables.py
```

This creates:
- `kyc_documents` table
- `kyc_verifications` table

## Authentication

The module uses JWT (JSON Web Tokens) for authentication. To use the API:

1. Obtain a JWT token from your authentication system
2. Include the token in requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

The token should include a `sub` claim with the user ID.

## Usage Example

```python
import requests

# Authenticate and get token
token = "your-jwt-token"
headers = {"Authorization": f"Bearer {token}"}

# Upload Aadhaar card
with open('aadhaar.jpg', 'rb') as f:
    files = {'file': f}
    data = {'document_type': 'aadhaar'}
    response = requests.post(
        'http://localhost:8000/api/kyc/upload',
        headers=headers,
        files=files,
        data=data
    )
    print(response.json())

# Check KYC status
response = requests.get(
    'http://localhost:8000/api/kyc/status',
    headers=headers
)
print(response.json())
```

## File Storage

Documents are stored in the following structure:
```
uploads/kyc/
  ├── user123/
  │   ├── photo_20240101_120000_image.jpg
  │   ├── aadhaar_20240101_120500_scan.jpg
  │   └── pan_20240101_121000_card.jpg
  └── user456/
      └── ...
```

Files are named: `{document_type}_{timestamp}_{original_filename}`

## Error Handling

The module provides comprehensive error handling:

- **400 Bad Request**: Invalid file type, missing parameters
- **401 Unauthorized**: Invalid or missing JWT token
- **404 Not Found**: Document or resource not found
- **500 Internal Server Error**: Processing or server errors

Error responses include descriptive messages:
```json
{
  "detail": "Invalid document type. Must be 'photo', 'aadhaar', or 'pan'"
}
```

## Security Considerations

1. **JWT Authentication**: All endpoints require valid JWT tokens
2. **File Validation**: File types and sizes are strictly validated
3. **Secure Storage**: Files stored in user-specific directories
4. **Data Privacy**: Sensitive document data stored encrypted in database
5. **No Security Vulnerabilities**: Passed CodeQL security analysis

## Validation Rules

### Aadhaar Card
- Must be 12 digits
- Must pass Verhoeff checksum validation
- Name: minimum 3 characters, letters only
- DOB: valid date, age 0-120 years
- Gender: Male or Female

### PAN Card
- Format: [A-Z]{5}[0-9]{4}[A-Z]
- 4th character must be valid holder type (P, C, H, F, A, T, B, L, J, G)
- Name: minimum 3 characters, letters only
- DOB: valid date, age 18-120 years

### Cross-Validation
- Name matching: 80% similarity threshold using SequenceMatcher
- DOB matching: Exact match required

### Face Matching
- Tolerance: 0.6 (configurable)
- Compares photo with Aadhaar card photo

## Troubleshooting

### Tesseract not found
```
Error: TesseractNotFoundError
```
**Solution**: Install Tesseract OCR and set `TESSERACT_PATH` in config.py

### Face recognition installation fails
```
Error: dlib installation failed
```
**Solution**: Install cmake and boost libraries first

### Low OCR confidence
**Solution**: 
- Ensure images are clear and high quality
- Images should be well-lit and not blurry
- Text should be horizontal and not skewed

### Face matching fails
**Solution**:
- Photo should have clear, front-facing face
- Good lighting conditions
- No obstructions (sunglasses, masks)

## Testing

Run validator tests:
```bash
python -m pytest tests/test_validators.py
```

Test OCR processors (requires sample documents):
```bash
python -m pytest tests/test_ocr.py
```

## Future Enhancements

- [ ] Support for additional document types (Driver's License, Passport)
- [ ] Integration with government verification APIs
- [ ] Liveness detection for photos
- [ ] Multi-language support for more Indian languages
- [ ] Batch processing for multiple users
- [ ] Analytics dashboard for KYC statistics
- [ ] Webhook notifications for status changes

## License

This module is part of the Compliance Automation Tool project.
