from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _normalize_row(row: list[float]) -> list[float]:
    clipped = [max(0.0, float(x)) for x in row]
    total = sum(clipped)
    if total <= 0.0:
        n = len(clipped)
        return [1.0 / n for _ in range(n)]
    return [x / total for x in clipped]


def _normalize_kernel(kernel: list[list[float]]) -> list[list[float]]:
    return [_normalize_row(row) for row in kernel]


def _copy_kernel(kernel: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in kernel]


def _kernel_signature(kernel: list[list[float]], digits: int = 4) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(round(x, digits) for x in row) for row in kernel)


def _frobenius_delta(a: list[list[float]], b: list[list[float]]) -> float:
    return math.sqrt(sum((x - y) ** 2 for row_a, row_b in zip(a, b) for x, y in zip(row_a, row_b)))


def _row_sums(kernel: list[list[float]]) -> list[float]:
    return [sum(row) for row in kernel]


def _col_sums(kernel: list[list[float]]) -> list[float]:
    n = len(kernel)
    return [sum(kernel[i][j] for i in range(n)) for j in range(n)]


def _transpose(kernel: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*kernel)]


def _stationary_distribution(kernel: list[list[float]], steps: int = 80) -> list[float]:
    """Finite power-iteration estimate, with no stationarity certificate.

    Periodic/reducible kernels may not converge. Exact rational completion
    certificates use stationary_distribution_exact in exact_completion.
    """
    n = len(kernel)
    if n == 0:
        return []
    vec = [1.0 / n for _ in range(n)]
    transposed = _transpose(kernel)
    for _ in range(steps):
        nxt = [sum(a * b for a, b in zip(row, vec)) for row in transposed]
        total = sum(nxt)
        if total <= 0.0:
            return [1.0 / n for _ in range(n)]
        nxt = [x / total for x in nxt]
        if max(abs(a - b) for a, b in zip(nxt, vec)) <= 1e-12:
            return nxt
        vec = nxt
    return vec


def _entropy(vec: list[float]) -> float:
    total = sum(vec)
    if total <= 0.0:
        return 0.0
    out = 0.0
    for value in vec:
        if value > 0.0:
            p = value / total
            out -= p * math.log(p)
    return out


def _softmax(scores: list[float], temperature: float = 1.0) -> list[float]:
    if not scores:
        return []
    temp = max(temperature, 1e-6)
    mx = max(scores)
    exps = [math.exp((s - mx) / temp) for s in scores]
    total = sum(exps)
    if total <= 0.0:
        return [1.0 / len(scores) for _ in scores]
    return [x / total for x in exps]


def _weighted_choice(rng: random.Random, labels: list[str], weights: list[float]) -> str:
    if not labels:
        raise ValueError("labels may not be empty")
    clean = [max(0.0, float(w)) for w in weights]
    total = sum(clean)
    if total <= 0.0:
        return labels[0]
    pick = rng.random() * total
    cumulative = 0.0
    for label, weight in zip(labels, clean):
        cumulative += weight
        if pick <= cumulative:
            return label
    return labels[-1]


