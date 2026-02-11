import random
import time
from datetime import datetime

from sqlalchemy.orm import Session

from db import SessionLocal
from models import Job

def process_job(job: Job) -> tuple[bool, str | None]:
    """
    Simulate doing work.
    Return (success, error_message).
    """
    # 80% success rate by default
    if random.random() < 0.8:
        return True, None
    return False, "Simulated failure"

def run_worker(poll_seconds: float = 1.0):
    print("[worker] started")
    while True:
        db: Session = SessionLocal()
        try:
            job = (
                db.query(Job)
                .filter(Job.status == "QUEUED")
                .order_by(Job.id.asc())
                .first()
            )

            if not job:
                time.sleep(poll_seconds)
                continue

            # Mark RUNNING
            job.status = "RUNNING"
            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)

            # Simulate work taking time
            time.sleep(0.5)

            success, err = process_job(job)

            if success:
                job.status = "SUCCEEDED"
                job.last_error = None
            else:
                job.attempts += 1
                job.last_error = err
                if job.attempts < job.max_attempts:
                    job.status = "QUEUED"   # retry later
                else:
                    job.status = "FAILED"   # give up

            job.updated_at = datetime.utcnow()
            db.commit()

        finally:
            db.close()

        time.sleep(poll_seconds)
