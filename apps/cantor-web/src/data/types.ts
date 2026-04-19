/** Web data contract types for cantor-web v1 datasets. */

export interface DatasetEntry {
  name: string;
  path: string;
}

export interface DataIndex {
  schema_version: string;
  generated_at_utc: string;
  datasets: DatasetEntry[];
}

export interface TheoremletSummary {
  theoremlet_id: string;
  status: string;
  class_scope: string;
  note: string;
}

export interface CanonicalHybridSummary {
  object_id: string;
  base_theory_id: string;
  extended_theory_id: string;
  decision: string;
  object_identity_verdict: string;
  factorization_verdict: string;
}

export interface ClaimPosture {
  core_positioning: string;
  core_claim_ids: string[];
  support_only_claim_ids: string[];
  reserve_claim_ids: string[];
  nonclaim_ids: string[];
  manuscript_posture: string;
  phrases_to_avoid: string[];
}

export interface TheoremPackage {
  schema_version: string;
  package_id: string;
  paper_core_positioning: string;
  canonical_object_id: string;
  core_class_id: string;
  selected_routes: Record<string, string>;
  included_theoremlets: TheoremletSummary[];
  nonclaims: string[];
  reserve_routes: string[];
  canonical_hybrid_object: CanonicalHybridSummary;
  claim_posture: ClaimPosture;
}

export interface ClaimEntry {
  claim_id: string;
  claim_status: string;
  claim_type: string;
  allowed_final_paper_use: string;
  object_scope: string;
  class_scope: string;
  statement_short: string;
}

export interface ClaimLedger {
  schema_version: string;
  ledger_id: string;
  claim_counts: Record<string, number>;
  claims: ClaimEntry[];
}

export interface TraceabilityTheoremlet {
  theoremlet_id: string;
  status: string;
  class_scope: string;
  assumptions_used: string[];
  dependency_paths: string[];
  evidence_paths: string[];
  allowed_claim_ids: string[];
  forbidden_claim_ids: string[];
}

export interface ClaimBinding {
  theoremlet_id: string;
  allowed_claim_ids: string[];
  forbidden_claim_ids: string[];
  figure_ids: string[];
}

export interface ScopeFirewall {
  core_closed_claims: string[];
  explicit_nonclaims: string[];
  reserve_routes: string[];
  support_only_claims: string[];
  scope_boundaries: string[];
}

export interface Traceability {
  schema_version: string;
  matrix_id: string;
  paper_core_positioning: string;
  decision: string;
  theoremlets: TraceabilityTheoremlet[];
  claim_bindings: ClaimBinding[];
  scope_firewall: ScopeFirewall;
}

export interface FigureEntry {
  figure_id: string;
  title_short: string;
  role: string;
  status: string;
  supports_theoremlets: string[];
  allowed_claim_ids: string[];
  source_artifacts: string[];
}

export interface FigureManifest {
  schema_version: string;
  manifest_id: string;
  figures: FigureEntry[];
  allowed_claim_bindings: unknown[];
  nonclaim_bindings: unknown[];
}

export interface WitnessEntry {
  theoremlet_id: string;
  witness_families: string[];
  evidence_paths: string[];
  dependency_paths: string[];
}

export interface Witnesses {
  schema_version: string;
  package_witness_families: string[];
  witnesses: WitnessEntry[];
}

// --- Continuous trajectory types ---

export interface ContinuousTimelineStep {
  step: number;
  variation: number;
  tau: number;
  budget: number;
  lens: string;
  packaging: string;
  action_weights: Record<string, number>;
  primitive_activity: Record<string, boolean>;
}

export interface KernelSnapshot {
  step: number;
  kernel: number[][];
}

export interface ContinuousTrajectory {
  schema_version: string;
  witness_id: string;
  config: {
    steps: number;
    kernel_dim: number;
    seed: number;
  };
  total_steps: number;
  kernel_snapshot_interval: number;
  kernel_snapshots: KernelSnapshot[];
  timeline: ContinuousTimelineStep[];
}

// --- T0 cocycle object view types ---

export interface T0ObjectMap {
  map_id: string;
  description: string;
}

