import json
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from models import Job
from schemas import JobCreate, JobOut
import threading
from worker import run_worker

app = FastAPI()

# Create DB tables at startup (fine for this learning project)
Base.metadata.create_all(bind=engine)

def start_worker():
    t = threading.Thread(target=run_worker, daemon=True)
    t.start()

start_worker()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/jobs", response_model=JobOut, status_code=201)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    job = Job(
        type=job_in.type,
        payload=json.dumps(job_in.payload),
        status="QUEUED",
        attempts=0,
        max_attempts=job_in.max_attempts,
        last_error=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobOut(
        id=job.id,
        type=job.type,
        payload=json.loads(job.payload),
        status=job.status,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        last_error=job.last_error,
    )

@app.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.id.desc()).all()
    return [
        JobOut(
            id=j.id,
            type=j.type,
            payload=json.loads(j.payload),
            status=j.status,
            attempts=j.attempts,
            max_attempts=j.max_attempts,
            last_error=j.last_error,
        )
        for j in jobs
    ]

@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobOut(
        id=job.id,
        type=job.type,
        payload=json.loads(job.payload),
        status=job.status,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        last_error=job.last_error,
    )
