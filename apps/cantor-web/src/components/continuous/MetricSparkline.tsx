interface MetricSparklineProps {
  label: string;
  data: number[];
  currentIndex: number;
  color: string;
  height?: number;
  width?: number;
}

export default function MetricSparkline({
  label,
  data,
  currentIndex,
  color,
  height = 60,
  width = 400,
}: MetricSparklineProps) {
  if (data.length === 0) return null;

  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const range = maxVal - minVal || 1;
  const padding = 2;
  const innerH = height - padding * 2;
  const innerW = width - padding * 2;

  const points = data
    .map((v, i) => {
      const x = padding + (i / Math.max(1, data.length - 1)) * innerW;
      const y = padding + innerH - ((v - minVal) / range) * innerH;
      return `${x},${y}`;
    })
    .join(" ");

  const cursorX =
    padding + (currentIndex / Math.max(1, data.length - 1)) * innerW;
  const cursorY =
    currentIndex < data.length
      ? padding + innerH - ((data[currentIndex] - minVal) / range) * innerH
      : 0;
  const currentVal = currentIndex < data.length ? data[currentIndex] : 0;

  return (
    <div className="sparkline" data-testid={`sparkline-${label.toLowerCase().replace(/\s/g, "-")}`}>
      <div className="sparkline__header">
        <span className="sparkline__label">{label}</span>
        <span className="sparkline__value" style={{ color }}>
          {currentVal.toFixed(4)}
        </span>
      </div>
      <svg width={width} height={height} className="sparkline__svg">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          opacity={0.7}
        />
        {currentIndex < data.length && (
          <>
            <line
              x1={cursorX}
              y1={padding}
              x2={cursorX}
              y2={height - padding}
              stroke="rgba(255,255,255,0.3)"
              strokeWidth={1}
            />
            <circle cx={cursorX} cy={cursorY} r={3} fill={color} />
          </>
        )}
      </svg>
      <div className="sparkline__range">
        <span>{minVal.toFixed(3)}</span>
        <span>{maxVal.toFixed(3)}</span>
      </div>
    </div>
  );
}
