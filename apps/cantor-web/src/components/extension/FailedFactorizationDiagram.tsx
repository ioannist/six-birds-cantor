import type { FactorizationTest, T0ObjectMap, T1ExtendedObjectMap } from "../../data/types";
import Icon from "../ui/Icon";

interface FailedFactorizationDiagramProps {
  baseMap: T0ObjectMap;
  extendedMap: T1ExtendedObjectMap;
  test: FactorizationTest;
  baseTheoryId: string;
  extendedTheoryId: string;
}

export default function FailedFactorizationDiagram({
  baseMap,
  extendedMap,
  test,
  baseTheoryId,
  extendedTheoryId,
}: FailedFactorizationDiagramProps) {
  const rate = (test.non_factorization_rate * 100).toFixed(1);

  return (
    <div className="factorization-diagram" data-testid="factorization-diagram">
      <h3>Failed Factorization</h3>
      <div className="factorization-diagram__visual">
        <svg viewBox="0 0 440 200" className="factorization-diagram__svg">
          {/* T0 box */}
          <rect x="20" y="30" width="160" height="60" rx="8"
            fill="rgba(74, 144, 217, 0.12)" stroke="var(--color-t0)" strokeWidth="1.5" />
          <text x="100" y="55" textAnchor="middle" fill="var(--color-t0)" fontSize="13" fontWeight="600">
            T0
          </text>
          <text x="100" y="75" textAnchor="middle" fill="var(--color-text-muted)" fontSize="9">
            {baseMap.map_id}
          </text>

          {/* T1 box */}
          <rect x="260" y="30" width="160" height="60" rx="8"
            fill="rgba(217, 122, 74, 0.12)" stroke="var(--color-t1)" strokeWidth="1.5" />
          <text x="340" y="55" textAnchor="middle" fill="var(--color-t1)" fontSize="13" fontWeight="600">
            T1
          </text>
          <text x="340" y="75" textAnchor="middle" fill="var(--color-text-muted)" fontSize="9">
            {extendedMap.map_id}
          </text>

          {/* Arrow T0 → T1 (attempted factorization) */}
          <line x1="180" y1="60" x2="255" y2="60"
            stroke="var(--color-nonclaim)" strokeWidth="2" strokeDasharray="6 4" />
          <polygon points="255,55 265,60 255,65" fill="var(--color-nonclaim)" />

          {/* X mark — failed */}
          <line x1="210" y1="45" x2="230" y2="70" stroke="var(--color-nonclaim)" strokeWidth="3" strokeLinecap="round" />
          <line x1="230" y1="45" x2="210" y2="70" stroke="var(--color-nonclaim)" strokeWidth="3" strokeLinecap="round" />

          {/* Bottom: non-factorization evidence */}
          <rect x="100" y="120" width="240" height="55" rx="8"
            fill="rgba(201, 84, 84, 0.08)" stroke="rgba(201, 84, 84, 0.3)" strokeWidth="1" />
          <text x="220" y="142" textAnchor="middle" fill="var(--color-nonclaim)" fontSize="11" fontWeight="600">
            Non-factorization: {rate}%
          </text>
          <text x="220" y="162" textAnchor="middle" fill="var(--color-text-muted)" fontSize="9">
            {test.multiple_T1_strata_per_T0_class} T1 strata per T0 class
          </text>
        </svg>
      </div>
      <p className="factorization-diagram__note">{test.note}</p>
    </div>
  );
}
