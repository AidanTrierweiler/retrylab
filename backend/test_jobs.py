import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

# IMPORTANT: set test DB name BEFORE importing app/db modules
os.environ["RETRYLAB_DB"] = "test_retrylab.db"

from main import app  # noqa: E402
from db import engine  # noqa: E402

client = TestClient(app)


def wait_for_terminal(job_id: int, timeout_s: float = 8.0):
    """
    Poll GET /jobs/{id} until the job reaches a terminal state.
    Terminal states: SUCCEEDED or FAILED
    """
    start = time.time()
    while time.time() - start < timeout_s:
        r = client.get(f"/jobs/{job_id}")
        assert r.status_code == 200
        job = r.json()
        if job["status"] in ("SUCCEEDED", "FAILED"):
            return job
        time.sleep(0.2)
    raise AssertionError(f"Job {job_id} did not reach terminal state in time")


@pytest.fixture(autouse=True)
def cleanup_jobs_table():
    """
    Clear the jobs table before/after each test.

    We do NOT delete the SQLite file on Windows because the process may keep it
    open, causing WinError 32 (file locked).
    """
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM jobs"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM jobs"))


def test_force_success():
    r = client.post(
        "/jobs",
        json={
            "type": "send-email",
            "payload": {"force": "success"},
            "max_attempts": 3,
        },
    )
    assert r.status_code == 201
    job_id = r.json()["id"]

    final = wait_for_terminal(job_id)
    assert final["status"] == "SUCCEEDED"
    assert final["attempts"] == 0


def test_fail_times_then_succeed():
    r = client.post(
        "/jobs",
        json={
            "type": "send-email",
            "payload": {"fail_times": 2},
            "max_attempts": 5,
        },
    )
    assert r.status_code == 201
    job_id = r.json()["id"]

    final = wait_for_terminal(job_id)
    assert final["status"] == "SUCCEEDED"
    assert final["attempts"] == 2


def test_force_fail_hits_max_attempts():
    r = client.post(
        "/jobs",
        json={
            "type": "send-email",
            "payload": {"force": "fail"},
            "max_attempts": 2,
        },
    )
    assert r.status_code == 201
    job_id = r.json()["id"]

    final = wait_for_terminal(job_id)
    assert final["status"] == "FAILED"
    assert final["attempts"] == 2
