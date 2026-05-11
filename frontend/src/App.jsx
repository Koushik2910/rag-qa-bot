import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi Koushik! Ask me anything about your test repos. Try: 'What tests do we have?' or 'What is not covered?'" }
  ]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [owner, setOwner] = useState("Koushik2910");
  const [repo, setRepo] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState("");
  const [gapLoading, setGapLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim()) return;
    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/chat`, { question, repo });
      setMessages((prev) => [...prev, { role: "bot", text: res.data.answer }]);
      setSources(res.data.sources || []);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "Error — is the backend running?" }]);
    }
    setLoading(false);
  };

  const ingestRepo = async () => {
    if (!repo.trim()) return;
    setIngesting(true);
    setIngestMsg("");
    try {
      const res = await axios.post(`${API}/ingest`, { owner, repo });
      setIngestMsg(`✅ ${res.data.files_fetched} files, ${res.data.chunks_added} chunks added`);
    } catch {
      setIngestMsg("❌ Ingest failed — check repo name");
    }
    setIngesting(false);
  };

  const findGaps = async () => {
    if (!repo.trim()) return;
    setGapLoading(true);
    try {
      const res = await axios.post(`${API}/gaps`, { owner, repo });
      setMessages((prev) => [...prev, { role: "bot", text: res.data.analysis }]);
      setSources(res.data.sources || []);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "Gap analysis failed" }]);
    }
    setGapLoading(false);
  };

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "Arial, sans-serif", background: "#f5f7fa" }}>

      {/* Sidebar */}
      <div style={{ width: "280px", background: "#1e1e2e", color: "white", padding: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "16px", color: "#7c6af7" }}>QA Coverage Agent</h2>
          <p style={{ fontSize: "12px", color: "#888", margin: "4px 0 0" }}>Powered by Groq + ChromaDB</p>
        </div>

        <div style={{ borderTop: "1px solid #333", paddingTop: "16px" }}>
          <p style={{ fontSize: "12px", color: "#aaa", margin: "0 0 8px" }}>CONNECT REPO</p>
          <input
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            placeholder="GitHub owner"
            style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #444", background: "#2a2a3e", color: "white", fontSize: "13px", marginBottom: "8px", boxSizing: "border-box" }}
          />
          <input
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="Repo name e.g. self-healing-framework"
            style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #444", background: "#2a2a3e", color: "white", fontSize: "13px", marginBottom: "8px", boxSizing: "border-box" }}
          />
          <button
            onClick={ingestRepo}
            disabled={ingesting}
            style={{ width: "100%", padding: "9px", background: "#7c6af7", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "13px", fontWeight: "bold" }}
          >
            {ingesting ? "Indexing..." : "Index Repo"}
          </button>
          {ingestMsg && <p style={{ fontSize: "12px", color: "#7c6af7", margin: "8px 0 0" }}>{ingestMsg}</p>}
        </div>

        <div style={{ borderTop: "1px solid #333", paddingTop: "16px" }}>
          <p style={{ fontSize: "12px", color: "#aaa", margin: "0 0 8px" }}>ACTIONS</p>
          <button
            onClick={findGaps}
            disabled={gapLoading || !repo.trim()}
            style={{ width: "100%", padding: "9px", background: "#e74c3c", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "13px", fontWeight: "bold" }}
          >
            {gapLoading ? "Analyzing..." : "Find Coverage Gaps"}
          </button>
        </div>

        {sources.length > 0 && (
          <div style={{ borderTop: "1px solid #333", paddingTop: "16px" }}>
            <p style={{ fontSize: "12px", color: "#aaa", margin: "0 0 8px" }}>SOURCES</p>
            {sources.map((s, i) => (
              <div key={i} style={{ fontSize: "11px", color: "#bbb", padding: "4px 0", borderBottom: "1px solid #333" }}>
                <span style={{ color: "#7c6af7" }}>{s.repo}/</span>{s.file}
                <span style={{ float: "right", color: "#555" }}>{s.score}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Chat */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "16px 20px", background: "white", borderBottom: "1px solid #e0e0e0" }}>
          <h1 style={{ margin: 0, fontSize: "18px", color: "#1e1e2e" }}>QA Knowledge Bot</h1>
          <p style={{ margin: 0, fontSize: "13px", color: "#888" }}>Ask questions about your test codebase</p>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "20px", display: "flex", flexDirection: "column", gap: "12px" }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{
                maxWidth: "70%", padding: "12px 16px", borderRadius: "12px", fontSize: "14px", lineHeight: "1.6",
                background: msg.role === "user" ? "#7c6af7" : "white",
                color: msg.role === "user" ? "white" : "#1e1e2e",
                border: msg.role === "bot" ? "1px solid #e0e0e0" : "none",
                whiteSpace: "pre-wrap"
              }}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <div style={{ padding: "12px 16px", background: "white", borderRadius: "12px", border: "1px solid #e0e0e0", fontSize: "14px", color: "#888" }}>
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div style={{ padding: "16px 20px", background: "white", borderTop: "1px solid #e0e0e0", display: "flex", gap: "10px" }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about your tests... e.g. What tests cover login?"
            style={{ flex: 1, padding: "12px 16px", borderRadius: "8px", border: "1px solid #ddd", fontSize: "14px", outline: "none" }}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            style={{ padding: "12px 24px", background: "#7c6af7", color: "white", border: "none", borderRadius: "8px", cursor: "pointer", fontSize: "14px", fontWeight: "bold" }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}