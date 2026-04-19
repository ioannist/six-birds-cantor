import type { ShellUniformBounds } from "../../data/types";

interface ShellMarkerLegendProps {
  bounds: ShellUniformBounds;
  shellExitCount: number;
  allPrimitivesActive: boolean;
}

export default function ShellMarkerLegend({
  bounds,
  shellExitCount,
  allPrimitivesActive,
}: ShellMarkerLegendProps) {
  return (
    <div className="shell-legend" data-testid="shell-markers">
      <h3>Shell-Stable Class Markers</h3>
      <div className="shell-legend__grid">
        <div className="shell-legend__item">
          <span className="shell-legend__label">Budget range</span>
          <span className="shell-legend__value">
            [{bounds.budget_range[0].toFixed(3)}, {bounds.budget_range[1].toFixed(3)}]
          </span>
        </div>
        <div className="shell-legend__item">
          <span className="shell-legend__label">Tau range</span>
          <span className="shell-legend__value">
            [{bounds.tau_range[0].toFixed(3)}, {bounds.tau_range[1].toFixed(3)}]
          </span>
        </div>
        <div className="shell-legend__item">
          <span className="shell-legend__label">Lens margin (min)</span>
          <span className="shell-legend__value">{bounds.lens_margin_min.toFixed(4)}</span>
        </div>
        <div className="shell-legend__item">
          <span className="shell-legend__label">Packaging margin (min)</span>
          <span className="shell-legend__value">{bounds.packaging_margin_min.toFixed(4)}</span>
        </div>
        <div className="shell-legend__item">
          <span className="shell-legend__label">Shell exits</span>
          <span className="shell-legend__value">{shellExitCount}</span>
        </div>
        <div className="shell-legend__item">
          <span className="shell-legend__label">All 6 primitives active</span>
          <span className="shell-legend__value">{allPrimitivesActive ? "Yes" : "No"}</span>
        </div>
      </div>
    </div>
  );
}
