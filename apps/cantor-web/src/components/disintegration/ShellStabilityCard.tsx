interface ShellStabilityCardProps {
  gapBoundedOnBoth: boolean;
  macroFailureAligns: boolean;
  workingRoute: string;
}

export default function ShellStabilityCard({
  gapBoundedOnBoth,
  macroFailureAligns,
  workingRoute,
}: ShellStabilityCardProps) {
  return (
    <div className="t1-panel" data-testid="shell-stability">
      <h3>Shell Stability of the Consequence</h3>
      <div className="t1-panel__metric-row">
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Gap bounded on both witnesses</span>
          <span className="t1-panel__metric-value" style={{ color: gapBoundedOnBoth ? "var(--color-closed)" : "var(--color-nonclaim)" }}>
            {gapBoundedOnBoth ? "Yes" : "No"}
          </span>
        </div>
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Macro-admissibility failure aligns</span>
          <span className="t1-panel__metric-value" style={{ color: macroFailureAligns ? "var(--color-closed)" : "var(--color-nonclaim)" }}>
            {macroFailureAligns ? "Yes" : "No"}
          </span>
        </div>
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Working route</span>
          <span className="t1-panel__metric-value" style={{ fontSize: "0.78rem" }}>
            {workingRoute.replace(/_/g, " ")}
          </span>
        </div>
      </div>
    </div>
  );
}
