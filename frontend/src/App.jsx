import { useState } from "react";
import "./App.css";
import { analyzeImage } from "./api";
import { HistoryList } from "./components/HistoryList";
import { ResultView } from "./components/ResultView";
import { UploadForm } from "./components/UploadForm";
import { addHistoryEntry, loadHistory } from "./history";

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | loading | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState(loadHistory);

  async function handleFileSelected(file) {
    setStatus("loading");
    setError(null);
    setResult(null);
    try {
      const analyzed = await analyzeImage(file);
      setResult(analyzed);
      setStatus("idle");
      setHistory(
        addHistoryEntry({
          imageId: analyzed.imageId,
          label: analyzed.label,
          confidence: analyzed.confidence,
          date: new Date().toISOString(),
        })
      );
    } catch (e) {
      setError(e.message);
      setStatus("error");
    }
  }

  return (
    <div className="app">
      <header>
        <h1>OCTera</h1>
        <p>Анализ OCT-снимков сетчатки с помощью ИИ</p>
      </header>

      <UploadForm onFileSelected={handleFileSelected} disabled={status === "loading"} />

      {status === "loading" && <p className="status-message">Анализируем снимок…</p>}
      {status === "error" && <p className="status-message status-message--error">{error}</p>}
      {result && <ResultView result={result} />}

      <HistoryList entries={history} />
    </div>
  );
}
