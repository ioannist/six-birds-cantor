import type { AnnotationPolicy } from "../data/types";

export type ClaimCategory = "core" | "support" | "reserve" | "nonclaim" | "unknown";

export interface ResolvedClaim {
  claimId: string;
  category: ClaimCategory;
  label: string;
  allowed: boolean;
  paperUse: string;
}

export function classifyClaim(
  claimId: string,
  policy: AnnotationPolicy,
): ClaimCategory {
  if (policy.core_claim_ids.includes(claimId)) return "core";
  if (policy.support_only_claim_ids.includes(claimId)) return "support";
  if (policy.reserve_claim_ids.includes(claimId)) return "reserve";
  if (policy.nonclaim_ids.includes(claimId)) return "nonclaim";
  return "unknown";
}

export function resolveClaim(
  claimId: string,
  policy: AnnotationPolicy,
): ResolvedClaim {
  const category = classifyClaim(claimId, policy);
  const classification = policy.claim_classifications[claimId];
  return {
    claimId,
    category,
    label: claimId.replace(/_/g, " "),
    allowed: category === "core" || category === "support",
    paperUse: classification?.allowed_final_paper_use ?? "unknown",
  };
}

export function isAllowedOnPanel(
  claimId: string,
  theoremletId: string,
  policy: AnnotationPolicy,
): boolean {
  const binding = policy.per_theoremlet_bindings.find(
    (b) => b.theoremlet_id === theoremletId,
  );
  if (!binding) return false;
  if (binding.forbidden_claim_ids.includes(claimId)) return false;
  return binding.allowed_claim_ids.includes(claimId);
}

export function filterAllowedClaims(
  claimIds: string[],
  policy: AnnotationPolicy,
): ResolvedClaim[] {
  return claimIds
    .map((id) => resolveClaim(id, policy))
    .filter((r) => r.category !== "unknown");
}

export function getCoreClaimsOnly(
  policy: AnnotationPolicy,
): ResolvedClaim[] {
  return policy.core_claim_ids.map((id) => resolveClaim(id, policy));
}

export function getScopeGuards(policy: AnnotationPolicy): string[] {
  return policy.scope_guards;
}
