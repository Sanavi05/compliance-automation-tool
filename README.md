# Compliance Automation Tool for FinTechs (KYC & AML)

**Project ID**:  FD005

A digital solution that automates parts of the compliance process for FinTech companies, making KYC (Know Your Customer) and AML (Anti-Money Laundering) verification faster, safer, and more efficient.

##  Overview

FinTech companies are required to follow strict regulations like Know Your Customer (KYC) and Anti-Money Laundering (AML), which can be time-consuming and costly when done manually. This tool automates key compliance processes including:

- **KYC Document Upload & Verification**:  Supports PAN, Aadhaar, driver's license
- **Basic Validation Checks**: Document type, expiry date, format validation
- **AML Rule Engine**: Flags suspicious patterns (large/unusual transfers, rapid movement of funds)
- **Compliance Dashboard**: Track verification and flagged cases

##  Tech Stack

### **Frontend**
- React.js
- Material-UI (MUI)
- Redux Toolkit / Context API
- React Hook Form + Yup
- Axios

### **Backend**
- Python 3.9+
- Flask
- Flask-CORS, Flask-JWT-Extended, Flask-SQLAlchemy
- Flask-Marshmallow, Flask-RESTful
- Celery + Redis (async processing)

### **Document Processing**
- pytesseract (OCR)
- Pillow (PIL)
- pdf2image
- OpenCV (cv2)
- python-magic

### **AML & Analytics**
- Pandas
- NumPy
- Scikit-learn

### **Database**
- PostgreSQL
- SQLAlchemy ORM
- Alembic (migrations)

### **Storage**
- AWS S3 (boto3)
- Local filesystem (development)

##  Project Structure

```
compliance-automation-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/                  # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── kyc_document.py
│   │   │   └── transaction.py
│   │   ├── routes/                  # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── kyc.py
│   │   │   └── aml.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── kyc_service.py
│   │   │   ├── aml_service.py
│   │   │   └── ocr_service.py
│   │   ├── utils/                   # Helper functions
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   └── document_processor.py
│   │   ├── tasks/                   # Celery tasks
│   │   │   ├── __init__.py
│   │   │   └── process_documents.py
│   │   └── config.py                # Configuration
│   ├── migrations/                  # Database migrations
│   ├── tests/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_kyc.py
│   │   └── test_aml.py
│   ├── uploads/                     # Temporary file storage
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py                       # Application entry point
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── KYCUpload/
│   │   │   ├── AMLMonitor/
│   │   │   └── Common/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── KYCVerification.jsx
│   │   │   └── AMLDashboard.jsx
│   │   ├── services/                # API calls
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── kycService.js
│   │   ├── utils/
│   │   │   └── validators.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

##  Getting Started

### Prerequisites

**Backend:**
- Python 3.9 or higher
- PostgreSQL 13+
- Redis (for Celery)
- Tesseract OCR

**Frontend:**
- Node.js 16+ and npm/yarn

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Sanavi05/compliance-automation-tool.git
cd compliance-automation-tool
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# On Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# On macOS: 
brew install tesseract

# On Windows:
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki

# Create .env file
cp .env.example .env
# Edit .env with your database credentials and configuration

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create uploads directory
mkdir -p uploads
```

#### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
# or
yarn install

# Create .env file
cp .env.example .env
# Edit .env with backend API URL
```

### Environment Variables

**Backend (.env):**
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/compliance_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-bucket-name
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:5000/api
```

##  Running the Application

### Development Mode

#### Start PostgreSQL & Redis

```bash
# Using Docker (recommended)
docker-compose up -d postgres redis

# Or start services manually
# PostgreSQL (system service)
sudo service postgresql start

# Redis
redis-server
```

#### Start Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Flask development server
python run.py
# Server will run on http://localhost:5000
```

#### Start Celery Worker (in a new terminal)

```bash
cd backend
source venv/bin/activate

# Start Celery worker
celery -A app.celery worker --loglevel=info
```

#### Start Frontend

```bash
cd frontend

# Start React development server
npm start
# or
yarn start

# Application will open on http://localhost:3000
```

### Production Mode

```bash
# Backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Frontend build
cd frontend
npm run build
# Serve the build folder with Nginx or similar
```

### Using Docker (Optional)

```bash
# Build and start all services
docker-compose up --build

# Stop all services
docker-compose down
```

##  Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_kyc.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test
# or
yarn test
```

##  API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:5000/api/docs`

### Key Endpoints

```
POST   /api/auth/register          - Register new user
POST   /api/auth/login             - Login user
POST   /api/kyc/upload             - Upload KYC document
GET    /api/kyc/documents          - List all KYC documents
GET    /api/kyc/documents/:id      - Get document details
POST   /api/kyc/verify/:id         - Verify document
POST   /api/aml/analyze            - Analyze transaction for AML
GET    /api/aml/flagged            - Get flagged cases
GET    /api/dashboard/stats        - Get dashboard statistics
```

##  Deployment

### Deploy Backend (Example:  Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy Frontend (Example: Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

##  Configuration

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Adding New Dependencies

**Backend:**
```bash
pip install package-name
pip freeze > requirements.txt
```

**Frontend:**
```bash
npm install package-name
# or
yarn add package-name
```

##  Features Roadmap

- [x] Basic project structure
- [ ] User authentication (JWT)
- [ ] KYC document upload
- [ ] OCR integration for document extraction
- [ ] Document validation (PAN, Aadhaar, Driver's License)
- [ ] AML rule engine
- [ ] Compliance dashboard
- [ ] Email notifications
- [ ] Audit logs
- [ ] Advanced ML-based fraud detection

##  Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Contact

**Sanavi05**
- GitHub: [@Sanavi05](https://github.com/Sanavi05)

For questions or feedback, please open an issue in this repository.

##  Acknowledgments

- Flask documentation
- React documentation
- Tesseract OCR
- Material-UI community

---

**Note**:  This is a development project for educational purposes. For production use, ensure proper security audits and compliance with local regulations.
