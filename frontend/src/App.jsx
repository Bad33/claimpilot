import React, { useMemo, useState } from "react";

const API_BASE_DEFAULT = "http://localhost:8000";

const emptyClaimForm = {
  external_claim_id: "",
  claimant_name: "",
  incident_date: "",
  claim_type: "",
  claimed_amount: "",
  status: "new",
};

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f8fafc",
    padding: "24px",
    fontFamily: "Arial, sans-serif",
    color: "#0f172a",
  },
  container: {
    maxWidth: "1280px",
    margin: "0 auto",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "20px",
    flexWrap: "wrap",
    marginBottom: "24px",
  },
  title: {
    margin: 0,
    fontSize: "32px",
    fontWeight: "700",
  },
  subtitle: {
    marginTop: "8px",
    color: "#475569",
  },
  card: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "20px",
    boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "10px",
    border: "1px solid #cbd5e1",
    fontSize: "14px",
    boxSizing: "border-box",
  },
  button: {
    padding: "10px 16px",
    borderRadius: "12px",
    border: "none",
    background: "#0f172a",
    color: "white",
    cursor: "pointer",
    fontWeight: "600",
  },
  secondaryButton: {
    padding: "10px 16px",
    borderRadius: "12px",
    border: "1px solid #cbd5e1",
    background: "white",
    color: "#0f172a",
    cursor: "pointer",
    fontWeight: "600",
  },
  grid4: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "16px",
    marginBottom: "24px",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
    gap: "20px",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: "700",
    margin: "6px 0",
  },
  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "600",
    marginBottom: "6px",
  },
  field: {
    marginBottom: "14px",
  },
  bannerError: {
    background: "#fef2f2",
    border: "1px solid #fecaca",
    color: "#991b1b",
    padding: "14px 16px",
    borderRadius: "14px",
    marginBottom: "16px",
  },
  bannerSuccess: {
    background: "#ecfdf5",
    border: "1px solid #a7f3d0",
    color: "#065f46",
    padding: "14px 16px",
    borderRadius: "14px",
    marginBottom: "16px",
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: "8px",
    fontSize: "20px",
  },
  smallText: {
    color: "#64748b",
    fontSize: "14px",
  },
  textarea: {
    width: "100%",
    minHeight: "160px",
    padding: "12px",
    borderRadius: "12px",
    border: "1px solid #cbd5e1",
    boxSizing: "border-box",
    fontSize: "13px",
    fontFamily: "monospace",
    resize: "vertical",
  },
  badge: {
    display: "inline-block",
    padding: "4px 10px",
    borderRadius: "999px",
    background: "#e2e8f0",
    fontSize: "12px",
    marginRight: "8px",
    marginBottom: "8px",
  },
  snippet: {
    background: "#f1f5f9",
    borderRadius: "12px",
    padding: "10px 12px",
    fontSize: "12px",
    color: "#334155",
    marginTop: "8px",
  },
  pre: {
    background: "#020617",
    color: "#e2e8f0",
    borderRadius: "12px",
    padding: "12px",
    fontSize: "12px",
    overflowX: "auto",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
};

function StatCard({ title, value, subtitle }) {
  return (
    <div style={styles.card}>
      <div style={{ fontSize: "14px", color: "#64748b" }}>{title}</div>
      <div style={styles.statValue}>{value}</div>
      <div style={{ fontSize: "13px", color: "#64748b" }}>{subtitle}</div>
    </div>
  );
}

