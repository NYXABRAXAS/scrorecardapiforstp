# Configurable Two Wheeler Loan STP Scorecard API

Production-shaped FastAPI service for bank LOS scorecard integration. It calculates score, evaluates DB-configured business rules, routes cases to STP / Conditional STP / Non-STP / Reject, and returns explainable reason codes.

## Run Locally

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
python -m app.db.init_db
uvicorn app.main:app --reload
```

Swagger UI: `http://localhost:8000/docs`

Business console: `http://localhost:8000/`

## Docker

```powershell
docker compose up --build
```

## Main APIs

- `POST /generate-scorecard`
- `POST /simulate-scorecard`
- `GET /scorecard/{lead_id}`
- `GET /rules`
- `POST /rules`
- `PUT /rules/{id}`
- `PATCH /rules/{id}/status`
- `GET /health`

## Rule Model

Rules are structured records, not code. Business teams can update thresholds, scores, eligibility checks, and underwriting triggers through APIs.

Supported operators: `>`, `>=`, `<`, `<=`, `=`, `!=`, `BETWEEN`, `IN`, `NOT_IN`.

Rule types:

- `SCORE`
- `HARD_REJECT`
- `NON_STP`
- `STP_ELIGIBILITY`

The HTML console lets users edit rules product-wise for two wheeler, new/used car, new/used commercial vehicle, and new/used tractor scorecards.

## Example Request

```json
{
  "tenantId": "default",
  "productType": "TWO_WHEELER_LOAN",
  "application": {
    "leadId": "TW10001",
    "customerName": "ABC",
    "mobile": "9999999999",
    "employmentType": "SALARIED",
    "monthlyIncome": 45000,
    "existingEMI": 8000,
    "foir": 32,
    "loanAmount": 95000,
    "assetCost": 125000,
    "ltv": 76,
    "tenure": 36,
    "dealerId": "DL101",
    "state": "Karnataka",
    "city": "Bangalore",
    "negativeArea": false,
    "faceMatchScore": 92,
    "panVerified": true,
    "aadhaarVerified": true,
    "bankingSurrogate": true,
    "coApplicant": false
  },
  "bureau": {
    "cibilScore": 753,
    "creditVintageMonths": 123,
    "activeAccounts": 2,
    "closedAccounts": 47,
    "overdueAmount": 0,
    "writtenOffAccounts": 0,
    "settledAccounts": 0,
    "maxDPD": 0,
    "dpd30Count": 0,
    "dpd60Count": 0,
    "dpd90Count": 0,
    "creditEnquiries6M": 2,
    "creditEnquiries12M": 4,
    "activeUnsecuredLoans": 1,
    "activeSecuredLoans": 1,
    "jointAccounts": 0,
    "creditUtilization": 2
  }
}
```
