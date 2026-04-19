import { useAnnotationPolicy } from "../claims/useAnnotationPolicy";
import { filterAllowedClaims, getScopeGuards } from "../claims/resolveAnnotations";
import ClaimChipList from "../components/claims/ClaimChipList";
import ScopeGuardBanner from "../components/claims/ScopeGuardBanner";

export default function ClaimScopePage() {
  const { policy, loading } = useAnnotationPolicy();

  if (loading || !policy) {
    return (
      <section>
        <h1>Claim scope</h1>
        <p>Loading annotation policy...</p>
      </section>
    );
  }

  const allClaimIds = [
    ...policy.core_claim_ids,
    ...policy.support_only_claim_ids,
    ...policy.reserve_claim_ids,
    ...policy.nonclaim_ids,
  ];
  const resolved = filterAllowedClaims(allClaimIds, policy);

  return (
    <section data-testid="claim-scope-page">
      <h1>Claim scope</h1>
      <p className="page-subtitle">
        Positioning: <code>{policy.paper_core_positioning}</code>
      </p>

      <ScopeGuardBanner guards={getScopeGuards(policy)} />

      <div className="claim-scope-section">
        <h3>All Claims by Category</h3>
        <ClaimChipList claims={resolved} testId="all-claims" />
      </div>

      <div className="claim-scope-section">
        <h3>Phrases to Avoid</h3>
        <ul style={{ margin: 0, paddingLeft: "var(--space-md)" }}>
          {policy.phrases_to_avoid.map((p) => (
            <li key={p} style={{ fontSize: "0.82rem", color: "var(--color-nonclaim)" }}>
              {p}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
