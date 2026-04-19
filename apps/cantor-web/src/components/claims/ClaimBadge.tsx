import type { ClaimCategory } from "../../claims/resolveAnnotations";
import Badge from "../ui/Badge";
import type { BadgeVariant } from "../../theme/tokens";

const CATEGORY_TO_VARIANT: Record<ClaimCategory, BadgeVariant> = {
  core: "closed",
  support: "support",
  reserve: "reserve",
  nonclaim: "nonclaim",
  unknown: "nonclaim",
};

const CATEGORY_LABELS: Record<ClaimCategory, string> = {
  core: "",
  support: "support only",
  reserve: "reserve",
  nonclaim: "non-claim",
  unknown: "unknown",
};

interface ClaimBadgeProps {
  claimId: string;
  category: ClaimCategory;
  showCategory?: boolean;
}

export default function ClaimBadge({ claimId, category, showCategory = true }: ClaimBadgeProps) {
  const variant = CATEGORY_TO_VARIANT[category];
  const label = claimId.replace(/_/g, " ");
  const suffix = showCategory && category !== "core" ? ` (${CATEGORY_LABELS[category]})` : "";

  return (
    <span data-testid={`claim-badge-${category}`} data-claim-id={claimId}>
      <Badge variant={variant} label={`${label}${suffix}`} />
    </span>
  );
}
