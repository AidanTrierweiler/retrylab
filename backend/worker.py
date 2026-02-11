import random
import time
import json
from datetime import datetime

from sqlalchemy.orm import Session

from db import SessionLocal
from models import Job

def process_job(job: Job) -> tuple[bool, str | None]:
    """
    Deterministic controls (for QA/testing) via payload:
      payload.force = "success" | "fail"
      payload.fail_times = int  (fail this many attempts, then succeed)
    Otherwise, default is 80% success probability.
    """
    try:
        payload = json.loads(job.payload)
    except Exception:
        payload = {}

    force = payload.get("force")
    if force == "success":
        return True, None
    if force == "fail":
        return False, "Forced failure"

    fail_times = payload.get("fail_times")
    if isinstance(fail_times, int) and fail_times >= 0:
        # If attempts so far are less than fail_times, fail; otherwise succeed
        if job.attempts < fail_times:
            return False, f"Planned failure {job.attempts + 1}/{fail_times}"
        return True, None

    # Default random mode (good for manual exploration)
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
