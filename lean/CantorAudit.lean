import Mathlib.Analysis.Subadditive
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic

/-!
Mathematical audit lemmas. These do not certify the simulation shell or the
paper's four theoremlets. In particular no collision of *exact* base objects
is supplied by the generic non-factorization lemma below.
-/

namespace CantorAudit
open Filter Set
open scoped Topology

theorem collision_obstructs_factorization {X A B : Type*}
    (p₀ : X → A) (p₁ : X → B) {x y : X}
    (same : p₀ x = p₀ y) (different : p₁ x ≠ p₁ y) :
    ¬ ∃ f : A → B, p₁ = f ∘ p₀ := by
  rintro ⟨f, hf⟩
  apply different
  rw [hf]
  exact congrArg f same

/-- The converse requires an inhabited output carrier to extend a map from
the image of p₀ to all of A. This is the exact descriptor-relative criterion.
-/
theorem factorization_iff_constant_on_fibers {X A B : Type*} [Nonempty B]
    (p₀ : X → A) (p₁ : X → B) :
    (∃ f : A → B, p₁ = f ∘ p₀) ↔
    (∀ x y, p₀ x = p₀ y → p₁ x = p₁ y) := by
  classical
  constructor
  · rintro ⟨f, hf⟩ x y h
    rw [hf]
    exact congrArg f h
  · intro h
    let f : A → B := fun a =>
      if ha : ∃ x, p₀ x = a then p₁ (Classical.choose ha) else Classical.choice inferInstance
    refine ⟨f, ?_⟩
    funext x
    have hx : ∃ y, p₀ y = p₀ x := ⟨x, rfl⟩
    simp only [Function.comp_apply, f, dif_pos hx]
    exact h x (Classical.choose hx) (Classical.choose_spec hx).symm

/-- Non-factorization is possible when *all* pressure profiles are zero.
This refutes the implication from object extension to a nonzero weighted gap.
-/
theorem extension_with_zero_gap :
    (¬ ∃ f : Unit → Bool, (fun x : Bool => x) = f ∘ (fun _ => ())) ∧
    ((0 : ℝ) - ((1 / 2) * 0 + (1 / 2) * 0) = 0) := by
  constructor
  · exact collision_obstructs_factorization (fun _ : Bool => ()) id
      (x := false) (y := true) rfl (by decide)
  · norm_num

/-- A faithful base object may still split after an additional coarse readout.
Splitting of a binned readout alone does not refute factorization through the
original base object.
-/
theorem coarse_collision_with_exact_factorization :
    (∃ f : Bool → Bool, id = f ∘ id) ∧
    ((fun _ : Bool => ()) false = (fun _ : Bool => ()) true) ∧
    (id false ≠ id true) := by
  exact ⟨⟨id, rfl⟩, rfl, by decide⟩

/-- Almost-subadditivity gives a genuine subadditive sequence after shifting.
The uniform all-horizon inequality here is an explicit premise, not inferred
from a finite trajectory or a consecutive-difference diagnostic.
-/
theorem shifted_subadditive (u : ℕ → ℝ) (C : ℝ)
    (comparison : ∀ m n, u (m + n) ≤ u m + u n + C) :
    Subadditive (fun n => u n + C) := by
  intro m n
  have h := comparison m n
  dsimp
  linarith

theorem conditional_fekete (u : ℕ → ℝ) (C : ℝ)
    (comparison : ∀ m n, u (m + n) ≤ u m + u n + C)
    (lower : BddBelow (range fun n => (u n + C) / n)) :
    ∃ L : ℝ, Tendsto (fun n => u n / n) atTop (𝓝 L) := by
  have h := shifted_subadditive u C comparison
  refine ⟨h.lim, ?_⟩
  have hlim := h.tendsto_lim lower
  have hc := tendsto_const_div_atTop_nhds_zero_nat C
  have hs := hlim.sub hc
  simpa only [add_div, add_sub_cancel_right, sub_zero] using hs

