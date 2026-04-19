import type { KernelSnapshot } from "../../data/types";

interface KernelHeatmapProps {
  snapshot: KernelSnapshot | null;
  dim: number;
}

function valueToColor(v: number, maxVal: number): string {
  const t = Math.min(1, v / Math.max(maxVal, 1e-6));
  // Dark blue → cyan → yellow → red
  const r = Math.round(255 * Math.min(1, t * 2));
  const g = Math.round(255 * (t < 0.5 ? t * 2 : 2 - t * 2));
  const b = Math.round(255 * Math.max(0, 1 - t * 2));
  return `rgb(${r},${g},${b})`;
}

export default function KernelHeatmap({ snapshot, dim }: KernelHeatmapProps) {
  if (!snapshot) {
    return <div className="heatmap-placeholder" data-testid="kernel-heatmap">No kernel data at this step</div>;
  }

  const kernel = snapshot.kernel;
  const maxVal = Math.max(...kernel.flat());
  const cellSize = Math.min(20, Math.floor(320 / dim));

  return (
    <div className="heatmap" data-testid="kernel-heatmap">
      <div className="heatmap__label">Step {snapshot.step} — {dim}x{dim} kernel</div>
      <svg
        width={cellSize * dim + 1}
        height={cellSize * dim + 1}
        className="heatmap__svg"
      >
        {kernel.map((row, i) =>
          row.map((val, j) => (
            <rect
              key={`${i}-${j}`}
              x={j * cellSize}
              y={i * cellSize}
              width={cellSize}
              height={cellSize}
              fill={valueToColor(val, maxVal)}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth={0.5}
            >
              <title>
                [{i},{j}] = {val.toFixed(4)}
              </title>
            </rect>
          )),
        )}
      </svg>
    </div>
  );
}
