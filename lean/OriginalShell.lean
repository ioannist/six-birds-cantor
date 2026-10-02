import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

/-! Exact arithmetic child of the original 20-state rectangular-shell
counterexample. The source-to-formula bridge (uniform informants, selectors,
P1/P2 multiplicities, empty switch history) is stated in the companion note;
it is not asserted as a complete formalization of the Python transition.
-/
namespace CantorAudit
noncomputable section

/-- Exact source selector scores at the stated uniform warm state. The
square-root bounds give isolation stronger than either original hysteresis
or the stochastic tie band 0.03; the latter therefore has only one member. -/
theorem uniformShell_selector_and_eta_bounds :
    (3/100:ℝ) < (731/1600:ℝ) - ((7/20:ℝ) + Real.sqrt 2 / 40) ∧
    (3/100:ℝ) < (731/1600:ℝ) - (45197/400000:ℝ) ∧
    (3/100:ℝ) < ((3671/5000:ℝ) + 7*Real.sqrt 3/200) - (427325/1000000:ℝ) ∧
    (3/100:ℝ) < ((3671/5000:ℝ) + 7*Real.sqrt 3/200) - (121/250:ℝ) ∧
    (0:ℝ) ≤ (101/1000:ℝ) + ((3671/5000:ℝ) + 7*Real.sqrt 3/200)/20 ∧
    (101/1000:ℝ) + ((3671/5000:ℝ) + 7*Real.sqrt 3/200)/20 ≤ 141/1000 := by
  have h2 : Real.sqrt (2:ℝ) ≤ 3/2 := by
    apply (Real.sqrt_le_iff).mpr; norm_num
  have h3 : Real.sqrt (3:ℝ) ≤ 7/4 := by
    apply (Real.sqrt_le_iff).mpr; norm_num
  have n3 := Real.sqrt_nonneg (3:ℝ)
  constructor
  · linarith
  constructor
  · norm_num
  constructor
  · linarith
  constructor
  · linarith
  constructor <;> linarith

def uniformShellVariationSquare (eta : ℝ) : ℝ :=
  20 * ((13/20:ℝ)*eta)^2 *
    ((((3/20:ℝ)+(731/1600:ℝ)/50)/((17/10:ℝ)+(731/1600:ℝ)/50)-1/20)^2 +
    9*((3/20:ℝ)/((17/10:ℝ)+(731/1600:ℝ)/50)-1/20)^2 +
    10*((1/50:ℝ)/((17/10:ℝ)+(731/1600:ℝ)/50)-1/20)^2)

theorem uniformShellVariation_cap (eta : ℝ) (lo : 0 ≤ eta) (hi : eta ≤ 141/1000) :
    Real.sqrt (uniformShellVariationSquare eta) ≤ 3/40 := by
  apply (Real.sqrt_le_iff).mpr
  constructor
  · norm_num
  · have sq : eta^2 ≤ (141/1000:ℝ)^2 := by nlinarith
    unfold uniformShellVariationSquare
    norm_num
    nlinarith

def uniformShellTimescale (variation : ℝ) : ℝ :=
  max (3/5:ℝ) (min 4 ((21/20:ℝ) + (11/100:ℝ)*max 0 ((3/25:ℝ)-variation)
    - (3/50:ℝ)*variation))

theorem uniformShellTimescale_exit (v : ℝ) (lo : 0 ≤ v) (hi : v ≤ 3/40) :
    (21009/20000:ℝ) ≤ uniformShellTimescale v ∧ (21/20:ℝ) < uniformShellTimescale v := by
  have stability : 0 ≤ (3/25:ℝ)-v := by linarith
  have rawlo : (21009/20000:ℝ) ≤ (21/20:ℝ)+(11/100:ℝ)*((3/25:ℝ)-v)-(3/50:ℝ)*v := by
    linarith
  have rawhi : (21/20:ℝ)+(11/100:ℝ)*((3/25:ℝ)-v)-(3/50:ℝ)*v ≤ 4 := by
    linarith
  unfold uniformShellTimescale
  rw [max_eq_right stability, min_eq_right rawhi, max_eq_right (by linarith :
    (3/5:ℝ) ≤ (21/20:ℝ)+(11/100:ℝ)*((3/25:ℝ)-v)-(3/50:ℝ)*v)]
  exact ⟨rawlo, by linarith⟩

end
end CantorAudit
