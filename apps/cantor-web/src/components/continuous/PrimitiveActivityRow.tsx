import { primitiveColors, primitiveLabels } from "../../theme/tokens";

interface PrimitiveActivityRowProps {
  actionWeights: Record<string, number>;
  primitiveActivity: Record<string, boolean>;
}

const PRIMITIVES = ["P1", "P2", "P3", "P4", "P5", "P6"] as const;

export default function PrimitiveActivityRow({
  actionWeights,
  primitiveActivity,
}: PrimitiveActivityRowProps) {
  return (
    <div className="activity-row" data-testid="primitive-activity">
      {PRIMITIVES.map((p) => {
        const active = primitiveActivity[p] ?? false;
        const weight = actionWeights[p] ?? 0;
        const color = primitiveColors[p];
        const barWidth = Math.round(weight * 100);

        return (
          <div
            key={p}
            className={`activity-cell${active ? "" : " activity-cell--disabled"}`}
          >
            <div className="activity-cell__header">
              <span
                className="activity-cell__dot"
                style={{ background: active ? color : "rgba(255,255,255,0.15)" }}
              />
              <span className="activity-cell__label">{p}</span>
              <span className="activity-cell__name">
                {primitiveLabels[p]}
              </span>
            </div>
            <div className="activity-cell__bar-bg">
              <div
                className="activity-cell__bar"
                style={{ width: `${barWidth}%`, background: color }}
              />
            </div>
            <span className="activity-cell__weight">
              {(weight * 100).toFixed(1)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}