def _initial_kernel(n: int, rng: random.Random) -> list[list[float]]:
    if n < 4:
        raise ValueError("kernel dimension must be at least 4")
    kernel: list[list[float]] = []
    core_left = max(2, n // 4)
    core_right = max(2, n // 3)
    for i in range(n):
        row: list[float] = []
        for j in range(n):
            dist = abs(i - j)
            same_block = (i < core_left and j < core_left) or (i >= n - core_right and j >= n - core_right)
            mid_band = abs(i - j) <= 2
            base = 0.02 + 0.08 * math.exp(-dist / 4.0)
            if same_block:
                base += 0.12
            if mid_band:
                base += 0.04
            if j == (i + 1) % n:
                base += 0.03
            if j == i:
                base += 0.05
            base += 0.01 * rng.random()
            row.append(base)
        kernel.append(_normalize_row(row))
    return kernel


def _packaging_template_from_groups(n: int, groups: list[list[int]]) -> list[list[float]]:
    support = [[0.0 for _ in range(n)] for _ in range(n)]
    for group in groups:
        if not group:
            continue
        group_weight = 1.0 / len(group)
        for i in group:
            for j in group:
                support[i][j] += group_weight
    return _normalize_kernel(support)


def _package_core_indices(stationary: list[float], kernel: list[list[float]], quantile: float = 0.72) -> list[int]:
    if not stationary:
        return []
    ordered = sorted(stationary)
    threshold = ordered[int(max(0, min(len(ordered) - 1, round((len(ordered) - 1) * quantile))))]
    diag = [kernel[i][i] for i in range(len(kernel))]
    return [i for i, (p, d) in enumerate(zip(stationary, diag)) if p >= threshold or d >= 0.18]


def _row_similarity_score(kernel: list[list[float]]) -> tuple[float, list[list[int]]]:
    n = len(kernel)
    if n == 0:
        return 0.0, []
    norms = [math.sqrt(sum(v * v for v in row)) or 1.0 for row in kernel]
    sims: list[tuple[float, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            dot = sum(a * b for a, b in zip(kernel[i], kernel[j]))
            sim = dot / (norms[i] * norms[j])
            sims.append((sim, i, j))
    sims.sort(reverse=True)
    groups: list[list[int]] = []
    used: set[int] = set()
    for _, i, j in sims[: max(3, n // 2)]:
        if i in used and j in used:
            continue
        if i not in used:
            groups.append([i])
            used.add(i)
        if j not in used:
            groups.append([j])
            used.add(j)
    for i in range(n):
        if i not in used:
            groups.append([i])
    score = sum(sim for sim, _, _ in sims[: max(1, n // 2)]) / max(1, min(len(sims), max(1, n // 2)))
    return score, groups


def _phase_wave(phase: int, period: int, offset: float = 0.0) -> float:
    if period <= 0:
        return 0.0
    angle = (2.0 * math.pi * ((phase % period) / period)) + offset
    return math.sin(angle)


@dataclass
class PilotParameters:
    lens_hysteresis: float = 0.025
    packaging_hysteresis: float = 0.018
    budget_income_scale: float = 1.0
    budget_cost_scale: float = 1.0
    tau_initial: float = 1.0
    action_temperature_bias: float = 0.0
    lens_temperature_shift: float = 0.0

    def __post_init__(self) -> None:
        if any(not math.isfinite(value) for value in vars(self).values()):
            raise ValueError("pilot parameters must be finite")
        if (self.lens_hysteresis < 0 or self.packaging_hysteresis < 0
                or self.budget_income_scale < 0 or self.budget_cost_scale < 0
                or self.tau_initial <= 0):
            raise ValueError("hysteresis and budget scales must be nonnegative; tau must be positive")


@dataclass
class KernelSubstrateState:
    kernel: list[list[float]]
    tau: float
    budget: float
    income: float
    phase: int
    protocol_state: str
    active_lens: str
    active_packaging: str
    action_weights: list[float]
    informant_cache: dict[str, Any] = field(default_factory=dict)
    invalidation_counts: dict[str, int] = field(default_factory=lambda: {"kernel": 0, "lens": 0, "packaging": 0, "phase": 0})
    lens_switch_count: int = 0
    packaging_switch_count: int = 0
    tau_switch_count: int = 0
    step_index: int = 0
    primitive_activity: dict[str, bool] = field(default_factory=lambda: {p: True for p in PRIMITIVES})
    previous_kernel: list[list[float]] = field(default_factory=list)
    previous_signature: tuple[tuple[float, ...], ...] | None = None
    kernel_variation_history: list[float] = field(default_factory=list)
    lens_history: list[str] = field(default_factory=list)
    packaging_history: list[str] = field(default_factory=list)
    tau_history: list[float] = field(default_factory=list)
    budget_history: list[float] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    pilot_parameters: PilotParameters = field(default_factory=PilotParameters)

    def snapshot(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "tau": self.tau,
            "budget": self.budget,
            "income": self.income,
            "phase": self.phase,
            "protocol_state": self.protocol_state,
            "active_lens": self.active_lens,
            "active_packaging": self.active_packaging,
            "kernel_signature": _kernel_signature(self.kernel),
        }


def build_initial_state(
    n: int = 16,
    seed: int = 0,
    pilot_parameters: PilotParameters | None = None,
) -> KernelSubstrateState:
    rng = random.Random(seed)
    kernel = _initial_kernel(n, rng)
    pilot_parameters = pilot_parameters or PilotParameters()
    return KernelSubstrateState(
        kernel=kernel,
        tau=pilot_parameters.tau_initial,
        budget=2.5,
        income=0.0,
        phase=0,
        protocol_state="boot",
        active_lens="spectral_lens",
        active_packaging="partition_cluster_packaging",
        action_weights=[1.0, 1.0, 1.0],
        previous_kernel=_copy_kernel(kernel),
        previous_signature=_kernel_signature(kernel),
        pilot_parameters=pilot_parameters,
    )


def refresh_informants(
    state: KernelSubstrateState,
    primitive_activity: dict[str, bool],
    rng: random.Random | None = None,
) -> dict[str, Any]:
    rng = rng or random.Random(0)
    signature = _kernel_signature(state.kernel)
    changed = state.previous_signature != signature
    if changed:
        state.invalidation_counts["kernel"] += 1
        state.cache_misses += 1
        state.informant_cache = {}
    else:
        state.cache_hits += 1
    state.previous_signature = signature

    stationary = _stationary_distribution(state.kernel)
    row_sums = _row_sums(state.kernel)
    col_sums = _col_sums(state.kernel)
    diagonal = [state.kernel[i][i] for i in range(len(state.kernel))]
    imbalance = [abs(r - c) for r, c in zip(row_sums, col_sums)]
    support = [max(0.0, min(1.0, 0.5 * (p + d))) for p, d in zip(stationary, diagonal)]
    if not primitive_activity.get("P4", True):
        support = [0.5 * x for x in support]

    informants = {
        "stationary": stationary,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "diagonal": diagonal,
        "imbalance": imbalance,
        "support": support,
        "signature": signature,
        "phase": state.phase,
        "budget": state.budget,
        "tau": state.tau,
        "random_probe": rng.random(),
    }
    state.informant_cache = informants
    return informants


def compute_p4_lenses(
    state: KernelSubstrateState,
    informants: dict[str, Any],
    primitive_activity: dict[str, bool] | None = None,
) -> list[dict[str, Any]]:
    primitive_activity = primitive_activity or state.primitive_activity
    kernel = state.kernel
    stationary = informants["stationary"]
    row_sums = informants["row_sums"]
    col_sums = informants["col_sums"]
    imbalance = informants["imbalance"]
    phase_signal = 0.5 + 0.5 * _phase_wave(state.phase, 12)
    budget_signal = 1.0 - min(1.0, state.budget / 12.0)
    tau_signal = min(1.0, state.tau / 4.0)
    phase_bucket = state.phase % 12
    spectral_window = 0.42 if phase_bucket in {0, 1, 2, 3} else -0.08
    similarity_window = 0.42 if phase_bucket in {4, 5, 6, 7} else -0.08
    audit_window = 0.42 if phase_bucket in {8, 9, 10, 11} else -0.08

    spectral_score = (1.0 - _entropy(stationary) / max(math.log(len(stationary) or 2), 1e-9))
    spectral_score = 0.78 * spectral_score * (0.82 + 0.18 * phase_signal)
    spectral_score += 0.05 * (1.0 - tau_signal)
    spectral_score += spectral_window
    if not primitive_activity.get("P4", True):
        spectral_score *= 0.25

    similarity_score, groups = _row_similarity_score(kernel)
    similarity_score = max(0.0, 0.32 * similarity_score)
    similarity_score += 0.10 * (0.5 + 0.5 * _phase_wave(state.phase, 6, offset=math.pi / 4.0))
    similarity_score += 0.08 * budget_signal
    similarity_score += similarity_window
    spread = max(row_sums) - min(row_sums) if row_sums else 0.0
    flow_score = 1.0 / (1.0 + sum(imbalance))
    quantile_score = (spread + max(informants["diagonal"]) - min(informants["diagonal"])) / max(1.0, len(kernel))
    quantile_score += 0.06 * tau_signal + 0.05 * (state.phase % 4) / 3.0
    audit_score = 0.38 * (0.5 * flow_score + 0.5 * quantile_score)
    audit_score += audit_window
    if not primitive_activity.get("P4", True):
        audit_score *= 0.25

    lens = [
        {
            "name": "spectral_lens",
            "score": spectral_score,
            "details": {
                "stationary_entropy": _entropy(stationary),
                "stationary_peak": max(stationary) if stationary else 0.0,
            },
        },
        {
            "name": "row_similarity_cluster_lens",
            "score": similarity_score,
            "details": {
                "cluster_count": len(groups),
                "mean_row_sum": sum(row_sums) / len(row_sums) if row_sums else 0.0,
            },
        },
        {
            "name": "audit_flow_quantile_lens",
            "score": audit_score,
            "details": {
                "flow_balance": flow_score,
                "row_sum_spread": spread,
                "diagonal_spread": (max(informants["diagonal"]) - min(informants["diagonal"])) if kernel else 0.0,
            },
        },
    ]
    return lens


def _build_packaging_groups_from_similarity(kernel: list[list[float]]) -> list[list[int]]:
    _, groups = _row_similarity_score(kernel)
    if not groups:
        return []
    groups = [group for group in groups if group]
    if len(groups) > 6:
        # compress into contiguous clusters
        ordered = sorted({idx for group in groups for idx in group})
        return [ordered[: len(ordered) // 2], ordered[len(ordered) // 2 :]]
    return groups


def compute_p5_packagings(
    state: KernelSubstrateState,
    informants: dict[str, Any],
    selected_lens: dict[str, Any],
    primitive_activity: dict[str, bool] | None = None,
) -> list[dict[str, Any]]:
    primitive_activity = primitive_activity or state.primitive_activity
    kernel = state.kernel
    n = len(kernel)
    stationary = informants["stationary"]
    support = informants["support"]
    row_sums = informants["row_sums"]
    lens_name = selected_lens["name"]
    lens_weight = float(selected_lens["score"])
    if not primitive_activity.get("P5", True):
        return []

    phase_signal = 0.5 + 0.5 * _phase_wave(state.phase, 12, offset=math.pi / 3.0)
    tau_signal = min(1.0, state.tau / 4.0)
    budget_signal = 1.0 - min(1.0, state.budget / 12.0)
    protocol_signal = {
        "refresh": 0.25,
        "audit": 0.55,
        "packaging": 0.85,
        "settle": 0.40,
    }.get(state.protocol_state, 0.35)
    phase_bucket = state.phase % 12
    cluster_window = 0.22 if phase_bucket in {0, 1, 2, 3} else 0.0
    return_window = 0.22 if phase_bucket in {4, 5, 6, 7} else 0.0
    budget_window = 0.22 if phase_bucket in {8, 9, 10, 11} else 0.0

    groups = _build_packaging_groups_from_similarity(kernel)
    if not groups:
        groups = [list(range(n // 2)), list(range(n // 2, n))]

    core_indices = _package_core_indices(stationary, kernel)
    if not core_indices:
        core_indices = list(range(max(2, n // 4)))

    budget_sorted = sorted(range(n), key=lambda i: (support[i], -row_sums[i]), reverse=True)
    budget_core = budget_sorted[: max(2, n // 4)]

    cluster_packaging = {
        "name": "partition_cluster_packaging",
        "score": min(
            1.0,
            0.28 + 0.32 * lens_weight + 0.18 * (len(groups) / max(1, n)) + 0.14 * phase_signal + cluster_window,
        ),
        "groups": groups,
        "core_indices": sorted({idx for group in groups for idx in group}),
        "support": support,
        "leakage": sum(abs(support[i] - support[j]) for i in range(n) for j in range(n) if (i in core_indices) != (j in core_indices)) / max(1, n * n),
        "producers": ["P5<-P4"],
        "details": {"lens_name": lens_name},
    }
    recurrence_packaging = {
        "name": "return_core_packaging",
        "score": min(
            1.0,
            0.32
            + 0.42 * (sum(stationary[i] for i in core_indices) / max(1, len(core_indices)))
            + 0.12 * lens_weight
            + 0.12 * tau_signal
            + return_window,
        ),
        "groups": [core_indices, [i for i in range(n) if i not in core_indices]],
        "core_indices": core_indices,
        "support": support,
        "leakage": sum(1.0 - kernel[i][j] for i in core_indices for j in core_indices) / max(1, len(core_indices) ** 2),
        "producers": ["P5<-P3"],
        "details": {"stationary_core_mass": sum(stationary[i] for i in core_indices)},
    }
    budget_packaging = {
        "name": "budget_audit_packaging",
        "score": min(
            1.0,
            0.24
            + 0.28 * (sum(support[i] for i in budget_core) / max(1, len(budget_core)))
            + 0.10 * (state.budget / 5.0)
            + 0.18 * budget_signal
            + 0.10 * protocol_signal
            + budget_window,
        ),
        "groups": [budget_core, [i for i in range(n) if i not in budget_core]],
        "core_indices": budget_core,
        "support": support,
        "leakage": sum(abs(row_sums[i] - row_sums[j]) for i in budget_core for j in budget_core) / max(1, len(budget_core) ** 2),
        "producers": ["P5<-P6"],
        "details": {"budget": state.budget, "row_sum_bias": sum(row_sums[i] for i in budget_core)},
    }
    return [cluster_packaging, recurrence_packaging, budget_packaging]


def _select_competing(
    current_name: str,
    candidates: list[dict[str, Any]],
    hysteresis: float,
    rng: random.Random,
) -> dict[str, Any]:
    if not candidates:
        raise ValueError("candidates must be non-empty")
    ordered = sorted(candidates, key=lambda c: c["score"], reverse=True)
    best = ordered[0]
    current = next((cand for cand in candidates if cand["name"] == current_name), None)
    if current is not None and best["score"] - current["score"] <= hysteresis:
        # retain the incumbent unless the challenger is clearly better
        return current
    # soft stochastic tie-break among near-best candidates
    top_band = [cand for cand in ordered if best["score"] - cand["score"] <= max(hysteresis, 0.03)]
    if len(top_band) == 1:
        return best
    weights = _softmax([cand["score"] for cand in top_band], temperature=0.08 + 0.2 * rng.random())
    chosen_name = _weighted_choice(rng, [cand["name"] for cand in top_band], weights)
    return next(cand for cand in top_band if cand["name"] == chosen_name)


def _make_packaging_target(
    kernel: list[list[float]],
    packaging: dict[str, Any],
    lens: dict[str, Any],
) -> list[list[float]]:
    n = len(kernel)
    core = set(packaging["core_indices"])
    groups = packaging["groups"]
    target = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        row = [0.0 for _ in range(n)]
        if packaging["name"] == "partition_cluster_packaging":
            group = next((g for g in groups if i in g), [i])
            for j in range(n):
                if j in group:
                    row[j] = kernel[i][j] + 0.10
                else:
                    row[j] = 0.4 * kernel[i][j]
        elif packaging["name"] == "return_core_packaging":
            for j in range(n):
                if j in core:
                    row[j] = kernel[i][j] + (0.12 if i not in core else 0.08)
                else:
                    row[j] = 0.35 * kernel[i][j]
        else:
            for j in range(n):
                if j in core:
                    row[j] = kernel[i][j] + 0.07 + 0.03 * packaging["score"]
                else:
                    row[j] = 0.5 * kernel[i][j]
            if i in core:
                row[i] += 0.05
        # lens-aware shift for packaging competition
        if lens["name"] == "spectral_lens":
            row[i] += 0.02 * lens["score"]
        elif lens["name"] == "row_similarity_cluster_lens":
            row[i] += 0.03 * packaging["score"]
        else:
            row[i] += 0.01 * packaging["score"]
        target[i] = _normalize_row(row)
    return target


def apply_p1_rewrite(
    state: KernelSubstrateState,
    packaging: dict[str, Any] | None,
    lens: dict[str, Any],
    primitive_activity: dict[str, bool] | None = None,
) -> tuple[list[list[float]], dict[str, Any]]:
    primitive_activity = primitive_activity or state.primitive_activity
    if not primitive_activity.get("P1", True) or packaging is None:
        return _copy_kernel(state.kernel), {"applied": False, "target_distance": 0.0}
    target = _make_packaging_target(state.kernel, packaging, lens)
    eta = _clamp(0.08 + 0.05 * packaging["score"] + 0.02 * state.tau, 0.03, 0.18)
    new_kernel = []
    for row, targ in zip(state.kernel, target):
        mixed = [(1.0 - eta) * x + eta * y for x, y in zip(row, targ)]
        new_kernel.append(_normalize_row(mixed))
    distance = _frobenius_delta(state.kernel, target)
    return new_kernel, {"applied": True, "target_distance": distance, "eta": eta}


def apply_p2_gating(
    state: KernelSubstrateState,
    kernel: list[list[float]],
    packaging: dict[str, Any] | None,
    lens: dict[str, Any],
    informants: dict[str, Any],
    primitive_activity: dict[str, bool] | None = None,
) -> tuple[list[list[float]], dict[str, Any]]:
    primitive_activity = primitive_activity or state.primitive_activity
    if not primitive_activity.get("P2", True) or packaging is None:
        return _normalize_kernel(kernel), {"applied": False, "viability_mean": 1.0, "viability_min": 1.0}
    core = set(packaging["core_indices"])
    support = informants["support"]
    stationary = informants["stationary"]
    n = len(kernel)
    gated: list[list[float]] = []
    viabilities: list[float] = []
    for i, row in enumerate(kernel):
        core_bias = 1.0 if i in core else 0.4
        lens_bias = 0.2 + 0.8 * support[i]
        stationary_bias = 0.5 + 0.5 * stationary[i]
        viability = _clamp(core_bias * lens_bias * stationary_bias, 0.08, 1.0)
        viabilities.append(viability)
        gated_row = []
        for j, value in enumerate(row):
            support_bias = 1.0 if j in core else 0.55
            gated_row.append(value * math.sqrt(viability * support_bias))
        gated.append(_normalize_row(gated_row))
    # if a row becomes too thin, blend in a core-preserving fallback rather than freezing
    fallback_row = _normalize_row([0.8 if j in core else 0.2 for j in range(n)])
    for i, row in enumerate(gated):
        if viabilities[i] < 0.18:
            gated[i] = _normalize_row([0.65 * x + 0.35 * y for x, y in zip(row, fallback_row)])
    stats = {
        "applied": True,
        "viability_mean": sum(viabilities) / len(viabilities),
        "viability_min": min(viabilities),
        "viability_max": max(viabilities),
    }
    return gated, stats


def apply_p3_timescale_update(
    state: KernelSubstrateState,
    variation: float,
    lens: dict[str, Any],
    packaging: dict[str, Any] | None,
    primitive_activity: dict[str, bool] | None = None,
) -> dict[str, Any]:
    primitive_activity = primitive_activity or state.primitive_activity
    if not primitive_activity.get("P3", True):
        return {"applied": False, "tau": state.tau, "phase": state.phase, "protocol_state": state.protocol_state}
    switch_penalty = 0.0
    if len(state.lens_history) >= 2 and state.active_lens != state.lens_history[-2]:
        switch_penalty += 0.07
    if len(state.packaging_history) >= 2 and state.active_packaging != state.packaging_history[-2]:
        switch_penalty += 0.05
    stability = max(0.0, 0.12 - variation)
    tau_next = _clamp(state.tau + 0.11 * stability - 0.06 * variation - switch_penalty, 0.6, 4.0)
    phase_next = (state.phase + 1) % 12
    if phase_next in {0, 1, 2}:
        protocol_state = "refresh"
    elif phase_next in {3, 4, 5}:
        protocol_state = "audit"
    elif phase_next in {6, 7, 8}:
        protocol_state = "packaging"
    else:
        protocol_state = "settle"
    changed = abs(tau_next - state.tau) > 0.02
    if changed:
        state.tau_switch_count += 1
    state.phase = phase_next
    state.protocol_state = protocol_state
    state.tau = tau_next
    return {"applied": True, "tau": state.tau, "phase": state.phase, "protocol_state": state.protocol_state}


def apply_p6_budget_update(
    state: KernelSubstrateState,
    packaging: dict[str, Any] | None,
    lens: dict[str, Any],
    variation: float,
    primitive_activity: dict[str, bool] | None = None,
) -> dict[str, Any]:
    primitive_activity = primitive_activity or state.primitive_activity
    if not primitive_activity.get("P6", True):
        return {"applied": False, "budget": state.budget, "income": 0.0, "cost": 0.0, "temperature": 0.15}
    packaging_score = packaging["score"] if packaging is not None else 0.0
    lens_score = lens["score"]
    income = state.pilot_parameters.budget_income_scale * (
        0.24 * packaging_score + 0.12 * lens_score + 0.08 * max(0.0, 1.0 - variation)
    )
    cost = state.pilot_parameters.budget_cost_scale * (0.06 + 0.018 * state.phase + 0.04 * variation)
    if len(state.lens_history) >= 2 and state.active_lens != state.lens_history[-2]:
        cost += 0.03
    if len(state.packaging_history) >= 2 and state.active_packaging != state.packaging_history[-2]:
        cost += 0.03
    budget_next = _clamp(state.budget + income - cost, 0.0, 12.0)
    state.income = income
    state.budget = budget_next
    temperature = _clamp(0.42 - 0.02 * budget_next + 0.08 * variation, 0.08, 0.6)
    return {"applied": True, "budget": state.budget, "income": income, "cost": cost, "temperature": temperature}


def _default_role_flags(primitive_activity: dict[str, bool] | None) -> dict[str, bool]:
    flags = {p: True for p in PRIMITIVES}
    if primitive_activity:
        for primitive, active in primitive_activity.items():
            flags[str(primitive)] = bool(active)
    return flags


def _score_margin(candidates: list[dict[str, Any]]) -> float:
    scores = sorted((float(item["score"]) for item in candidates), reverse=True)
    return scores[0] - scores[1] if len(scores) >= 2 else 0.0


def step_substrate(
    state: KernelSubstrateState,
    rng: random.Random,
    primitive_activity: dict[str, bool] | None = None,
) -> dict[str, Any]:
    primitive_activity = _default_role_flags(primitive_activity or state.primitive_activity)
    state.primitive_activity = dict(primitive_activity)
    state.step_index += 1

    informants = refresh_informants(state, primitive_activity, rng)
    lenses = compute_p4_lenses(state, informants, primitive_activity)
    if primitive_activity.get("P4", True):
        lens_temperature = _clamp(
            0.18 + 0.03 * state.tau - 0.02 * state.budget + state.pilot_parameters.lens_temperature_shift,
            0.08,
            0.35,
        )
        lens_choice = _select_competing(
            state.active_lens,
            lenses,
            hysteresis=state.pilot_parameters.lens_hysteresis,
            rng=rng,
        )
    else:
        lens_choice = {
            "name": state.active_lens if state.active_lens in {l["name"] for l in lenses} else "spectral_lens",
            "score": 0.0,
            "details": {"disabled": True},
        }
        lens_temperature = 0.0
    if state.lens_history and lens_choice["name"] != state.active_lens:
        state.lens_switch_count += 1
        state.invalidation_counts["lens"] += 1
    state.active_lens = lens_choice["name"]
    state.lens_history.append(state.active_lens)

    packagings = compute_p5_packagings(state, informants, lens_choice, primitive_activity)
    if primitive_activity.get("P5", True) and packagings:
        packaging_choice = _select_competing(
            state.active_packaging,
            packagings,
            hysteresis=state.pilot_parameters.packaging_hysteresis + 0.01 * max(0.0, state.tau - 1.0),
            rng=rng,
        )
    else:
        packaging_choice = {
            "name": "fallback_uniform_packaging",
            "score": 0.0,
            "core_indices": list(range(max(1, len(state.kernel) // 4))),
            "groups": [list(range(len(state.kernel)))],
            "support": informants["support"],
            "leakage": 1.0,
            "producers": [],
            "details": {"disabled": not primitive_activity.get("P5", True)},
        }
    if state.packaging_history and packaging_choice["name"] != state.active_packaging:
        state.packaging_switch_count += 1
        state.invalidation_counts["packaging"] += 1
    state.active_packaging = packaging_choice["name"]
    state.packaging_history.append(state.active_packaging)

    kernel_after_p1, p1_info = apply_p1_rewrite(state, packaging_choice, lens_choice, primitive_activity)
    kernel_after_p2, p2_info = apply_p2_gating(state, kernel_after_p1, packaging_choice, lens_choice, informants, primitive_activity)

    variation = _frobenius_delta(state.kernel, kernel_after_p2)
    p3_info = apply_p3_timescale_update(state, variation, lens_choice, packaging_choice, primitive_activity)
    p6_info = apply_p6_budget_update(state, packaging_choice, lens_choice, variation, primitive_activity)

    if primitive_activity.get("P6", True):
        noise_scale = 0.0025 + 0.002 * min(1.0, max(0.0, p6_info["budget"] / 6.0))
        noisy = []
        for row in kernel_after_p2:
            noisy.append(
                _normalize_row(
                    [
                        max(0.0, value + rng.uniform(-noise_scale, noise_scale))
                        for value in row
                    ]
                )
            )
        kernel_after_p2 = noisy

    state.previous_kernel = _copy_kernel(state.kernel)
    state.kernel = _normalize_kernel(kernel_after_p2)
    if primitive_activity.get("P5", True) and packaging_choice["name"] == "fallback_uniform_packaging":
        state.invalidation_counts["packaging"] += 1
    if variation > 0.02:
        state.invalidation_counts["kernel"] += 1

    final_variation = _frobenius_delta(state.previous_kernel, state.kernel)
    state.kernel_variation_history.append(final_variation)
    state.tau_history.append(state.tau)
    state.budget_history.append(state.budget)

    if state.previous_signature is not None and _kernel_signature(state.previous_kernel) == _kernel_signature(state.kernel):
        state.cache_hits += 1
    else:
        state.cache_misses += 1

    primitive_scores = {
        "P1": p1_info["target_distance"],
        "P2": p2_info["viability_mean"],
        "P3": p3_info["tau"],
        "P4": lens_choice["score"],
        "P5": packaging_choice["score"],
        "P6": p6_info["income"],
    }
    if not primitive_activity.get("P1", True):
        primitive_scores["P1"] = 0.0
    if not primitive_activity.get("P2", True):
        primitive_scores["P2"] = 0.0
    if not primitive_activity.get("P3", True):
        primitive_scores["P3"] = 0.0
    if not primitive_activity.get("P4", True):
        primitive_scores["P4"] = 0.0
    if not primitive_activity.get("P5", True):
        primitive_scores["P5"] = 0.0
    if not primitive_activity.get("P6", True):
        primitive_scores["P6"] = 0.0

    state.action_weights = _softmax(
        list(primitive_scores.values()),
        temperature=0.35 + lens_temperature + state.pilot_parameters.action_temperature_bias,
    )

    return {
        "step": state.step_index,
        "selector_diagnostics": {
            "lens_margin": _score_margin(lenses),
            "packaging_margin": _score_margin(packagings),
        },
        "variation": final_variation,
        "lens": lens_choice,
        "packaging": packaging_choice,
        "p1": p1_info,
        "p2": p2_info,
        "p3": p3_info,
        "p6": p6_info,
        "action_weights": dict(zip(PRIMITIVES, state.action_weights)),
        "kernel_signature": _kernel_signature(state.kernel),
    }


def simulate_substrate(
    steps: int = 1000,
    n: int = 16,
    seed: int = 0,
    primitive_activity: dict[str, bool] | None = None,
    pilot_parameters: PilotParameters | None = None,
) -> dict[str, Any]:
    if steps < 1:
        raise ValueError("steps must be positive")
    rng = random.Random(seed)
    state = build_initial_state(n=n, seed=seed, pilot_parameters=pilot_parameters)
    state.primitive_activity = _default_role_flags(primitive_activity)
    trajectory: list[dict[str, Any]] = []
    for _ in range(steps):
        trajectory.append(step_substrate(state, rng, state.primitive_activity))

    return {
        "state": state,
        "trajectory": trajectory,
    }


def _completion_kernel_blend(kernel: list[list[float]], tau: float) -> list[list[float]]:
    n = len(kernel)
    if n == 0:
        return []
    alpha = _clamp(0.22 + 0.18 * min(1.0, tau / 3.0), 0.18, 0.78)
    eye = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    return _normalize_kernel(
        [
            [(1.0 - alpha) * eye[i][j] + alpha * kernel[i][j] for j in range(n)]
            for i in range(n)
        ]
    )


def _completion_packaging_from_lens(
    kernel: list[list[float]],
    tau: float,
    lens_state: str,
) -> dict[str, Any]:
    n = len(kernel)
    stationary = _stationary_distribution(kernel)
    support = [max(0.0, min(1.0, 0.5 * (p + kernel[i][i]))) for i, p in enumerate(stationary)]
    if lens_state == "spectral_lens":
        core = _package_core_indices(stationary, kernel)
        if not core:
            core = list(range(max(2, n // 4)))
        groups = [sorted(core), [i for i in range(n) if i not in core]]
        name = "completion_spectral_packaging"
    elif lens_state == "row_similarity_cluster_lens":
        _, groups = _row_similarity_score(kernel)
        groups = [group for group in groups if group]
        if not groups:
            groups = [list(range(n // 2)), list(range(n // 2, n))]
        name = "completion_cluster_packaging"
    else:
        budget_sorted = sorted(range(n), key=lambda i: (support[i], kernel[i][i]), reverse=True)
        core = budget_sorted[: max(2, n // 4)]
        groups = [sorted(core), [i for i in range(n) if i not in core]]
        name = "completion_audit_packaging"
    core_indices = sorted({idx for group in groups for idx in group})
    score = _clamp(
        0.34
        + 0.18 * len(groups) / max(1, n)
        + 0.12 * (sum(stationary[i] for i in core_indices) / max(1, len(core_indices)))
        + 0.08 * min(1.0, tau / 4.0),
        0.0,
        1.0,
    )
    return {
        "name": name,
        "score": score,
        "groups": groups,
        "core_indices": core_indices,
        "support": support,
        "producers": ["P5<-P4", "P5<-P3", "P5<-P6"],
        "details": {"lens_state": lens_state, "tau": tau},
    }


def _completion_initial_distributions(kernel: list[list[float]]) -> list[list[float]]:
    n = len(kernel)
    if n == 0:
        return []
    stationary = _stationary_distribution(kernel)
    uniform = [1.0 / n for _ in range(n)]
    core = _package_core_indices(stationary, kernel)
    if not core:
        core = list(range(max(2, n // 4)))
    core_mass = [0.0 for _ in range(n)]
    for i in core:
        core_mass[i] = 1.0
    core_mass = _normalize_row(core_mass)
    alternating = _normalize_row([1.0 + 0.35 * ((i % 2) * 2 - 1) for i in range(n)])
    return [stationary, uniform, core_mass, alternating]


def evolve_forget_reinstate(
    mu: list[float],
    kernel: list[list[float]],
    tau: float,
    lens_state: str,
    packaging_state: dict[str, Any] | None = None,
    *,
    return_meta: bool = False,
) -> tuple[list[float], dict[str, Any]] | list[float]:
    """Apply U_f(Q_f(mu B_tau)) using the lazy blend B_tau of K and I.

    B_tau is defined by _completion_kernel_blend; it is not a fractional
    matrix power K^tau. With a fixed partition and prototypes this is a
    linear stochastic map on probability vectors.

    Q_f forgets within-package detail by coarse-graining mu to the lens-selected
    package masses. U_f reinstantiates a packaged state from those masses using
    the current kernel and lens-dependent prototype weights.
    """
    n = len(kernel)
    if n == 0:
        meta = {"applied": False, "reason": "empty-kernel"}
        return ([], meta) if return_meta else []
    if len(mu) != n:
        raise ValueError("mu and kernel must have the same dimension")
    if any(len(row) != n for row in kernel):
        raise ValueError("kernel must be square")
    if any(not math.isfinite(x) or x < 0 for row in kernel for x in row):
        raise ValueError("kernel entries must be finite and nonnegative")
    if any(abs(sum(row) - 1.0) > 1e-10 for row in kernel):
        raise ValueError("kernel must be row-stochastic")
    if any(not math.isfinite(x) or x < 0 for x in mu) or sum(mu) <= 0:
        raise ValueError("mu must have finite nonnegative entries and positive mass")
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError("tau must be finite and positive")
    packaging_state = packaging_state or _completion_packaging_from_lens(kernel, tau, lens_state)
    kernel_tau = _completion_kernel_blend(kernel, tau)
    transport = _normalize_row(
        [
            sum(mu[i] * kernel_tau[i][j] for i in range(n))
            for j in range(n)
        ]
    )

    groups = [group for group in packaging_state.get("groups", []) if group]
    if not groups:
        groups = [list(range(n))]
    members = [i for group in groups for i in group]
    if sorted(members) != list(range(n)):
        raise ValueError("packaging groups must partition the kernel states")

    package_masses = [sum(transport[i] for i in group) for group in groups]
    reinstated = [0.0 for _ in range(n)]
    stationary = _stationary_distribution(kernel)
    support = packaging_state.get("support") or [1.0 / n for _ in range(n)]
    if len(support) != n or any(not math.isfinite(x) or x < 0 for x in support):
        raise ValueError("packaging support must be finite, nonnegative, and dimension-matched")
    for group, mass in zip(groups, package_masses):
        proto = [
            max(0.0, 0.55 * stationary[i] + 0.25 * support[i] + 0.20 * kernel[i][i])
            for i in group
        ]
        total = sum(proto)
        if total <= 0.0:
            proto = [1.0 / len(group) for _ in group]
            total = 1.0
        for idx, state_idx in enumerate(group):
            reinstated[state_idx] += mass * (proto[idx] / total)

    completed = _normalize_row(reinstated)
    meta = {
        "applied": True,
        "transport_mass": sum(transport),
        "package_count": len(groups),
        "package_masses": package_masses,
        "package_entropy": _entropy(package_masses),
        "lens_state": lens_state,
        "packaging_state": packaging_state,
    }
    return (completed, meta) if return_meta else completed


def iterate_completion_endomap(
    mu0: list[float],
    kernel: list[list[float]],
    tau: float,
    lens_state: str,
    *,
    max_iter: int = 48,
    tol: float = 1e-7,
    packaging_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if max_iter < 1 or not math.isfinite(tol) or tol <= 0:
        raise ValueError("max_iter and tol must be positive")
    if not kernel or len(mu0) != len(kernel):
        raise ValueError("completion requires a nonempty kernel and matching mu0")
    if any(not math.isfinite(x) or x < 0 for x in mu0) or sum(mu0) <= 0:
        raise ValueError("mu0 must have finite nonnegative entries and positive mass")
    current = _normalize_row(list(mu0))
    # Rounded bins can repeat while the map is still converging. Only a
    # repeated full floating vector is recorded as a numerical cycle.
    seen: dict[tuple[float, ...], int] = {tuple(current): 0}
    history: list[list[float]] = [current]
    meta_history: list[dict[str, Any]] = []
    status = "nonconvergent"
    cycle_length = 0
    for step in range(max_iter):
        nxt, meta = evolve_forget_reinstate(
            current,
            kernel,
            tau,
            lens_state,
            packaging_state,
            return_meta=True,
        )
        meta_history.append(meta)
        diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(current, nxt)))
        sig = tuple(nxt)
        if diff <= tol:
            status = "fixed_point"
            current = nxt
            history.append(current)
            break
        if sig in seen:
            status = "cycle"
            cycle_length = step + 1 - seen[sig]
            current = nxt
            history.append(current)
            break
        seen[sig] = step + 1
        current = nxt
        history.append(current)
    else:
        current = history[-1]

    fixed_point_signature = tuple(round(x, 6) for x in current)
    image, final_meta = evolve_forget_reinstate(
        current, kernel, tau, lens_state, packaging_state, return_meta=True,
    )
    residual = math.sqrt(sum((a - b) ** 2 for a, b in zip(current, image)))
    return {
        "status": status,
        "cycle_length": cycle_length,
        "iterations": len(history) - 1,
        "initial_mu_signature": tuple(round(x, 6) for x in mu0),
        "final_mu": current,
        "final_signature": fixed_point_signature,
        "history": history,
        "meta_history": meta_history,
        "residual": residual,
        "package_count": final_meta["package_count"],
        "package_entropy": final_meta["package_entropy"],
        "numerically_converged": status == "fixed_point" and residual <= tol,
        "certified_fixed_point": False,
    }


def update_lens_from_packaging(
    current_lens: str,
    completion_summary: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    package_count = int(completion_summary.get("package_count", 0))
    entropy = float(completion_summary.get("package_entropy", 0.0))
    residual = float(completion_summary.get("residual", 0.0))
    status = str(completion_summary.get("status", "nonconvergent"))
    packaging_active = status in {"fixed_point", "cycle"} or package_count >= 2 or entropy > 0.4 or residual < 1e-4
    if current_lens == "spectral_lens" and packaging_active:
        next_lens = "row_similarity_cluster_lens"
    elif current_lens == "row_similarity_cluster_lens" and packaging_active:
        next_lens = "audit_flow_quantile_lens"
    elif current_lens == "audit_flow_quantile_lens" and packaging_active:
        next_lens = "spectral_lens"
    else:
        next_lens = current_lens
    return next_lens, {
        "applied": next_lens != current_lens,
        "from_lens": current_lens,
        "to_lens": next_lens,
        "status": status,
        "package_count": package_count,
        "package_entropy": entropy,
        "residual": residual,
    }


def packaging_macro_admissibility(
    completion_summary: dict[str, Any],
    *,
    kernel: list[list[float]] | None = None,
    groups: list[list[int]] | None = None,
    tol: float = 1e-10,
) -> dict[str, Any]:
    """Numerically test strong lumpability of transport under a partition.

    Convergence of the completion iteration is a separate question. When the
    transport and partition are absent, admissibility is unknown.
    """
    status = str(completion_summary.get("status", "nonconvergent"))
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be finite and positive")
    residual = float(completion_summary.get("residual", 1.0))
    package_count = int(completion_summary.get("package_count", 0))
    defect = None
    if kernel is not None and groups is not None:
        n = len(kernel)
        if not n or any(len(row) != n for row in kernel):
            raise ValueError("kernel must be nonempty square")
        if any(not math.isfinite(x) or x < 0 for row in kernel for x in row):
            raise ValueError("kernel must have finite nonnegative entries")
        if any(abs(sum(row) - 1.0) > tol for row in kernel):
            raise ValueError("kernel must be row-stochastic")
        if any(not group for group in groups) or sorted(i for group in groups for i in group) != list(range(n)):
            raise ValueError("groups must be a partition")
        defect = max(
            (max(sum(kernel[i][j] for j in target) for i in source)
             - min(sum(kernel[i][j] for j in target) for i in source))
            for source in groups for target in groups
        )
    admissible = None if defect is None else defect <= tol
    return {
        "admissible": admissible,
        "status": status,
        "residual": residual,
        "package_count": package_count,
        "lumpability_checked": defect is not None,
        "max_lumpability_defect": defect,
        "criterion": "strong_lumpability_numerical",
        "certified": False,
    }


def compute_packaging_fixed_points(
    kernel: list[list[float]],
    tau_values: list[float],
    lens_states: list[str],
    initial_distributions: list[list[float]],
    *,
    max_iter: int = 48,
    tol: float = 1e-7,
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    fixed_signatures: set[tuple[float, ...]] = set()
    for tau in tau_values:
        for lens_state in lens_states:
            packaging_state = _completion_packaging_from_lens(kernel, tau, lens_state)
            for idx, mu0 in enumerate(initial_distributions):
                summary = iterate_completion_endomap(
                    mu0,
                    kernel,
                    tau,
                    lens_state,
                    max_iter=max_iter,
                    tol=tol,
                    packaging_state=packaging_state,
                )
                next_lens, feedback = update_lens_from_packaging(lens_state, summary)
                admissibility = packaging_macro_admissibility(
                    summary, kernel=_completion_kernel_blend(kernel, tau),
                    groups=packaging_state["groups"],
                )
                if summary["numerically_converged"]:
                    fixed_signatures.add(summary["final_signature"])
                runs.append(
                    {
                        "tau": tau,
                        "lens_state": lens_state,
                        "initial_index": idx,
                        "completion_summary": summary,
                        "packaging_state": packaging_state,
                        "feedback": feedback,
                        "next_lens": next_lens,
                        "macro_admissibility": admissibility,
                    }
                )
    return {
        "runs": runs,
        "distinct_fixed_point_count": len(fixed_signatures),
        "distinct_fixed_point_signatures": [list(sig) for sig in sorted(fixed_signatures)],
        "fixed_point_count_scope": "rounded_numerically_converged_candidates_only",
        "certified_fixed_point_count": 0,
    }


def detect_packaging_saturation(
    completion_runs: list[dict[str, Any]],
    *,
    tau_values: list[float],
    lens_states: list[str],
    initial_count: int,
) -> dict[str, Any]:
    by_panel: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for run in completion_runs:
        by_panel.setdefault((float(run["tau"]), str(run["lens_state"])), []).append(run)

    panel_summaries: list[dict[str, Any]] = []
    saturated_panels = 0
    for (tau, lens_state), entries in by_panel.items():
        seen: set[tuple[float, ...]] = set()
        new_counts: list[int] = []
        for entry in entries:
            if not entry["completion_summary"].get("numerically_converged", False):
                continue
            sig = tuple(entry["completion_summary"]["final_signature"])
            before = len(seen)
            seen.add(sig)
            new_counts.append(len(seen) - before)
        saturated = (bool(new_counts) and len(new_counts) == len(entries)
                     and new_counts[-1] == 0 and len(seen) <= max(1, initial_count - 1))
        saturated_panels += 1 if saturated else 0
        panel_summaries.append(
            {
                "tau": tau,
                "lens_state": lens_state,
                "distinct_fixed_points": len(seen),
                "saturated": saturated,
            }
        )
    return {
        "panel_summaries": panel_summaries,
        "saturated_panel_count": saturated_panels,
        "total_panels": len(panel_summaries),
        "saturation_verified": False,
        "scope": "finite_start_duplicate_candidate_diagnostic",
        "tau_values": tau_values,
        "lens_states": lens_states,
        "initial_count": initial_count,
        "saturated": saturated_panels == len(panel_summaries) and len(panel_summaries) > 0,
    }
