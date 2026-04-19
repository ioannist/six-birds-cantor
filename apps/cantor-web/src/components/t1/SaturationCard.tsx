import type { T1Saturation } from "../../data/types";

interface SaturationCardProps {
  saturation: T1Saturation;
}

export default function SaturationCard({ saturation }: SaturationCardProps) {
  return (
    <div className="t1-panel" data-testid="saturation-card">
      <h3>Saturation Behavior</h3>
      <div className="t1-panel__metric-row">
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Overall saturated</span>
          <span
            className="t1-panel__metric-value"
            style={{ color: saturation.saturated ? "var(--color-closed)" : "var(--color-support)" }}
          >
            {saturation.saturated ? "Yes" : "No"}
          </span>
        </div>
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Saturated panels</span>
          <span className="t1-panel__metric-value">
            {saturation.saturated_panel_count} / {saturation.total_panels}
          </span>
        </div>
      </div>
      <table className="t1-panel__table">
        <thead>
          <tr>
            <th>Tau</th>
            <th>Lens</th>
            <th>Distinct FPs</th>
            <th>Saturated</th>
          </tr>
        </thead>
        <tbody>
          {saturation.panel_summaries.map((p, i) => (
            <tr key={i}>
              <td>{p.tau}</td>
              <td>{p.lens_state.replace(/_/g, " ")}</td>
              <td>{p.distinct_fixed_points}</td>
              <td style={{ color: p.saturated ? "var(--color-closed)" : "var(--color-text-muted)" }}>
                {p.saturated ? "yes" : "no"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
