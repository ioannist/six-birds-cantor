import { useEffect, useState } from "react";
import { useAppStore } from "../app/store";
import { loadT0View, loadT1View, CONTINUOUS_WITNESS_IDS } from "../data/loadData";
import type { ContinuousWitnessId } from "../data/loadData";
import type { T0View, T1View } from "../data/types";

// T0 components
import T0ClassMap from "../components/t0/T0ClassMap";
import PressureObjectCard from "../components/t0/PressureObjectCard";
import ShellMarkerLegend from "../components/t0/ShellMarkerLegend";
import ClaimSafeAnnotationList from "../components/t0/ClaimSafeAnnotationList";

// T1 components
import FixedPointStrataPanel from "../components/t1/FixedPointStrataPanel";
import SaturationCard from "../components/t1/SaturationCard";
import P4FromP5EventList from "../components/t1/P4FromP5EventList";
import PackagingIdentityPanel from "../components/t1/PackagingIdentityPanel";

import Badge from "../components/ui/Badge";

type ViewTab = "t0" | "t1";

function witnessIdToShort(id: string): ContinuousWitnessId {
  const short = id.replace("generated.", "");
  if (CONTINUOUS_WITNESS_IDS.includes(short as ContinuousWitnessId)) {
    return short as ContinuousWitnessId;
  }
  return CONTINUOUS_WITNESS_IDS[0];
}

function T0Content({ data }: { data: T0View }) {
  return (
    <div className="t0-layout" data-testid="t0-content">
      <div className="t0-object-map" data-testid="t0-object-map">
        <h3>T0 Object Map</h3>
        <code>{data.t0_object_map.map_id}</code>
        <p className="t0-object-map__desc">{data.t0_object_map.description}</p>
      </div>

      <T0ClassMap
        coreClassId={data.core_class_id}
        shellStable={data.shell_stable}
        theoremlets={data.theoremlets}
      />

      {data.pressure_object && (
        <PressureObjectCard pressure={data.pressure_object} />
      )}

      {data.shell_uniform_bounds && data.pressure_object && (
        <ShellMarkerLegend
          bounds={data.shell_uniform_bounds}
          shellExitCount={data.pressure_object.shell_exit_count}
          allPrimitivesActive={data.pressure_object.all_six_primitives_active}
        />
      )}

      <ClaimSafeAnnotationList claimBindings={data.claim_bindings} />

      <div className="t0-comparison" data-testid="t1-comparison">
        <h3>
          T1 Comparison <Badge variant="support" label="comparison only" />
        </h3>
        <div className="t0-comparison__grid">
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Object identity</span>
            <span className="t0-comparison__value">
              {data.t1_comparison.object_identity_verdict.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Factorization</span>
            <span className="t0-comparison__value">
              {data.t1_comparison.factorization_verdict.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Macro-admissibility</span>
            <span className="t0-comparison__value">
              {data.t1_comparison.macro_admissibility_verdict.replace(/_/g, " ")}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function T1Content({ data }: { data: T1View }) {
  return (
    <div className="t1-layout" data-testid="t1-content">
      <div className="t1-panel" data-testid="t1-object-map">
        <h3>T1 Completion Object</h3>
        <code style={{ color: "var(--color-t1)" }}>{data.extended_object_map.map_id}</code>
        <p className="t1-panel__detail-label">{data.extended_object_map.description}</p>
        <div className="t1-panel__metric-row" style={{ marginTop: "var(--space-sm)" }}>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Theory</span>
            <span className="t1-panel__metric-value" style={{ color: "var(--color-t1)", fontSize: "0.78rem" }}>
              {data.theory_id.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Kernel dim</span>
            <span className="t1-panel__metric-value">{data.completion_config.kernel_dim}</span>
          </div>
          <div className="t1-panel__metric">
            <span className="t1-panel__metric-label">Initial dists</span>
            <span className="t1-panel__metric-value">{data.completion_config.initial_distribution_count}</span>
          </div>
        </div>
      </div>

      <FixedPointStrataPanel strata={data.fixed_point_strata} />
      <SaturationCard saturation={data.saturation} />
      <P4FromP5EventList events={data.p4_from_p5_events} />
      <PackagingIdentityPanel changes={data.packaging_identity_changes} />

      <div className="t0-comparison" data-testid="t0-comparison">
        <h3>
          T0 Comparison <Badge variant="support" label="comparison only" />
        </h3>
        <div className="t0-comparison__grid">
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Base theory</span>
            <span className="t0-comparison__value">
              {data.t0_comparison.base_theory_id.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Object identity</span>
            <span className="t0-comparison__value">
              {data.t0_comparison.object_identity_verdict.replace(/_/g, " ")}
            </span>
          </div>
          <div className="t0-comparison__item">
            <span className="t0-comparison__label">Macro-admissibility</span>
            <span className="t0-comparison__value">
              {data.t0_comparison.macro_admissibility_verdict.replace(/_/g, " ")}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function T0VsT1Page() {
  const witnessId = useAppStore((s) => s.selectedWitnessId);
  const shortId = witnessIdToShort(witnessId);

  const [tab, setTab] = useState<ViewTab>("t0");
  const [t0Data, setT0Data] = useState<T0View | null>(null);
  const [t1Data, setT1Data] = useState<T1View | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([loadT0View(shortId), loadT1View(shortId)])
      .then(([t0, t1]) => {
        setT0Data(t0);
        setT1Data(t1);
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
        <h1>T0 vs T1</h1>
        <p>Loading data for {shortId}...</p>
      </section>
    );
  }

  if (error || !t0Data || !t1Data) {
    return (
      <section>
        <h1>T0 vs T1</h1>
        <p className="error" role="alert">{error ?? "No data available"}</p>
      </section>
    );
  }

  return (
    <section data-testid="t0-vs-t1-page">
      <h1>T0 vs T1</h1>
      <p className="page-subtitle">
        Witness: <code>{shortId}</code>
      </p>

      <div className="view-toggle" data-testid="view-toggle">
        <button
          className={`view-toggle__btn${tab === "t0" ? " view-toggle__btn--active" : ""}`}
          onClick={() => setTab("t0")}
          style={tab === "t0" ? { borderColor: "var(--color-t0)", color: "var(--color-t0)" } : undefined}
        >
          T0 Object
        </button>
        <button
          className={`view-toggle__btn${tab === "t1" ? " view-toggle__btn--active" : ""}`}
          onClick={() => setTab("t1")}
          style={tab === "t1" ? { borderColor: "var(--color-t1)", color: "var(--color-t1)" } : undefined}
        >
          T1 Object
        </button>
      </div>

      {tab === "t0" && <T0Content data={t0Data} />}
      {tab === "t1" && <T1Content data={t1Data} />}
    </section>
  );
}
