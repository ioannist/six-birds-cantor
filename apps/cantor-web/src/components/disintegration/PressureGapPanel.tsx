import type { DisintegrationDescriptor } from "../../data/types";

interface PressureGapPanelProps {
  descriptors: DisintegrationDescriptor[];
  minGap: number | null;
}

export default function PressureGapPanel({ descriptors, minGap }: PressureGapPanelProps) {
  return (
    <div className="t1-panel" data-testid="pressure-gap">
      <h3>Weighted Package-Conditioned Pressure Gap</h3>
      {minGap !== null && (
        <div className="t1-panel__metric-row" style={{ marginBottom: "var(--space-sm)" }}>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Minimum gap across descriptors</span>
            <span className="t1-panel__metric-value t1-panel__metric-value--large" style={{ color: "var(--color-closed)" }}>
              {minGap.toFixed(6)}
            </span>
          </div>
        </div>
      )}
      <table className="t1-panel__table">
        <thead>
          <tr>
            <th>Lens</th>
            <th>Tau</th>
            <th>Gap (1.0)</th>
            <th>Bounded</th>
            <th>Fibers</th>
            <th>Deficit proxy</th>
          </tr>
        </thead>
        <tbody>
          {descriptors.map((d, i) => {
            const gap1 = d.pressure_gap["1.0"];
            return (
              <tr key={i}>
                <td>{d.lens_state.replace(/_/g, " ")}</td>
                <td>{d.tau}</td>
                <td style={{ color: "var(--color-closed)" }}>{gap1 ? gap1.gap.toFixed(6) : "—"}</td>
                <td style={{ color: d.gap_bounded_away_from_zero ? "var(--color-closed)" : "var(--color-nonclaim)" }}>
                  {d.gap_bounded_away_from_zero ? "yes" : "no"}
                </td>
                <td>{d.fiber_count}</td>
                <td>{d.closure_deficit_proxy.toExponential(2)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