export interface PressureProfile {
  gap_proxy: number;
  pressure_proxy: number;
  sign: number;
}

export interface T0PressureObject {
  pressure_route: string;
  observable_family: string;
  fekete_gap_proxy: number;
  growth_bound_proxy: number;
  pressure_profiles: Record<string, PressureProfile>;
  budget_range: [number, number];
  tau_range: [number, number];
  shell_exit_count: number;
  min_lens_margin: number;
  min_packaging_margin: number;
  all_six_primitives_active: boolean;
}

export interface T0Theoremlet {
  theoremlet_id: string;
  status: string;
  class_scope: string;
  assumptions_used: string[];
  allowed_claim_ids: string[];
}

export interface T0ClaimBinding {
  theoremlet_id: string;
  allowed_claim_ids: string[];
  figure_ids: string[];
}

export interface ShellUniformBounds {
  budget_range: [number, number];
  tau_range: [number, number];
  lens_margin_min: number;
  packaging_margin_min: number;
}

export interface T1Comparison {
  _scope: "comparison_only";
  object_identity_verdict: string;
  factorization_verdict: string;
  macro_admissibility_verdict: string;
}

export interface T0View {
  schema_version: string;
  witness_id: string;
  theory_id: string;
  core_class_id: string;
  shell_stable: boolean;
  t0_object_map: T0ObjectMap;
  theoremlets: T0Theoremlet[];
  claim_bindings: T0ClaimBinding[];
  pressure_object: T0PressureObject | null;
  shell_uniform_bounds: ShellUniformBounds | null;
  t1_comparison: T1Comparison;
}

// --- T1 completion/fixed-point view types ---

export interface T1ExtendedObjectMap {
  map_id: string;
  description: string;
}

export interface T1CompletionConfig {
  tau_values: number[];
  lens_states: string[];
  initial_distribution_count: number;
  kernel_dim: number;
}

export interface T1FixedPointStrata {
  distinct_count: number;
  signatures: number[][];
}

export interface T1SaturationPanel {
  tau: number;
  lens_state: string;
  distinct_fixed_points: number;
  saturated: boolean;
}

export interface T1Saturation {
  saturated: boolean;
  saturated_panel_count: number;
  total_panels: number;
  panel_summaries: T1SaturationPanel[];
}

export interface T1RunSummary {
  tau: number;
  lens_state: string;
  initial_index: number;
  status: string;
  iterations: number;
  residual: number;
  final_signature_hash: number;
  macro_admissible: boolean;
}

export interface T1P4FromP5Event {
  tau: number;
  from_lens: string;
  to_lens: string;
  trigger_status: string;
  package_count: number;
}

export interface T1PackagingIdentityChange {
  tau: number;
  lens_state: string;
  packaging_name: string;
  packaging_score: number;
  group_count: number;
}

export interface T0Comparison {
  _scope: "comparison_only";
  base_theory_id: string;
  base_object_map_id: string;
  object_identity_verdict: string;
  macro_admissibility_verdict: string;
}

export interface T1View {
  schema_version: string;
  witness_id: string;
  theory_id: string;
  extended_object_map: T1ExtendedObjectMap;
  completion_config: T1CompletionConfig;
  fixed_point_strata: T1FixedPointStrata;
  saturation: T1Saturation;
  run_summaries: T1RunSummary[];
  p4_from_p5_events: T1P4FromP5Event[];
  packaging_identity_changes: T1PackagingIdentityChange[];
  t0_comparison: T0Comparison;
}

// --- Extension certificate types ---

export interface FactorizationTest {
  factor_through_T0: boolean;
  non_factorization_rate: number;
  multiple_T1_strata_per_T0_class: number;
  note: string;
}

export interface ExtensionVerdicts {
  factorization: string;
  object_identity: string;
  saturation: string;
  forcing: string;
  macro_admissibility: string;
}

