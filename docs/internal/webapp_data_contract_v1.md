# Web App Data Contract v1

## What the web app may consume

The web app is a **read-only**, static, data-driven React workspace.
It loads frozen JSON exports produced by `scripts/export_webapp_data.py` and displays them.
It must **never** perform theorem inference, proof verification, or claim derivation in the browser.

## Versioned data root

All exported datasets live under:

```
apps/cantor-web/public/data/v1/
```

The `v1` prefix is the contract version. A future schema-breaking change would use `v2/`.

## Dataset inventory

| File                    | Description                                      |
|-------------------------|--------------------------------------------------|
| `index.json`            | Manifest of all exported datasets                |
| `theorem-package.json`  | Minimal web-facing theorem package               |
| `claim-ledger.json`     | Claim IDs, statuses, and allowed paper uses      |
| `traceability.json`     | Theoremlet dependency/evidence/assumption links  |
| `figure-manifest.json`  | Figure/table manifest with claim bindings        |
| `witnesses.json`        | Witness family associations and artifact refs    |
| `continuous/<id>.json`  | Continuous substrate trajectory per witness       |

### Continuous trajectory datasets

Stored under `public/data/v1/continuous/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `timeline[]`: per-step records (variation, tau, budget, lens, packaging, action_weights, primitive_activity)
- `kernel_snapshots[]`: full kernel matrix every 10 steps (compact representation)
- `config`: seed, kernel_dim, steps
- `total_steps`, `kernel_snapshot_interval`

### T0 cocycle object datasets

Stored under `public/data/v1/t0/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel_t0.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell_t0.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `theory_id`: base theory ID (`T0_cocycle_pressure_theory`)
- `core_class_id`: shell-stable class ID
- `t0_object_map`: T0 cocycle descriptor quotient map
- `theoremlets[]`: T0-scoped theoremlets only (lawfulness + cocycle pressure)
- `claim_bindings[]`: allowed claims and figure bindings
- `pressure_object`: cocycle pressure closure data (fekete gap, profiles, bounds)
- `shell_uniform_bounds`: shell stability bounds
- `t1_comparison`: comparison-only T1 verdicts (explicitly scoped as `comparison_only`)

### T1 completion/fixed-point datasets

Stored under `public/data/v1/t1/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel_t1.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell_t1.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `theory_id`: extended theory ID (`T1_hybrid_cocycle_plus_completion_theory`)
- `extended_object_map`: T1 packaged object map
- `completion_config`: tau values, lens states, initial distribution count
- `fixed_point_strata`: distinct count and signatures
- `saturation`: panel summaries, saturated panel count
- `run_summaries[]`: per-run completion status, iterations, residual, macro-admissibility
- `p4_from_p5_events[]`: lens feedback events triggered by packaging
- `packaging_identity_changes[]`: packaging name/score/group changes across lens states
- `t0_comparison`: comparison-only T0 verdicts (explicitly scoped as `comparison_only`)

### Extension certificate datasets

Stored under `public/data/v1/extension/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel_extension.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell_extension.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `base_theory_id`, `extended_theory_id`: T0 and T1 theory IDs
- `base_object_map`, `extended_object_map`: both object maps
- `factorization_test`: factor_through_T0, non_factorization_rate, multiple_T1_strata_per_T0_class
- `verdicts`: factorization, object_identity, saturation, forcing, macro_admissibility
- `saturation_summary`, `forcing_summary`, `macro_admissibility_summary`: certificate counts
- `completion_summary`: distinct strata, fixed-point/cycle/nonconvergent run counts
- `scope`: always `audited_shell_only`
- `theoremlet`: strict theory extension theoremlet with allowed claim IDs
- `claim_binding`: allowed claim and figure bindings

### Conditional disintegration datasets

Stored under `public/data/v1/disintegration/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel_disintegration.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell_disintegration.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `selected_consequence_object`: the closed consequence type (weighted package-conditioned pressure gap)
- `t0_pressure`: global T0 pressure summary
- `descriptor_summaries[]`: per-lens/tau gap and closure-deficit data
- `config_summary`: min gap, descriptor count, macro-admissibility summary
- `shell_stability`: gap bounded on both witnesses, macro failure alignment
- `rejected_routes`: stratumwise (rejected) and KL deficit (support-only) with reasons
- `theoremlet`: conditional pressure disintegration theoremlet with allowed claim IDs
- `scope`: always `audited_shell_only`

### Annotation policy dataset

Stored at `public/data/v1/policy/annotation_policy.json`.

Contains:
- `paper_core_positioning`: level3 core on audited shell
- `core_claim_ids[]`: allowed core theorem claims
- `support_only_claim_ids[]`: support-only diagnostics
- `reserve_claim_ids[]`: reserve/stretch routes
- `nonclaim_ids[]`: explicit non-claims
- `scope_guards[]`: scope boundaries (audited shell only, etc.)
- `per_theoremlet_bindings[]`: allowed/forbidden claim IDs per theoremlet
- `claim_classifications`: per-claim status and paper-use classification
- `phrases_to_avoid[]`: claim-unsafe phrases

The annotation resolver in the app must use this policy to classify, filter, and badge all claim references.

### Primitive knockout datasets

Stored under `public/data/v1/knockouts/`. One file per frozen witness:

| File | Witness |
|------|---------|
| `continuous_full_loop_kernel_knockouts.json` | `generated.continuous_full_loop_kernel` |
| `continuous_full_loop_kernel_shell_knockouts.json` | `generated.continuous_full_loop_kernel_shell` |

Each file contains:
- `full_loop`: reference metrics (lens/packaging/tau switches, budget/tau range, mean variation, closure defect proxy)
- `knockouts[]`: 6 entries (no_P1 through no_P6), each with material_degradation flag, reasons, defect proxy, and summary metrics
- `theoremlet`: lawfulness theoremlet with allowed claim IDs
- `scope`: always `audited_shell_only`

## Core IDs and linking rules

All IDs are **stable strings already present in the frozen internal package**.
The app may resolve these cross-references:

- `theoremlet_id` → claim via `claim_id` in `claim-ledger.json`
- `theoremlet_id` → figures via `figure_ids` in `traceability.json` claim bindings
- `theoremlet_id` → witnesses via `witness_families` in `witnesses.json`
- `figure_id` → supported theoremlets via `supports_theoremlets` in `figure-manifest.json`

The app must not synthesize IDs, infer missing links, or create derived claim objects.

## Claim-safety requirements

- All visible claims must bind to exported IDs from the frozen package.
- Nonclaim and reserve entries are exported so the app can display scope boundaries.
- The app must not promote `reserve_only` or `nonclaim_only` entries to core status.
- `support_only` claims must be visually distinguished from `core_claim` entries.

## What the web app must not infer

- Theorem truth or falsity
- Proof correctness
- Claim status changes
- New theoremlet–claim bindings not in the exported data
- Any broader-class or shell-general scope beyond what is explicitly exported

## Export/update flow

1. Run `make web-export-data` (calls `python scripts/export_webapp_data.py`)
2. Exported JSON lands in `apps/cantor-web/public/data/v1/`
3. Run `make web-build` to bundle the app with fresh data
4. The app loads data at runtime via `fetch()` from the `/data/v1/` path
