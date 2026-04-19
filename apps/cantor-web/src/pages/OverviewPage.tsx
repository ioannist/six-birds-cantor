import { useEffect, useState } from "react";
import { loadIndex } from "../data/loadData";
import type { DataIndex } from "../data/types";
import { useAppStore } from "../app/store";

export default function OverviewPage() {
  const store = useAppStore();
  const [index, setIndex] = useState<DataIndex | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadIndex()
      .then(setIndex)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section>
      <h1>Overview</h1>
      <p className="page-subtitle">
        Layer: <code>{store.selectedTheoremLayer}</code> | Witness:{" "}
        <code>{store.selectedWitnessId}</code> | Shell:{" "}
        <code>{store.selectedShell}</code> | Time:{" "}
        <code>{store.selectedTimeIndex}</code>
      </p>

      <h2>Loaded Datasets</h2>
      {error && <p className="error" role="alert">Load error: {error}</p>}
      {!index && !error && <p>Loading...</p>}
      {index && (
        <div>
          <p>
            Schema: <code>{index.schema_version}</code> | Generated:{" "}
            <code>{index.generated_at_utc}</code>
          </p>
          <ul>
            {index.datasets.map((ds) => (
              <li key={ds.name}>
                <strong>{ds.name}</strong> — <code>{ds.path}</code>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
