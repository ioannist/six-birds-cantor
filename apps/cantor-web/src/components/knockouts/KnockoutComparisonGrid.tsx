import type { KnockoutEntry, FullLoopMetrics } from "../../data/types";
import { primitiveColors } from "../../theme/tokens";
import Badge from "../ui/Badge";

interface KnockoutComparisonGridProps {
  fullLoop: FullLoopMetrics;
  knockouts: KnockoutEntry[];
}

function CollapseBadge({ degraded }: { degraded: boolean }) {
  return degraded ? (
    <Badge variant="nonclaim" label="degraded" />
  ) : (
    <Badge variant="closed" label="intact" />
  );
}

export default function KnockoutComparisonGrid({
  fullLoop,
  knockouts,
}: KnockoutComparisonGridProps) {
  return (
    <div className="knockout-grid" data-testid="knockout-grid">
      {/* Full loop reference */}
      <div className="knockout-card knockout-card--full" data-testid="full-loop-card">
        <div className="knockout-card__header">
          <span className="knockout-card__label" style={{ color: "var(--color-closed)" }}>
            Full Loop (all 6 active)
          </span>
          <Badge variant="closed" label="reference" />
        </div>
        <div className="knockout-card__metrics">
          <MetricRow label="Lens switches" value={fullLoop.lens_switch_count} />
          <MetricRow label="Packaging switches" value={fullLoop.packaging_switch_count} />
          <MetricRow label="Tau switches" value={fullLoop.tau_switch_count} />
          <MetricRow label="Budget" value={`${fullLoop.budget_min.toFixed(1)} – ${fullLoop.budget_max.toFixed(1)}`} />
          <MetricRow label="Tau range" value={`${fullLoop.tau_min.toFixed(3)} – ${fullLoop.tau_max.toFixed(3)}`} />
          <MetricRow label="Defect proxy" value={fullLoop.closure_defect_proxy.toFixed(4)} />
        </div>
      </div>

      {/* Knockout cards */}
      {knockouts.map((ko) => {
        const color = primitiveColors[ko.removed as keyof typeof primitiveColors] ?? "var(--color-text)";
        return (
          <div
            key={ko.removed}
            className={`knockout-card${ko.material_degradation ? " knockout-card--degraded" : ""}`}
            data-testid={`knockout-${ko.removed}`}
          >
            <div className="knockout-card__header">
              <span className="knockout-card__dot" style={{ background: color }} />
              <span className="knockout-card__label">
                No <strong>{ko.removed}</strong>
              </span>
              <CollapseBadge degraded={ko.material_degradation} />
            </div>
            <div className="knockout-card__metrics">
              <MetricRow label="Lens switches" value={ko.summary.lens_switch_count} warn={ko.summary.lens_switch_count === 0} />
              <MetricRow label="Pkg switches" value={ko.summary.packaging_switch_count} warn={ko.summary.packaging_switch_count === 0} />
              <MetricRow label="Tau switches" value={ko.summary.tau_switch_count} warn={ko.summary.tau_switch_count <= 1} />
              <MetricRow label="Budget" value={`${ko.summary.budget_min.toFixed(1)} – ${ko.summary.budget_max.toFixed(1)}`} warn={ko.summary.budget_max - ko.summary.budget_min < 1} />
              <MetricRow label="Defect proxy" value={ko.closure_defect_proxy.toFixed(4)} />
            </div>
            {ko.material_reasons.length > 0 && (
              <div className="knockout-card__reasons">
                {ko.material_reasons.map((r, i) => (
                  <span key={i} className="knockout-card__reason">{r}</span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function MetricRow({ label, value, warn }: { label: string; value: string | number; warn?: boolean }) {
  return (
    <div className="knockout-metric">
      <span className="knockout-metric__label">{label}</span>
      <span
        className="knockout-metric__value"
        style={warn ? { color: "var(--color-nonclaim)" } : undefined}
      >
        {value}
      </span>
    </div>
  );
}