export default function App() {
  const [apiBase, setApiBase] = useState(API_BASE_DEFAULT);
  const [claimForm, setClaimForm] = useState(emptyClaimForm);
  const [claim, setClaim] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [extractions, setExtractions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [triage, setTriage] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState({
    createClaim: false,
    upload: false,
    extract: false,
    summarize: false,
    triage: false,
    refreshDocs: false,
    refreshExtracts: false,
    audit: false,
    fullRefresh: false,
  });

  const canRunDocumentActions = useMemo(() => Boolean(claim?.id), [claim]);

  const setLoadingKey = (key, value) => {
    setLoading((prev) => ({ ...prev, [key]: value }));
  };

  const clearBanners = () => {
    setError("");
    setSuccess("");
  };

  const handleFieldChange = (field, value) => {
    setClaimForm((prev) => ({ ...prev, [field]: value }));
  };

  const resetWorkspace = () => {
    setClaimForm(emptyClaimForm);
    setClaim(null);
    setDocuments([]);
    setExtractions([]);
    setSummary(null);
    setTriage(null);
    setAuditLogs([]);
    setSelectedFile(null);
    clearBanners();
  };

  const createClaim = async () => {
    clearBanners();
    setLoadingKey("createClaim", true);

    try {
      const payload = {
        ...claimForm,
        claimed_amount:
          claimForm.claimed_amount === "" ? null : Number(claimForm.claimed_amount),
        incident_date: claimForm.incident_date || null,
      };

      const response = await fetch(`${apiBase}/api/v1/claims`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to create claim.");
      }

      setClaim(data);
      setDocuments([]);
      setExtractions([]);
      setSummary(null);
      setTriage(null);
      setAuditLogs([]);
      setSuccess(`Claim ${data.external_claim_id} created successfully.`);
    } catch (err) {
      setError(err.message || "Failed to create claim.");
    } finally {
      setLoadingKey("createClaim", false);
    }
  };

  const uploadDocument = async () => {
    if (!claim?.id) {
      setError("Create a claim first.");
      return;
    }

    if (!selectedFile) {
      setError("Select a TXT or PDF document to upload.");
      return;
    }

    clearBanners();
    setLoadingKey("upload", true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/documents`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to upload document.");
      }

      setDocuments((prev) => [data, ...prev]);
      setSelectedFile(null);
      setSuccess(`Uploaded ${data.filename} successfully.`);
    } catch (err) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setLoadingKey("upload", false);
    }
  };

  const refreshDocuments = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("refreshDocs", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/documents`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch documents.");
      }

      setDocuments(data);
      setSuccess("Documents refreshed.");
    } catch (err) {
      setError(err.message || "Failed to fetch documents.");
    } finally {
      setLoadingKey("refreshDocs", false);
    }
  };

  const runExtraction = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("extract", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/extract`, {
        method: "POST",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Extraction failed.");
      }

      setExtractions(data.extracted_fields || []);
      setSuccess(`Extraction complete. ${data.total_extractions} fields found.`);
    } catch (err) {
      setError(err.message || "Extraction failed.");
    } finally {
      setLoadingKey("extract", false);
    }
  };

  const refreshExtractions = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("refreshExtracts", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/extractions`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch extractions.");
      }

      setExtractions(data);
      setSuccess("Extractions refreshed.");
    } catch (err) {
      setError(err.message || "Failed to fetch extractions.");
    } finally {
      setLoadingKey("refreshExtracts", false);
    }
  };

  const runSummary = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("summarize", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/summarize`, {
        method: "POST",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Summarization failed.");
      }

      setSummary(data);
      setSuccess(`Summary generated using ${data.model_name}.`);
    } catch (err) {
      setError(err.message || "Summarization failed.");
    } finally {
      setLoadingKey("summarize", false);
    }
  };

  const runTriage = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("triage", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/triage`, {
        method: "POST",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Triage failed.");
      }

      setTriage(data);
      setSuccess(`Triage complete. Recommended route: ${data.routing_label}`);
    } catch (err) {
      setError(err.message || "Triage failed.");
    } finally {
      setLoadingKey("triage", false);
    }
  };

  const loadAuditLogs = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("audit", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/audit`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load audit logs.");
      }

      setAuditLogs(data);
      setSuccess("Audit logs loaded.");
    } catch (err) {
      setError(err.message || "Failed to load audit logs.");
    } finally {
      setLoadingKey("audit", false);
    }
  };

  const loadFullClaim = async () => {
    if (!claim?.id) return;

    clearBanners();
    setLoadingKey("fullRefresh", true);

    try {
      const response = await fetch(`${apiBase}/api/v1/claims/${claim.id}/full`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load full claim view.");
      }

      setClaim(data.claim || null);
      setDocuments(data.documents || []);
      setExtractions(data.extractions || []);
      setSummary(data.summary || null);
      setTriage(data.triage || null);
      setSuccess("Full claim view refreshed.");
    } catch (err) {
      setError(err.message || "Failed to load full claim view.");
    } finally {
      setLoadingKey("fullRefresh", false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>ClaimPilot</h1>
            <p style={styles.subtitle}>
              Explainable AI Claims Triage & Document Intelligence Platform
            </p>
          </div>

          <div style={{ ...styles.card, minWidth: "320px" }}>
            <label style={styles.label}>API Base URL</label>
            <input
              style={styles.input}
              value={apiBase}
              onChange={(e) => setApiBase(e.target.value)}
              placeholder="http://localhost:8000"
            />
            <p style={{ ...styles.smallText, marginTop: "8px" }}>
              Point this to your FastAPI backend.
            </p>
          </div>
        </div>

        {error && <div style={styles.bannerError}>{error}</div>}
        {success && <div style={styles.bannerSuccess}>{success}</div>}

        <div style={styles.grid4}>
          <StatCard
            title="Active Claim"
            value={claim?.external_claim_id || "None"}
            subtitle={claim ? `${claim.claim_type} • ${claim.status}` : "Create a claim to begin"}
          />
          <StatCard
            title="Documents"
            value={documents.length}
            subtitle="Uploaded and parsed files"
          />
          <StatCard
            title="Extractions"
            value={extractions.length}
            subtitle="Structured extracted fields"
          />
          <StatCard
            title="Route"
            value={triage?.routing_label || "Pending"}
            subtitle={
              triage
                ? `${triage.complexity_label} complexity • ${triage.requires_human_review ? "human review" : "auto-ready"}`
                : "Run triage"
            }
          />
        </div>

        <div style={styles.grid2}>
          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>1. Create claim</h2>
            <p style={styles.smallText}>Start a claim record before uploading documents.</p>

            <div style={styles.field}>
              <label style={styles.label}>External Claim ID</label>
              <input
                style={styles.input}
                value={claimForm.external_claim_id}
                onChange={(e) => handleFieldChange("external_claim_id", e.target.value)}
                placeholder="CLM-2026-0001"
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Claimant Name</label>
              <input
                style={styles.input}
                value={claimForm.claimant_name}
                onChange={(e) => handleFieldChange("claimant_name", e.target.value)}
                placeholder="John Carter"
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Incident Date</label>
              <input
                style={styles.input}
                type="date"
                value={claimForm.incident_date}
                onChange={(e) => handleFieldChange("incident_date", e.target.value)}
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Claim Type</label>
              <input
                style={styles.input}
                value={claimForm.claim_type}
                onChange={(e) => handleFieldChange("claim_type", e.target.value)}
                placeholder="auto / property"
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Claimed Amount</label>
              <input
                style={styles.input}
                type="number"
                value={claimForm.claimed_amount}
                onChange={(e) => handleFieldChange("claimed_amount", e.target.value)}
                placeholder="4200.50"
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Status</label>
              <input
                style={styles.input}
                value={claimForm.status}
                onChange={(e) => handleFieldChange("status", e.target.value)}
                placeholder="new"
              />
            </div>

            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button
                style={styles.button}
                onClick={createClaim}
                disabled={loading.createClaim}
              >
                {loading.createClaim ? "Creating..." : "Create Claim"}
              </button>

              <button
                style={styles.secondaryButton}
                onClick={resetWorkspace}
              >
                Reset
              </button>

              <button
                style={styles.secondaryButton}
                onClick={loadFullClaim}
                disabled={!canRunDocumentActions || loading.fullRefresh}
              >
                {loading.fullRefresh ? "Refreshing..." : "Refresh Full View"}
              </button>
            </div>
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>2. Upload document</h2>
            <p style={styles.smallText}>Attach TXT or PDF claim notes, forms, or notices.</p>

            <div style={styles.field}>
              <label style={styles.label}>Select file</label>
              <input
                style={styles.input}
                type="file"
                accept=".txt,.pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                disabled={!canRunDocumentActions}
              />
            </div>

            {selectedFile && (
              <div style={{ marginBottom: "12px", fontSize: "14px", color: "#475569" }}>
                <div><strong>Filename:</strong> {selectedFile.name}</div>
                <div><strong>Size:</strong> {selectedFile.size} bytes</div>
              </div>
            )}

            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "20px" }}>
              <button
                style={styles.button}
                onClick={uploadDocument}
                disabled={!canRunDocumentActions || loading.upload}
              >
                {loading.upload ? "Uploading..." : "Upload"}
              </button>

              <button
                style={styles.secondaryButton}
                onClick={refreshDocuments}
                disabled={!canRunDocumentActions || loading.refreshDocs}
              >
                {loading.refreshDocs ? "Refreshing..." : "Refresh Docs"}
              </button>
            </div>

            <h3 style={{ marginBottom: "10px" }}>Uploaded documents</h3>
            {documents.length === 0 ? (
              <p style={styles.smallText}>No documents uploaded yet.</p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: "14px",
                    padding: "14px",
                    marginBottom: "12px",
                  }}
                >
                  <div style={{ marginBottom: "8px", fontWeight: "600" }}>{doc.filename}</div>
                  <div style={{ marginBottom: "8px" }}>
                    <span style={styles.badge}>{doc.file_type}</span>
                    <span style={styles.badge}>{doc.parse_status}</span>
                    <span style={styles.badge}>{doc.file_size} bytes</span>
                  </div>
                  <textarea
                    style={styles.textarea}
                    readOnly
                    value={doc.parsed_text || ""}
                  />
                </div>
              ))
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>3. Run extraction</h2>
            <p style={styles.smallText}>Extract structured fields with evidence snippets.</p>

            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "20px" }}>
              <button
                style={styles.button}
                onClick={runExtraction}
                disabled={!canRunDocumentActions || loading.extract}
              >
                {loading.extract ? "Extracting..." : "Run Extraction"}
              </button>

              <button
                style={styles.secondaryButton}
                onClick={refreshExtractions}
                disabled={!canRunDocumentActions || loading.refreshExtracts}
              >
                {loading.refreshExtracts ? "Refreshing..." : "Refresh Extractions"}
              </button>
            </div>

            {extractions.length === 0 ? (
              <p style={styles.smallText}>No extracted fields yet.</p>
            ) : (
              extractions.map((item) => (
                <div
                  key={item.id}
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: "14px",
                    padding: "14px",
                    marginBottom: "12px",
                  }}
                >
                  <div style={{ marginBottom: "8px" }}>
                    <span style={styles.badge}>{item.field_name}</span>
                    <span style={styles.badge}>{item.extraction_method}</span>
                    <span style={styles.badge}>
                      confidence {Number(item.confidence).toFixed(2)}
                    </span>
                  </div>
                  <div style={{ fontSize: "14px", marginBottom: "8px" }}>
                    <strong>Value:</strong> {item.field_value}
                  </div>
                  {item.source_snippet && (
                    <div style={styles.snippet}>{item.source_snippet}</div>
                  )}
                </div>
              ))
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>4. Generate summary</h2>
            <p style={styles.smallText}>Create a grounded operational summary.</p>

            <div style={{ marginBottom: "20px" }}>
              <button
                style={styles.button}
                onClick={runSummary}
                disabled={!canRunDocumentActions || loading.summarize}
              >
                {loading.summarize ? "Generating..." : "Generate Summary"}
              </button>
            </div>

            {summary ? (
              <>
                <div style={{ marginBottom: "10px" }}>
                  <span style={styles.badge}>{summary.model_name}</span>
                  <span style={styles.badge}>
                    confidence {Number(summary.confidence).toFixed(2)}
                  </span>
                </div>

                <div
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: "14px",
                    padding: "14px",
                    background: "#fff",
                    lineHeight: "1.7",
                    marginBottom: "16px",
                  }}
                >
                  {summary.summary_text}
                </div>

                {summary.source_snippets?.length > 0 && (
                  <div>
                    <h3 style={{ marginBottom: "10px" }}>Supporting snippets</h3>
                    {summary.source_snippets.map((snippet, idx) => (
                      <div key={idx} style={{ ...styles.snippet, marginBottom: "8px" }}>
                        {snippet}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <p style={styles.smallText}>No summary generated yet.</p>
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>5. Run triage</h2>
            <p style={styles.smallText}>
              Predict complexity, recommend routing, and flag claims needing human review.
            </p>

            <div style={{ marginBottom: "20px" }}>
              <button
                style={styles.button}
                onClick={runTriage}
                disabled={!canRunDocumentActions || loading.triage}
              >
                {loading.triage ? "Running..." : "Run Triage"}
              </button>
            </div>

            {triage ? (
              <>
                <div style={{ marginBottom: "10px" }}>
                  <span style={styles.badge}>complexity {triage.complexity_label}</span>
                  <span style={styles.badge}>
                    score {Number(triage.complexity_score).toFixed(2)}
                  </span>
                  <span style={styles.badge}>route {triage.routing_label}</span>
                  <span style={styles.badge}>
                    route confidence {Number(triage.routing_confidence).toFixed(2)}
                  </span>
                </div>

                <div style={{ marginBottom: "10px", fontSize: "14px" }}>
                  <strong>Requires human review:</strong>{" "}
                  {triage.requires_human_review ? "Yes" : "No"}
                </div>

                {triage.reason_codes?.length > 0 && (
                  <div style={{ marginBottom: "12px" }}>
                    <h3 style={{ marginBottom: "8px" }}>Reason codes</h3>
                    {triage.reason_codes.map((code, idx) => (
                      <span key={idx} style={styles.badge}>{code}</span>
                    ))}
                  </div>
                )}

                {triage.review_flags?.length > 0 && (
                  <div style={{ marginBottom: "12px" }}>
                    <h3 style={{ marginBottom: "8px" }}>Review flags</h3>
                    {triage.review_flags.map((flag, idx) => (
                      <span key={idx} style={styles.badge}>{flag}</span>
                    ))}
                  </div>
                )}

                <h3 style={{ marginBottom: "8px" }}>Feature snapshot</h3>
                <pre style={styles.pre}>
                  {JSON.stringify(triage.feature_snapshot || {}, null, 2)}
                </pre>
              </>
            ) : (
              <p style={styles.smallText}>No triage result yet.</p>
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>6. Audit trail</h2>
            <p style={styles.smallText}>
              Load the claim-level audit history for extraction, summary, and triage events.
            </p>

            <div style={{ marginBottom: "12px" }}>
              <button
                style={styles.secondaryButton}
                onClick={loadAuditLogs}
                disabled={!canRunDocumentActions || loading.audit}
              >
                {loading.audit ? "Loading..." : "Load Audit Logs"}
              </button>
            </div>

            {auditLogs.length === 0 ? (
              <p style={styles.smallText}>No audit logs loaded yet.</p>
            ) : (
              auditLogs.map((log) => (
                <div
                  key={log.id}
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: "14px",
                    padding: "12px",
                    marginBottom: "10px",
                  }}
                >
                  <div style={{ marginBottom: "8px" }}>
                    <span style={styles.badge}>{log.event_type}</span>
                    <span style={styles.badge}>{log.actor}</span>
                  </div>
                  <pre style={styles.pre}>
                    {JSON.stringify(log.event_payload || {}, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>

        <div style={{ ...styles.card, marginTop: "24px" }}>
          <h2 style={styles.sectionTitle}>Debug view</h2>
          <div style={styles.grid2}>
            <div>
              <h3>Claim object</h3>
              <pre style={styles.pre}>{JSON.stringify(claim || {}, null, 2)}</pre>
            </div>
            <div>
              <h3>Latest summary</h3>
              <pre style={styles.pre}>{JSON.stringify(summary || {}, null, 2)}</pre>
            </div>
            <div>
              <h3>Latest triage</h3>
              <pre style={styles.pre}>{JSON.stringify(triage || {}, null, 2)}</pre>
            </div>
            <div>
              <h3>Audit logs</h3>
              <pre style={styles.pre}>{JSON.stringify(auditLogs || [], null, 2)}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}