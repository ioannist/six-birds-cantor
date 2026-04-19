import type { PressureProfile } from "../../data/types";

interface GlobalPressureCardProps {
  pressureRoute: string;
  feketeGapProxy: number;
  profiles: Record<string, PressureProfile>;
}

export default function GlobalPressureCard({
  pressureRoute,
  feketeGapProxy,
  profiles,
}: GlobalPressureCardProps) {
  const sortedParams = Object.keys(profiles).sort((a, b) => Number(a) - Number(b));

  return (
    <div className="t1-panel" data-testid="global-pressure">
      <h3>Global T0 Pressure Object</h3>
      <div className="t1-panel__metric-row">
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Route</span>
          <span className="t1-panel__metric-value" style={{ color: "var(--color-t0)", fontSize: "0.78rem" }}>
            {pressureRoute.replace(/_/g, " ")}
          </span>
        </div>
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Fekete gap proxy</span>
          <span className="t1-panel__metric-value" style={{ color: "var(--color-t0)" }}>
            {feketeGapProxy.toFixed(4)}
          </span>
        </div>
      </div>
      <table className="t1-panel__table">
        <thead>
          <tr><th>Param</th><th>Gap proxy</th><th>Pressure proxy</th></tr>
        </thead>
        <tbody>
          {sortedParams.map((p) => (
            <tr key={p}>
              <td>{p}</td>
              <td>{profiles[p].gap_proxy.toFixed(4)}</td>
              <td>{profiles[p].pressure_proxy.toFixed(6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
