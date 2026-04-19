import Badge from "../ui/Badge";
import type { T0ClaimBinding } from "../../data/types";

interface ClaimSafeAnnotationListProps {
  claimBindings: T0ClaimBinding[];
}

export default function ClaimSafeAnnotationList({
  claimBindings,
}: ClaimSafeAnnotationListProps) {
  return (
    <div className="claim-annotations" data-testid="claim-annotations">
      <h3>Allowed Claim Annotations</h3>
      <ul className="claim-annotations__list">
        {claimBindings.map((b) => (
          <li key={b.theoremlet_id} className="claim-annotations__item">
            <div>
              <Badge variant="closed" label={b.theoremlet_id.replace(/_/g, " ")} />
            </div>
            <div className="claim-annotations__details">
              <span className="claim-annotations__label">Claims:</span>{" "}
              {b.allowed_claim_ids.map((id) => (
                <code key={id}>{id}</code>
              ))}
            </div>
            {b.figure_ids.length > 0 && (
              <div className="claim-annotations__details">
                <span className="claim-annotations__label">Figures:</span>{" "}
                {b.figure_ids.map((id) => (
                  <code key={id}>{id}</code>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
