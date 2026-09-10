import { DISEASE_INFO } from "../diseaseInfo";

export function ResultView({ result }) {
  const info = DISEASE_INFO[result.label] ?? {
    name: result.label,
    description: "",
  };

  return (
    <div className="result-view">
      <h2>{info.name}</h2>
      <p className="result-view__confidence">
        Уверенность модели: {(result.confidence * 100).toFixed(1)}%
      </p>
      <p>{info.description}</p>
      <p className="disclaimer">
        Это не медицинский диагноз. Результат носит справочный характер —
        для точной диагностики обратитесь к врачу-офтальмологу.
      </p>
    </div>
  );
}
