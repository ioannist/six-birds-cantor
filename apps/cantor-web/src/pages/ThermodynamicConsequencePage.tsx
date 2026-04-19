import { useEffect, useState } from "react";
import { useAppStore } from "../app/store";
import { loadDisintegrationView, CONTINUOUS_WITNESS_IDS } from "../data/loadData";
import type { ContinuousWitnessId } from "../data/loadData";
import type { DisintegrationView } from "../data/types";
import GlobalPressureCard from "../components/disintegration/GlobalPressureCard";
import PressureGapPanel from "../components/disintegration/PressureGapPanel";
import ShellStabilityCard from "../components/disintegration/ShellStabilityCard";
import RejectedRouteNotice from "../components/disintegration/RejectedRouteNotice";
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

export default function ThermodynamicConsequencePage() {
  const witnessId = useAppStore((s) => s.selectedWitnessId);
  const shortId = witnessIdToShort(witnessId);

  const [data, setData] = useState<DisintegrationView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { policy } = useAnnotationPolicy();

  useEffect(() => {
    setLoading(true);
    setError(null);
    loadDisintegrationView(shortId)
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
        <h1>Thermodynamic consequence</h1>
        <p>Loading disintegration data for {shortId}...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section>
        <h1>Thermodynamic consequence</h1>
        <p className="error" role="alert">{error ?? "No data available"}</p>
      </section>
    );
  }

  return (
    <section data-testid="disintegration-page">
      <h1>Thermodynamic consequence</h1>

      <div className="extension-scope-banner" data-testid="scope-banner">
        <Badge variant="nonclaim" label="audited shell only" />
        <span>All claims on this page are scoped to the audited shell.</span>
      </div>

      <p className="page-subtitle">
        Witness: <code>{data.witness_id}</code> | Consequence:{" "}
        <code>{data.selected_consequence_object.replace(/_/g, " ")}</code>
      </p>

      <div className="disintegration-intro" data-testid="consequence-object">
        <h3>Consequence Object</h3>
        <p>
          The closed thermodynamic consequence is the{" "}
          <strong>weighted package-conditioned pressure gap</strong> — a
          global-to-conditional decomposition of the T0 pressure. This is{" "}
          <em>not</em> a direct stratumwise root-separation claim.
        </p>
        <div className="t1-panel__metric-row" style={{ marginTop: "var(--space-sm)" }}>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Decision</span>
            <span className="t1-panel__metric-value" style={{ color: "var(--color-closed)" }}>
              {data.decision.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Supported</span>
            <span className="t1-panel__metric-value" style={{ color: data.config_summary.disintegration_supported ? "var(--color-closed)" : "var(--color-nonclaim)" }}>
              {data.config_summary.disintegration_supported ? "Yes" : "No"}
            </span>
          </div>
        </div>
      </div>

      {data.t0_pressure && (
        <GlobalPressureCard
          pressureRoute={data.t0_pressure.pressure_route}
          feketeGapProxy={data.t0_pressure.fekete_gap_proxy}
          profiles={data.t0_pressure.pressure_profiles}
        />
      )}

      <PressureGapPanel
        descriptors={data.descriptor_summaries}
        minGap={data.config_summary.min_gap}
      />

      <ShellStabilityCard
        gapBoundedOnBoth={data.shell_stability.gap_bounded_on_both_witnesses}
        macroFailureAligns={data.shell_stability.macro_failure_aligns}
        workingRoute={data.shell_stability.working_route}
      />

      <RejectedRouteNotice routes={data.rejected_routes} />

      {data.theoremlet && (
        <div className="extension-claim" data-testid="disintegration-claim">
          <h3>Allowed Claim</h3>
          {policy ? (
            <ClaimBadge claimId={data.theoremlet.theoremlet_id} category={resolveClaim(data.theoremlet.theoremlet_id, policy).category} />
          ) : (
            <Badge variant="closed" label={data.theoremlet.theoremlet_id.replace(/_/g, " ")} />
          )}
          <span className="extension-claim__status">
            {data.theoremlet.status.replace(/_/g, " ")}
          </span>
          {data.claim_binding && data.claim_binding.figure_ids.length > 0 && (
            <div className="extension-claim__figures">
              Figures: {data.claim_binding.figure_ids.map((id) => (
                <code key={id}>{id}</code>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
