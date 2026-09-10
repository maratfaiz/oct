import { DISEASE_INFO } from "../diseaseInfo";

export function HistoryList({ entries }) {
  if (entries.length === 0) return null;

  return (
    <div className="history">
      <h3>История загрузок (в этом браузере)</h3>
      <ul>
        {entries.map((entry) => (
          <li key={entry.imageId}>
            <span>{new Date(entry.date).toLocaleString("ru-RU")}</span>
            <span>{DISEASE_INFO[entry.label]?.name ?? entry.label}</span>
            <span>{(entry.confidence * 100).toFixed(1)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
