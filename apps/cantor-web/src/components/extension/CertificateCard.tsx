interface CertificateCardProps {
  title: string;
  testId: string;
  items: { label: string; value: string | number }[];
}

export default function CertificateCard({ title, testId, items }: CertificateCardProps) {
  return (
    <div className="certificate-card" data-testid={testId}>
      <h4>{title}</h4>
      <div className="certificate-card__grid">
        {items.map((item) => (
          <div key={item.label} className="certificate-card__item">
            <span className="certificate-card__label">{item.label}</span>
            <span className="certificate-card__value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
