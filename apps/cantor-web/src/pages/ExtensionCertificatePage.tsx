import { useEffect, useState } from "react";
import { useAppStore } from "../app/store";
import { loadExtensionView, CONTINUOUS_WITNESS_IDS } from "../data/loadData";
import type { ContinuousWitnessId } from "../data/loadData";
import type { ExtensionView } from "../data/types";
import FailedFactorizationDiagram from "../components/extension/FailedFactorizationDiagram";
import VerdictGrid from "../components/extension/VerdictGrid";
import CertificateCard from "../components/extension/CertificateCard";
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

export default function ExtensionCertificatePage() {
  const witnessId = useAppStore((s) => s.selectedWitnessId);
  const shortId = witnessIdToShort(witnessId);

  const [data, setData] = useState<ExtensionView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { policy } = useAnnotationPolicy();

  useEffect(() => {
    setLoading(true);
    setError(null);
    loadExtensionView(shortId)
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
        <h1>Extension certificate</h1>
        <p>Loading extension data for {shortId}...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section>
        <h1>Extension certificate</h1>
        <p className="error" role="alert">{error ?? "No data available"}</p>
      </section>
    );
  }

  return (
    <section data-testid="extension-page">
      <h1>Extension certificate</h1>

      <div className="extension-scope-banner" data-testid="scope-banner">
        <Badge variant="nonclaim" label="audited shell only" />
        <span>All claims on this page are scoped to the audited shell. No broader-class or shell-general claims.</span>
      </div>

      <p className="page-subtitle">
        Witness: <code>{data.witness_id}</code> |{" "}
        <span style={{ color: "var(--color-t0)" }}>{data.base_theory_id.replace(/_/g, " ")}</span>
        {" → "}
        <span style={{ color: "var(--color-t1)" }}>{data.extended_theory_id.replace(/_/g, " ")}</span>
      </p>

      <FailedFactorizationDiagram
        baseMap={data.base_object_map}
        extendedMap={data.extended_object_map}
        test={data.factorization_test}
        baseTheoryId={data.base_theory_id}
        extendedTheoryId={data.extended_theory_id}
      />

      <VerdictGrid verdicts={data.verdicts} />

      <div className="extension-certificates">
        <CertificateCard
          title="Saturation Certificate"
          testId="saturation-certificate"
          items={[
            { label: "Saturated", value: data.saturation_summary.saturated ? "Yes" : "No" },
            { label: "Saturated panels", value: `${data.saturation_summary.saturated_panel_count} / ${data.saturation_summary.total_panels}` },
          ]}
        />
        <CertificateCard
          title="Forcing Certificate (P4←P5)"
          testId="forcing-certificate"
          items={[
            { label: "P4←P5 events", value: data.forcing_summary.p4_from_p5_event_count },
            { label: "Total runs", value: data.forcing_summary.total_runs },
            { label: "Event rate", value: `${((data.forcing_summary.p4_from_p5_event_count / Math.max(1, data.forcing_summary.total_runs)) * 100).toFixed(1)}%` },
          ]}
        />
        <CertificateCard
          title="Macro-admissibility Obstruction"
          testId="macro-obstruction"
          items={[
            { label: "Obstructions", value: data.macro_admissibility_summary.obstruction_count },
            { label: "Total runs", value: data.macro_admissibility_summary.total_runs },
            { label: "Obstruction rate", value: `${((data.macro_admissibility_summary.obstruction_count / Math.max(1, data.macro_admissibility_summary.total_runs)) * 100).toFixed(1)}%` },
          ]}
        />
        <CertificateCard
          title="Completion Summary"
          testId="completion-summary"
          items={[
            { label: "Distinct strata", value: data.completion_summary.distinct_strata },
            { label: "Fixed-point runs", value: data.completion_summary.fixed_point_runs },
            { label: "Cycle runs", value: data.completion_summary.cycle_runs },
            { label: "Nonconvergent", value: data.completion_summary.nonconvergent_runs },
          ]}
        />
      </div>

      {data.theoremlet && (
        <div className="extension-claim" data-testid="extension-claim">
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
