import { useEffect, useState } from "react";
import { useAppStore } from "../app/store";
import { loadKnockoutsView, CONTINUOUS_WITNESS_IDS } from "../data/loadData";
import type { ContinuousWitnessId } from "../data/loadData";
import type { KnockoutsView } from "../data/types";
import KnockoutComparisonGrid from "../components/knockouts/KnockoutComparisonGrid";
import Badge from "../components/ui/Badge";
import { useAnnotationPolicy } from "../claims/useAnnotationPolicy";
import { resolveClaim } from "../claims/resolveAnnotations";
import ClaimBadge from "../components/claims/ClaimBadge";

function witnessIdToShort(id: string): ContinuousWitnessId {
  const short = id.replace("generated.", "");
  if (CONTINUOUS_WITNESS_IDS.includes(short as ContinuousWitnessId)) {
    return short as ContinuousWitnessId;
  }
  return CONTINUOUS_WITNESS_IDS[0];
}

export default function PrimitiveKnockoutsPage() {
  const witnessId = useAppStore((s) => s.selectedWitnessId);
  const shortId = witnessIdToShort(witnessId);

  const [data, setData] = useState<KnockoutsView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { policy } = useAnnotationPolicy();

  useEffect(() => {
    setLoading(true);
    setError(null);
    loadKnockoutsView(shortId)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [shortId]);

  if (loading) {
    return (
      <section>
        <h1>Primitive knockouts</h1>
        <p>Loading knockout data for {shortId}...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section>
        <h1>Primitive knockouts</h1>
        <p className="error" role="alert">{error ?? "No data available"}</p>
      </section>
    );
  }

  const degradedCount = data.knockouts.filter((k) => k.material_degradation).length;

  return (
    <section data-testid="knockouts-page">
      <h1>Primitive knockouts</h1>

      <div className="extension-scope-banner">
        <Badge variant="nonclaim" label="audited shell only" />
        <span>Six-primitive closure evidence on the audited shell.</span>
      </div>

      <p className="page-subtitle">
        Witness: <code>{data.witness_id}</code> |{" "}
        <strong>{degradedCount}/6</strong> knockouts show material degradation
      </p>

      <KnockoutComparisonGrid
        fullLoop={data.full_loop}
        knockouts={data.knockouts}
      />

      {data.theoremlet && (
        <div className="extension-claim" data-testid="knockout-claim" style={{ marginTop: "var(--space-md)" }}>
          <h3>Allowed Claim</h3>
          {policy ? (
            <ClaimBadge claimId={data.theoremlet.theoremlet_id} category={resolveClaim(data.theoremlet.theoremlet_id, policy).category} />
          ) : (
            <Badge variant="closed" label={data.theoremlet.theoremlet_id.replace(/_/g, " ")} />
          )}
          <span className="extension-claim__status">
            {data.theoremlet.status.replace(/_/g, " ")}
          </span>
        </div>
      )}
    </section>
  );
}
