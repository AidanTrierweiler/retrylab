import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");

  const [jobType, setJobType] = useState("send-email");
  const [mode, setMode] = useState("random"); // random | success | fail | fail_times
  const [failTimes, setFailTimes] = useState(2);
  const [maxAttempts, setMaxAttempts] = useState(3);

  const payload = useMemo(() => {
    if (mode === "success") return { force: "success" };
    if (mode === "fail") return { force: "fail" };
    if (mode === "fail_times") return { fail_times: Number(failTimes) };
    return {};
  }, [mode, failTimes]);

  async function refreshJobs() {
    try {
      const data = await apiGet("/jobs");
      setJobs(data);
      setError("");
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  async function createJob() {
    try {
      await apiPost("/jobs", {
        type: jobType,
        payload,
        max_attempts: Number(maxAttempts),
      });
      await refreshJobs();
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  useEffect(() => {
    refreshJobs();
    const id = setInterval(refreshJobs, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 900 }}>
      <h1>RetryLab</h1>
      <p>Create jobs and watch statuses update (QUEUED → RUNNING → SUCCEEDED/FAILED).</p>

      {error && (
        <div style={{ background: "#ffe6e6", padding: 12, borderRadius: 8, marginBottom: 12 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "end", marginBottom: 18 }}>
        <div>
          <label>Job type</label>
          <br />
          <input value={jobType} onChange={(e) => setJobType(e.target.value)} style={{ padding: 8, width: 180 }} />
        </div>

        <div>
          <label>Outcome mode</label>
          <br />
          <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ padding: 8 }}>
            <option value="random">random (80% success)</option>
            <option value="success">force success</option>
            <option value="fail">force fail</option>
            <option value="fail_times">fail N times then succeed</option>
          </select>
        </div>

        {mode === "fail_times" && (
          <div>
            <label>Fail times (N)</label>
            <br />
            <input
              type="number"
              value={failTimes}
              min={0}
              max={10}
              onChange={(e) => setFailTimes(e.target.value)}
              style={{ padding: 8, width: 120 }}
            />
          </div>
        )}

        <div>
          <label>Max attempts</label>
          <br />
          <input
            type="number"
            value={maxAttempts}
            min={1}
            max={10}
            onChange={(e) => setMaxAttempts(e.target.value)}
            style={{ padding: 8, width: 120 }}
          />
        </div>

        <button onClick={createJob} style={{ padding: "10px 14px", cursor: "pointer" }}>
          Create Job
        </button>

        <button onClick={refreshJobs} style={{ padding: "10px 14px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <h2>Jobs</h2>
      <table width="100%" cellPadding="8" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
            <th>ID</th>
            <th>Type</th>
            <th>Status</th>
            <th>Attempts</th>
            <th>Max</th>
            <th>Last Error</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((j) => (
            <tr key={j.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{j.id}</td>
              <td>{j.type}</td>
              <td>{j.status}</td>
              <td>{j.attempts}</td>
              <td>{j.max_attempts}</td>
              <td style={{ fontFamily: "monospace", fontSize: 12 }}>{j.last_error || ""}</td>
            </tr>
          ))}
          {jobs.length === 0 && (
            <tr>
              <td colSpan="6" style={{ padding: 12, color: "#666" }}>
                No jobs yet — create one above.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
