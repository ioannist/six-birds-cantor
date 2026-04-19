import { useEffect, useState, useMemo } from "react";
import { useAppStore } from "../app/store";
import {
  loadContinuousTrajectory,
  CONTINUOUS_WITNESS_IDS,
} from "../data/loadData";
import type { ContinuousWitnessId } from "../data/loadData";
import type { ContinuousTrajectory, KernelSnapshot } from "../data/types";
import KernelHeatmap from "../components/continuous/KernelHeatmap";
import TimelineScrubber from "../components/continuous/TimelineScrubber";
import MetricSparkline from "../components/continuous/MetricSparkline";
import PrimitiveActivityRow from "../components/continuous/PrimitiveActivityRow";
import StateCard from "../components/continuous/StateCard";

function witnessIdToShort(id: string): ContinuousWitnessId {
  const short = id.replace("generated.", "");
  if (CONTINUOUS_WITNESS_IDS.includes(short as ContinuousWitnessId)) {
    return short as ContinuousWitnessId;
  }
  return CONTINUOUS_WITNESS_IDS[0];
}

export default function LiveSubstratePage() {
  const witnessId = useAppStore((s) => s.selectedWitnessId);
  const timeIndex = useAppStore((s) => s.selectedTimeIndex);
  const setTimeIndex = useAppStore((s) => s.setTimeIndex);

  const [data, setData] = useState<ContinuousTrajectory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const shortId = witnessIdToShort(witnessId);

  useEffect(() => {
    setLoading(true);
    setError(null);
    loadContinuousTrajectory(shortId)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [shortId]);

  // Clamp time index to valid range when data changes
  useEffect(() => {
    if (data && timeIndex >= data.total_steps) {
      setTimeIndex(data.total_steps - 1);
    }
  }, [data, timeIndex, setTimeIndex]);

  const maxStep = data ? data.total_steps - 1 : 0;
  const step = data ? data.timeline[Math.min(timeIndex, maxStep)] : null;

  // Find nearest kernel snapshot
  const kernelSnapshot: KernelSnapshot | null = useMemo(() => {
    if (!data) return null;
    const snapshots = data.kernel_snapshots;
    let best = snapshots[0] ?? null;
    for (const s of snapshots) {
      if (
        Math.abs(s.step - (timeIndex + 1)) <
        Math.abs(best.step - (timeIndex + 1))
      ) {
        best = s;
      }
    }
    return best;
  }, [data, timeIndex]);

  // Precompute full series
  const budgetSeries = useMemo(
    () => data?.timeline.map((s) => s.budget) ?? [],
    [data],
  );
  const tauSeries = useMemo(
    () => data?.timeline.map((s) => s.tau) ?? [],
    [data],
  );
  const variationSeries = useMemo(
    () => data?.timeline.map((s) => s.variation) ?? [],
    [data],
  );

  if (loading) {
    return (
      <section>
        <h1>Live substrate</h1>
        <p>Loading trajectory for {shortId}...</p>
      </section>
    );
  }

  if (error || !data || !step) {
    return (
      <section>
        <h1>Live substrate</h1>
        <p className="error" role="alert">
          {error ?? "No data available"}
        </p>
      </section>
    );
  }

  return (
    <section data-testid="live-substrate-page">
      <h1>Live substrate</h1>
      <p className="page-subtitle">
        Witness: <code>{data.witness_id}</code> | {data.config.kernel_dim}x
        {data.config.kernel_dim} kernel | {data.total_steps} steps | seed{" "}
        {data.config.seed}
      </p>

      <TimelineScrubber
        min={0}
        max={maxStep}
        value={timeIndex}
        onChange={setTimeIndex}
      />

      <div className="substrate-grid">
        <div className="substrate-grid__left">
          <KernelHeatmap
            snapshot={kernelSnapshot}
            dim={data.config.kernel_dim}
          />

          <div className="state-cards">
            <StateCard
              label="Active lens"
              value={step.lens.replace(/_/g, " ")}
              color="var(--color-p4)"
            />
            <StateCard
              label="Active packaging"
              value={step.packaging.replace(/_/g, " ")}
              color="var(--color-p5)"
            />
            <StateCard
              label="Budget"
              value={step.budget.toFixed(4)}
              color="var(--color-p6)"
            />
            <StateCard
              label="Tau"
              value={step.tau.toFixed(4)}
              color="var(--color-p3)"
            />
          </div>
        </div>

        <div className="substrate-grid__right">
          <MetricSparkline
            label="Budget"
            data={budgetSeries}
            currentIndex={timeIndex}
            color="var(--color-p6)"
          />
          <MetricSparkline
            label="Tau"
            data={tauSeries}
            currentIndex={timeIndex}
            color="var(--color-p3)"
          />
          <MetricSparkline
            label="Variation"
            data={variationSeries}
            currentIndex={timeIndex}
            color="var(--color-accent)"
          />
        </div>
      </div>

      <PrimitiveActivityRow
        actionWeights={step.action_weights}
        primitiveActivity={step.primitive_activity}
      />
    </section>
  );
}
