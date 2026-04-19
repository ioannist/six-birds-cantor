interface TimelineScrubberProps {
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
}

export default function TimelineScrubber({
  min,
  max,
  value,
  onChange,
}: TimelineScrubberProps) {
  return (
    <div className="scrubber" data-testid="timeline-scrubber">
      <label className="scrubber__label">
        Time step: <strong>{value}</strong> / {max}
      </label>
      <input
        type="range"
        className="scrubber__input"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="time step"
      />
    </div>
  );
}
