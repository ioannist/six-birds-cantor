interface StateCardProps {
  label: string;
  value: string;
  color?: string;
}

export default function StateCard({ label, value, color }: StateCardProps) {
  return (
    <div className="state-card" data-testid={`state-card-${label.toLowerCase().replace(/\s/g, "-")}`}>
      <span className="state-card__label">{label}</span>
      <span className="state-card__value" style={color ? { color } : undefined}>
        {value}
      </span>
    </div>
  );
}