export interface ExtensionView {
  schema_version: string;
  witness_id: string;
  base_theory_id: string;
  extended_theory_id: string;
  base_object_map: T0ObjectMap;
  extended_object_map: T1ExtendedObjectMap;
  factorization_test: FactorizationTest;
  verdicts: ExtensionVerdicts;
  saturation_summary: {
    saturated: boolean;
    saturated_panel_count: number;
    total_panels: number;
  };
  forcing_summary: {
    p4_from_p5_event_count: number;
    total_runs: number;
  };
  macro_admissibility_summary: {
    obstruction_count: number;
    total_runs: number;
  };
  completion_summary: {
    distinct_strata: number;
    fixed_point_runs: number;
    cycle_runs: number;
    nonconvergent_runs: number;
  };
  scope: string;
  theoremlet: {
    theoremlet_id: string;
    status: string;
    class_scope: string;
    allowed_claim_ids: string[];
  } | null;
  claim_binding: {
    theoremlet_id: string;
    allowed_claim_ids: string[];
    figure_ids: string[];
  } | null;
}

// --- Conditional disintegration types ---

export interface DisintegrationDescriptor {
  lens_state: string;
  tau: number;
  gap_bounded_away_from_zero: boolean;
  closure_deficit_proxy: number;
  pressure_gap: Record<string, { gap: number; t0_pressure: number; weighted_conditioned_pressure: number }>;
  fiber_count: number;
}

export interface RejectedRoute {
  status: string;
  reason: string;
}

export interface DisintegrationView {
  schema_version: string;
  witness_id: string;
  base_theory_id: string;
  extended_theory_id: string;
  selected_consequence_object: string;
  decision: string;
  scope: string;
  t0_pressure: {
    pressure_route: string;
    fekete_gap_proxy: number;
    pressure_profiles: Record<string, PressureProfile>;
  } | null;
  descriptor_summaries: DisintegrationDescriptor[];
  config_summary: {
    disintegration_supported: boolean;
    min_gap: number | null;
    max_closure_deficit_proxy: number | null;
    descriptor_count: number;
    macro_admissibility_summary: { admissible_count: number; inadmissible_count: number } | null;
  };
  shell_stability: {
    gap_bounded_on_both_witnesses: boolean;
    macro_failure_aligns: boolean;
    working_route: string;
  };
  rejected_routes: {
    direct_stratumwise_separation: RejectedRoute;
    exact_kl_closure_deficit: RejectedRoute;
  };
  theoremlet: {
    theoremlet_id: string;
    status: string;
    class_scope: string;
    allowed_claim_ids: string[];
  } | null;
  claim_binding: {
    theoremlet_id: string;
    allowed_claim_ids: string[];
    figure_ids: string[];
  } | null;
}

// --- Primitive knockout types ---

export interface KnockoutSummaryMetrics {
  lens_switch_count: number;
  packaging_switch_count: number;
  tau_switch_count: number;
  budget_min: number;
  budget_max: number;
  tau_min: number;
  tau_max: number;
  mean_variation: number;
}

export interface KnockoutEntry {
  removed: string;
  material_degradation: boolean;
  material_reasons: string[];
  closure_defect_proxy: number;
  summary: KnockoutSummaryMetrics;
}

export interface FullLoopMetrics extends KnockoutSummaryMetrics {
  closure_defect_proxy: number;
}

export interface KnockoutsView {
  schema_version: string;
  witness_id: string;
  scope: string;
  full_loop: FullLoopMetrics;
  knockouts: KnockoutEntry[];
  theoremlet: {
    theoremlet_id: string;
    status: string;
    allowed_claim_ids: string[];
  } | null;
  claim_binding: {
    theoremlet_id: string;
    allowed_claim_ids: string[];
    figure_ids: string[];
  } | null;
}

// --- Annotation policy types ---

export interface ClaimClassification {
  status: string;
  allowed_final_paper_use: string;
  claim_type: string;
}

export interface TheoremletBinding {
  theoremlet_id: string;
  allowed_claim_ids: string[];
  forbidden_claim_ids: string[];
}

export interface AnnotationPolicy {
  schema_version: string;
  paper_core_positioning: string;
  core_claim_ids: string[];
  support_only_claim_ids: string[];
  reserve_claim_ids: string[];
  nonclaim_ids: string[];
  scope_guards: string[];
  per_theoremlet_bindings: TheoremletBinding[];
  claim_classifications: Record<string, ClaimClassification>;
  phrases_to_avoid: string[];
}