/-- Any positive partition sequence trapped between positive constant
multiples of n has zero normalized logarithmic growth.
-/
theorem linear_partition_zero_pressure (Z : ℕ → ℝ) (c C : ℝ)
    (hc : 0 < c) (hC : 0 < C)
    (bounds : ∀ n : ℕ, 0 < n → (n : ℝ) * c ≤ Z n ∧ Z n ≤ (n : ℝ) * C) :
    Tendsto (fun n => Real.log (Z n) / n) atTop (𝓝 0) := by
  have logn : Tendsto (fun n : ℕ => Real.log (n : ℝ) / n) atTop (𝓝 0) := by
    have h := Real.tendsto_pow_log_div_mul_add_atTop 1 0 1 (by norm_num : (1 : ℝ) ≠ 0)
    simpa using h.comp tendsto_natCast_atTop_atTop
  have lc : Tendsto (fun n : ℕ => (Real.log (n : ℝ) + Real.log c) / n) atTop (𝓝 0) := by
    simpa only [add_div, add_zero] using logn.add (tendsto_const_div_atTop_nhds_zero_nat (Real.log c))
  have lC : Tendsto (fun n : ℕ => (Real.log (n : ℝ) + Real.log C) / n) atTop (𝓝 0) := by
    simpa only [add_div, add_zero] using logn.add (tendsto_const_div_atTop_nhds_zero_nat (Real.log C))
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' lc lC
  · filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
    have hnR : (0 : ℝ) < n := by exact_mod_cast hn
    have hb := (bounds n hn).1
    have hl := Real.log_le_log (mul_pos hnR hc) hb
    rw [Real.log_mul hnR.ne' hc.ne'] at hl
    exact div_le_div_of_nonneg_right hl hnR.le

  · filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
    have hnR : (0 : ℝ) < n := by exact_mod_cast hn
    have hb := bounds n hn
    have hp : 0 < Z n := lt_of_lt_of_le (mul_pos hnR hc) hb.1
    have hl := Real.log_le_log hp hb.2
    rw [Real.log_mul hnR.ne' hC.ne'] at hl
    exact div_le_div_of_nonneg_right hl hnR.le

theorem bounded_weight_sum_zero_pressure (w : ℕ → ℝ) (c C : ℝ)
    (hc : 0 < c) (hC : 0 < C) (hw : ∀ t, c ≤ w t ∧ w t ≤ C) :
    Tendsto (fun n => Real.log (∑ t in Finset.range n, w t) / n) atTop (𝓝 0) := by
  apply linear_partition_zero_pressure _ c C hc hC
  intro n _
  constructor
  · calc
      (n : ℝ) * c = ∑ _t in Finset.range n, c := by simp
      _ ≤ ∑ t in Finset.range n, w t := Finset.sum_le_sum (fun t _ => (hw t).1)
  · calc
      (∑ t in Finset.range n, w t) ≤ ∑ _t in Finset.range n, C :=
        Finset.sum_le_sum (fun t _ => (hw t).2)
      _ = (n : ℝ) * C := by simp

/-- This is the actual time-sum formula in the pressure diagnostics, for
nonnegative uniformly bounded observables. Every s >= 0 has pressure zero.
-/
theorem selector_time_sum_zero (q : ℕ → ℝ) (Q s : ℝ)
    (hs : 0 ≤ s) (hq : ∀ t, 0 ≤ q t ∧ q t ≤ Q) :
    Tendsto (fun n => Real.log (∑ t in Finset.range n, Real.exp (-s * q t)) / n)
      atTop (𝓝 0) := by
  apply bounded_weight_sum_zero_pressure _ (Real.exp (-s * Q)) 1 (Real.exp_pos _) zero_lt_one
  intro t
  have ht := hq t
  constructor
  · apply Real.exp_le_exp.mpr
    nlinarith
  · rw [← Real.exp_zero]
    apply Real.exp_le_exp.mpr
    nlinarith

/-- Exact affine waiting-domain invariant for frontier witness a3. A point
may wait arbitrarily many times before returning; finite search depth cannot
establish a uniform return bound.
-/
theorem a3_wait_domain_invariant (x : ℚ) (lo : 11 / 50 ≤ x) (hi : x ≤ 3 / 10) :
    11 / 50 ≤ (7 / 20) * x + 9 / 50 ∧ (7 / 20) * x + 9 / 50 ≤ 3 / 10 := by
  constructor <;> linarith

def a3Wait (k : ℕ) (x : ℚ) : ℚ :=
  match k with
  | 0 => x
  | k + 1 => (7 / 20) * a3Wait k x + 9 / 50

theorem a3_arbitrarily_long_waits (k : ℕ) :
    11 / 50 ≤ a3Wait k (11 / 50) ∧ a3Wait k (11 / 50) ≤ 3 / 10 := by
  induction k with
  | zero => norm_num [a3Wait]
  | succ k ih => exact a3_wait_domain_invariant _ ih.1 ih.2

theorem a3_wait_then_return (k : ℕ) :
    0 ≤ (2 / 5 : ℚ) * a3Wait k (11 / 50) ∧
    (2 / 5 : ℚ) * a3Wait k (11 / 50) ≤ 1 / 5 := by
  have h := a3_arbitrarily_long_waits k
  constructor <;> linarith

end CantorAudit
