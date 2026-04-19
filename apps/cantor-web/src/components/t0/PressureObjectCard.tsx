import type { T0PressureObject } from "../../data/types";

interface PressureObjectCardProps {
  pressure: T0PressureObject;
}

export default function PressureObjectCard({ pressure }: PressureObjectCardProps) {
  const profiles = Object.entries(pressure.pressure_profiles).sort(
    ([a], [b]) => Number(a) - Number(b),
  );

  return (
    <div className="pressure-card" data-testid="pressure-object">
      <h3>Cocycle Pressure Object</h3>
      <div className="pressure-card__route">
        Route: <code>{pressure.pressure_route.replace(/_/g, " ")}</code>
      </div>
      <div className="pressure-card__metrics">
        <div className="pressure-card__metric">
          <span className="pressure-card__metric-label">Fekete gap proxy</span>
          <span className="pressure-card__metric-value">{pressure.fekete_gap_proxy.toFixed(4)}</span>
        </div>
        <div className="pressure-card__metric">
          <span className="pressure-card__metric-label">Growth bound proxy</span>
          <span className="pressure-card__metric-value">{pressure.growth_bound_proxy.toFixed(4)}</span>
        </div>
        <div className="pressure-card__metric">
          <span className="pressure-card__metric-label">Lens margin (min)</span>
          <span className="pressure-card__metric-value">{pressure.min_lens_margin.toFixed(4)}</span>
        </div>
        <div className="pressure-card__metric">
          <span className="pressure-card__metric-label">Packaging margin (min)</span>
          <span className="pressure-card__metric-value">{pressure.min_packaging_margin.toFixed(4)}</span>
        </div>
      </div>

      <h4>Pressure Profiles</h4>
      <table className="pressure-card__table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Gap proxy</th>
            <th>Pressure proxy</th>
            <th>Sign</th>
          </tr>
        </thead>
        <tbody>
          {profiles.map(([param, profile]) => (
            <tr key={param}>
              <td>{param}</td>
              <td>{profile.gap_proxy.toFixed(4)}</td>
              <td>{profile.pressure_proxy.toFixed(6)}</td>
              <td>{profile.sign > 0 ? "+" : "−"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
