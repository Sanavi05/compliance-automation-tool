# AML Model API

A FastAPI-based Anti-Money Laundering (AML) detection system that provides RESTful API endpoints for monitoring transactions, analyzing risk levels, and managing alerts.

## Features

- **Dashboard Summary**: Get overview statistics of transactions and alerts
- **Risk Distribution**: View distribution of transactions by risk level
- **Transaction Filtering**: Filter transactions by risk level (LOW, MEDIUM, HIGH, CRITICAL)
- **Transaction Details**: Get detailed information about specific transactions
- **User Risk Profiles**: View risk profiles for individual users
- **Alert Management**: View and manage AML alerts

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **ORM**: SQLAlchemy
- **Server**: Uvicorn
- **Environment**: python-dotenv

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Sanavi05/compliance-automation-tool.git
cd compliance-automation-tool
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv env
env\Scripts\activate

# On macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory of the project with the following content:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Example:
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/aml_db
```

**Important Notes:**
- Replace `username` with your PostgreSQL username
- Replace `password` with your PostgreSQL password
- Replace `localhost:5432` with your database host and port (if different)
- Replace `dbname` with your actual database name
- Do NOT commit the `.env` file to version control (it's already in `.gitignore`)

### 5. Database Setup

Make sure PostgreSQL is running and create a database:


Then, ensure your database tables are created on neon website . You may need to run migrations or create the tables manually based on the models defined in `models.py`.

## Running the Application

### Development Mode

```bash
# Make sure your virtual environment is activated
# On Windows
env\Scripts\activate

# On macOS/Linux
source env/bin/activate

# Run the FastAPI server with auto-reload
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative API Docs (ReDoc)**: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy"
}
```

### Dashboard Summary
```
GET /dashboard/summary
```
Returns summary statistics including total transactions today, high-risk transactions, critical alerts, and users under monitoring.

### Risk Distribution
```
GET /dashboard/risk-distribution
```
Returns the distribution of transactions by risk level.

**Response:**
```json
[
  {
    "risk_label": "LOW",
    "count": 150
  },
  {
    "risk_label": "MEDIUM",
    "count": 75
  },
  {
    "risk_label": "HIGH",
    "count": 25
  },
  {
    "risk_label": "CRITICAL",
    "count": 5
  }
]
```

### Get Transactions by Risk Level
```
GET /dashboard/transactions?risk={risk}
```
Get transactions filtered by risk level.

**Parameters:**
- `risk` (query parameter, required): One of `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`

**Example:**
```
GET /dashboard/transactions?risk=HIGH
```

**Response:**
```json
[
  {
    "transaction_id": "T001",
    "user_id": "U001",
    "transaction_amount": 5000.00,
    "timestamp": "2024-01-01T12:00:00",
    "final_risk_score": 75.5,
    "risk_label": "HIGH",
    "alert_status": "OPEN"
  }
]
```

### Get Transaction Details
```
GET /transaction/{tx_id}
```
Get detailed information about a specific transaction.

**Parameters:**
- `tx_id` (path parameter): Transaction ID

**Example:**
```
GET /transaction/T001
```

### Get User Risk Profile
```
GET /user/{user_id}/risk-profile
```
Get risk profile information for a specific user.

**Parameters:**
- `user_id` (path parameter): User ID

**Example:**
```
GET /user/U001/risk-profile
```

### Get All Alerts
```
GET /alerts
```
Returns all AML alerts ordered by creation date (newest first).

### Close Alert
```
PUT /alerts/{alert_id}/close
```
Closes an alert by setting its status to "CLOSED".

**Parameters:**
- `alert_id` (path parameter): Alert ID

**Example:**
```
PUT /alerts/1/close
```

## Project Structure

```
AMLModel/
├── main.py                 # FastAPI application and routes
├── crud.py                 # Database CRUD operations
├── models.py               # SQLAlchemy database models
├── database.py             # Database connection and session management
├── schemas.py              # Pydantic schemas for request/response validation
├── aml_pipeline.py          # AML scoring pipeline
├── dataGeneration.py        # Data generation utilities
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this file)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Database Models

The application uses the following main models:

- **User**: User information and KYC status
- **Transaction**: Transaction details
- **AMLScore**: Risk scores and labels for transactions
- **AMLAlert**: Alerts generated for high-risk transactions

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Development

### Adding New Endpoints

1. Add the route handler in `main.py`
2. Add the corresponding CRUD function in `crud.py` if needed
3. Update this README with the new endpoint documentation

### Database Migrations

If you need to modify database models:

1. Update the models in `models.py`
2. Create a migration script or manually update the database schema
3. Test the changes thoroughly

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready` or check service status
- Check your `.env` file has the correct `DATABASE_URL`
- Ensure the database exists and credentials are correct
- Check firewall settings if connecting to a remote database

### Import Errors

- Make sure your virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python path and module imports

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn main:app --reload --port 8001
```







