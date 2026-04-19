import type { ResolvedClaim } from "../../claims/resolveAnnotations";
import ClaimBadge from "./ClaimBadge";

interface ClaimChipListProps {
  claims: ResolvedClaim[];
  testId?: string;
}

export default function ClaimChipList({ claims, testId }: ClaimChipListProps) {
  if (claims.length === 0) return null;

  // Group by category
  const core = claims.filter((c) => c.category === "core");
  const support = claims.filter((c) => c.category === "support");
  const reserve = claims.filter((c) => c.category === "reserve");
  const nonclaim = claims.filter((c) => c.category === "nonclaim");

  return (
    <div className="claim-chip-list" data-testid={testId ?? "claim-chip-list"}>
      {core.length > 0 && (
        <div className="claim-chip-list__group">
          {core.map((c) => (
            <ClaimBadge key={c.claimId} claimId={c.claimId} category="core" />
          ))}
        </div>
      )}
      {support.length > 0 && (
        <div className="claim-chip-list__group claim-chip-list__group--support" data-testid="support-claims">
          {support.map((c) => (
            <ClaimBadge key={c.claimId} claimId={c.claimId} category="support" />
          ))}
        </div>
      )}
      {reserve.length > 0 && (
        <div className="claim-chip-list__group claim-chip-list__group--reserve" data-testid="reserve-claims">
          {reserve.map((c) => (
            <ClaimBadge key={c.claimId} claimId={c.claimId} category="reserve" />
          ))}
        </div>
      )}
      {nonclaim.length > 0 && (
        <div className="claim-chip-list__group claim-chip-list__group--nonclaim" data-testid="nonclaim-items">
          {nonclaim.map((c) => (
            <ClaimBadge key={c.claimId} claimId={c.claimId} category="nonclaim" />
          ))}
        </div>
      )}
    </div>
  );
}
