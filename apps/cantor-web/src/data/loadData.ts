import type {
  DataIndex,
  TheoremPackage,
  ClaimLedger,
  Traceability,
  FigureManifest,
  Witnesses,
  ContinuousTrajectory,
  T0View,
  T1View,
  ExtensionView,
  DisintegrationView,
  KnockoutsView,
  AnnotationPolicy,
} from "./types";

const DATA_ROOT = "/data/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${DATA_ROOT}/${path}`);
  if (!res.ok) {
    throw new Error(`Failed to load ${path}: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function loadIndex(): Promise<DataIndex> {
  return fetchJson<DataIndex>("index.json");
}

export async function loadTheoremPackage(): Promise<TheoremPackage> {
  return fetchJson<TheoremPackage>("theorem-package.json");
}

export async function loadClaimLedger(): Promise<ClaimLedger> {
  return fetchJson<ClaimLedger>("claim-ledger.json");
}

export async function loadTraceability(): Promise<Traceability> {
  return fetchJson<Traceability>("traceability.json");
}

export async function loadFigureManifest(): Promise<FigureManifest> {
  return fetchJson<FigureManifest>("figure-manifest.json");
}

export async function loadWitnesses(): Promise<Witnesses> {
  return fetchJson<Witnesses>("witnesses.json");
}

export type DatasetName =
  | "theorem-package"
  | "claim-ledger"
  | "traceability"
  | "figure-manifest"
  | "witnesses";

const LOADERS: Record<DatasetName, () => Promise<unknown>> = {
  "theorem-package": loadTheoremPackage,
  "claim-ledger": loadClaimLedger,
  traceability: loadTraceability,
  "figure-manifest": loadFigureManifest,
  witnesses: loadWitnesses,
};

export async function loadDataset(name: DatasetName): Promise<unknown> {
  const loader = LOADERS[name];
  if (!loader) {
    throw new Error(`Unknown dataset: ${name}`);
  }
  return loader();
}

export const CONTINUOUS_WITNESS_IDS = [
  "continuous_full_loop_kernel",
  "continuous_full_loop_kernel_shell",
] as const;

export type ContinuousWitnessId = (typeof CONTINUOUS_WITNESS_IDS)[number];

export async function loadContinuousTrajectory(
  witnessId: ContinuousWitnessId,
): Promise<ContinuousTrajectory> {
  return fetchJson<ContinuousTrajectory>(`continuous/${witnessId}.json`);
}

export async function loadT0View(
  witnessId: ContinuousWitnessId,
): Promise<T0View> {
  return fetchJson<T0View>(`t0/${witnessId}_t0.json`);
}

export async function loadT1View(
  witnessId: ContinuousWitnessId,
): Promise<T1View> {
  return fetchJson<T1View>(`t1/${witnessId}_t1.json`);
}

export async function loadExtensionView(
  witnessId: ContinuousWitnessId,
): Promise<ExtensionView> {
  return fetchJson<ExtensionView>(`extension/${witnessId}_extension.json`);
}

export async function loadDisintegrationView(
  witnessId: ContinuousWitnessId,
): Promise<DisintegrationView> {
  return fetchJson<DisintegrationView>(`disintegration/${witnessId}_disintegration.json`);
}

export async function loadKnockoutsView(
  witnessId: ContinuousWitnessId,
): Promise<KnockoutsView> {
  return fetchJson<KnockoutsView>(`knockouts/${witnessId}_knockouts.json`);
}

export async function loadAnnotationPolicy(): Promise<AnnotationPolicy> {
  return fetchJson<AnnotationPolicy>("policy/annotation_policy.json");
}
