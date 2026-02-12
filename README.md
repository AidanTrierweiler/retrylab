# RetryLab — Full-Stack Job Processing & QA Automation System

RetryLab is a mini full-stack system designed to simulate infrastructure job processing and demonstrate Quality Engineering automation practices.

It models how background services process tasks, handle retries, and expose observability through APIs and dashboards.

---

## Architecture Overview

Frontend (React) → FastAPI Backend → SQLite DB → Worker Thread → Status Updates → UI Polling

---

## Tech Stack

**Frontend**

* React (Vite)
* Fetch API
* Live polling UI

**Backend**

* FastAPI
* SQLAlchemy
* Background worker thread

**Database**

* SQLite

**Testing**

* pytest
* Deterministic job outcomes
* API automation

---

## Core Features

### Job Processing

* Create jobs via API or UI
* Background worker processes tasks
* State transitions:

  * QUEUED → RUNNING → SUCCEEDED / FAILED

### Retry Logic

* Configurable max attempts
* Automatic retries on failure
* Terminal failure handling

### Deterministic Testing Controls

Payload flags allow deterministic execution:

```
{ "force": "success" }
{ "force": "fail" }
{ "fail_times": 2 }
```

This prevents flaky automation tests.

---

## Automated Tests

pytest suite validates:

* Job creation
* Retry behavior
* Terminal state transitions
* Deterministic failure scenarios

Run tests:

```
cd backend
pytest -q
```

---

## Running Locally

### Backend

```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```
cd frontend
npm install
npm run dev
```

Open:

```
http://localhost:5173
```

---

## Learning Goals

This project demonstrates:

* End-to-end request flow
* Background processing
* Retry/failure modeling
* API automation
* Deterministic test design
* Observability dashboards

---

## Future Enhancements

* Redis queue backend
* Separate worker service
* Dead-letter queue
* Retry UI controls
* Load testing
* CI pipeline

---

## Author

Aidan Trierweiler
