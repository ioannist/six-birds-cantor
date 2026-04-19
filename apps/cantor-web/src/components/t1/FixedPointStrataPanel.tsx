import type { T1FixedPointStrata } from "../../data/types";

interface FixedPointStrataPanelProps {
  strata: T1FixedPointStrata;
}

export default function FixedPointStrataPanel({ strata }: FixedPointStrataPanelProps) {
  return (
    <div className="t1-panel" data-testid="fixed-point-strata">
      <h3>Fixed-Point Strata</h3>
      <div className="t1-panel__metric-row">
        <div className="t1-panel__metric">
          <span className="t1-panel__metric-label">Distinct strata</span>
          <span className="t1-panel__metric-value t1-panel__metric-value--large">
            {strata.distinct_count}
          </span>
        </div>
      </div>
      <div className="t1-panel__detail">
        <span className="t1-panel__detail-label">
          {strata.distinct_count} distinct fixed-point signatures found across all
          tau/lens/initial combinations.
        </span>
      </div>
    </div>
  );
}
