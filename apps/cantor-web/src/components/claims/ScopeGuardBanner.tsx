import Badge from "../ui/Badge";

interface ScopeGuardBannerProps {
  guards: string[];
}

export default function ScopeGuardBanner({ guards }: ScopeGuardBannerProps) {
  if (guards.length === 0) return null;

  return (
    <div className="scope-guard-banner" data-testid="scope-guard-banner">
      <Badge variant="nonclaim" label="scope firewall" />
      <ul className="scope-guard-banner__list">
        {guards.map((g) => (
          <li key={g}>{g}</li>
        ))}
      </ul>
    </div>
  );
}
