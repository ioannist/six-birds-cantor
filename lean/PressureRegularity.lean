import KernelCocycle
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Topology.MetricSpace.Lipschitz

/-! The parameter endpoint of the pressure theorem, with its precise input.
The secant bounds are obtained analytically from uniform branch-weight bounds;
this file does not assume continuity or monotonicity as additional premises.
-/
namespace CantorAudit
open Set

theorem pressure_lipschitz (P : ℝ → ℝ) (L U : ℝ)
    (hL : L ≤ U) (hU : U < 0)
    (secant : ∀ s t, 0 ≤ s → s ≤ t →
      (t - s) * L ≤ P t - P s ∧ P t - P s ≤ (t - s) * U) :
    LipschitzOnWith ⟨-L, by linarith⟩ P (Ici 0) := by
  apply lipschitzOnWith_iff_dist_le_mul.mpr
  intro s hs t ht
  simp only [Real.dist_eq, NNReal.coe_mk]
  rcases le_total s t with hst | hts
  · have hb := secant s t hs hst
    have hp : P t - P s ≤ 0 := by nlinarith
    rw [abs_of_nonneg (by linarith : 0 ≤ P s - P t),
      abs_of_nonpos (by linarith : s - t ≤ 0)]
    nlinarith [hb.1]
  · have hb := secant t s ht hts
    have hp : P s - P t ≤ 0 := by nlinarith
    rw [abs_of_nonpos hp, abs_of_nonneg (by linarith : 0 ≤ s - t)]
    nlinarith [hb.1]

theorem pressure_strictAnti (P : ℝ → ℝ) (L U : ℝ) (hU : U < 0)
    (secant : ∀ s t, 0 ≤ s → s ≤ t →
      (t - s) * L ≤ P t - P s ∧ P t - P s ≤ (t - s) * U) :
    StrictAntiOn P (Ici 0) := by
  intro s hs t _ hst
  have hb := (secant s t hs hst.le).2
  have hn : (t - s) * U < 0 := mul_neg_of_pos_of_neg (sub_pos.mpr hst) hU
  linarith

theorem pressure_unique_zero (P : ℝ → ℝ) (L U : ℝ) (hL : L ≤ U) (hU : U < 0)
    (secant : ∀ s t, 0 ≤ s → s ≤ t →
      (t - s) * L ≤ P t - P s ∧ P t - P s ≤ (t - s) * U)
    (at_zero : 0 < P 0) (at_one : P 1 < 0) :
    ∃ s ∈ Ioo (0 : ℝ) 1, P s = 0 ∧ ∀ t, 0 ≤ t → P t = 0 → t = s := by
  have hc := (pressure_lipschitz P L U hL hU secant).continuousOn.mono
    (show Icc (0 : ℝ) 1 ⊆ Ici 0 from fun _ h => h.1)
  obtain ⟨s, hs, hz⟩ := intermediate_value_Icc' (show (0 : ℝ) ≤ 1 by norm_num) hc
    (show (0 : ℝ) ∈ Icc (P 1) (P 0) from ⟨at_one.le, at_zero.le⟩)
  have hs0 : 0 < s := by
    apply lt_of_le_of_ne hs.1
    intro he
    subst s
    linarith
  have hs1 : s < 1 := by
    apply lt_of_le_of_ne hs.2
    intro he
    subst s
    linarith
  refine ⟨s, ⟨hs0, hs1⟩, hz, ?_⟩
  intro t ht htz
  exact (pressure_strictAnti P L U hU secant).injOn ht hs0.le (htz.trans hz.symm)

end CantorAudit
