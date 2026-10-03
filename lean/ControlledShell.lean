import KernelLawfulness
import PressureRegularity

/-! All-time control lemmas for the original-shell construction.

The concrete phase kernels, original selector guards and noise/income bounds
are certified by outward rational interval arithmetic in controlled_shell.py.
These lemmas mechanize their return through the actual clipping/normalization,
timescale and budget formulas. They do not encode that interval dataset or
certify the seeded experiments or uncontrolled-noise invariance.
-/
namespace CantorAudit
noncomputable section

theorem normalized_target_control {d : ℕ} (pre target : Fin d → ℝ)
    (nonneg : ∀ j, 0 ≤ target j) (mass : ∑ j, target j = 1) :
    noiseNormalizedRow pre (fun j => target j-pre j) = target := by
  have hc : ∀ j, clippedRow pre (fun j => target j-pre j) j = target j := by
    intro j
    dsimp [clippedRow]
    rw [add_sub_cancel, max_eq_right (nonneg j)]
  funext j
  simp only [noiseNormalizedRow, hc, mass, div_one]

def controlledTimescale (tau variation : ℝ) (switch : Bool) : ℝ :=
  max (3/5) (min 4 (tau + (11/100)*max 0 ((3/25)-variation)
    - (3/50)*variation - if switch then 3/25 else 0))

theorem controlledTimescale_step_bound (tau v : ℝ) (sw : Bool)
    (hv : 0 ≤ v) :
    3/5 ≤ controlledTimescale tau v sw ∧
      controlledTimescale tau v sw ≤ max (3/5) (tau+33/2500) := by
  have hm : max 0 ((3/25 : ℝ)-v) ≤ 3/25 := max_le (by norm_num) (by linarith)
  have hp : 0 ≤ (if sw then (3/25 : ℝ) else 0) := by split <;> norm_num
  constructor
  · exact le_max_left _ _
  · apply max_le_max (le_refl _)
    exact (min_le_right _ _).trans (by nlinarith)

theorem controlledTimescale_switch_reset (tau v : ℝ)
    (hv : 0 ≤ v) (ht : tau ≤ 1599/2500) :
    controlledTimescale tau v true = 3/5 := by
  have hm : max 0 ((3/25 : ℝ)-v) ≤ 3/25 := max_le (by norm_num) (by linarith)
  apply max_eq_left
  apply (min_le_right _ _).trans
  simp only [Bool.true_eq_false, ↓reduceIte]
  nlinarith

def controlledBudget (budget income cost : ℝ) : ℝ :=
  max 0 (min 12 (budget+income-cost))

theorem controlledBudget_preserved (b income cost : ℝ)
    (_hb : 3 ≤ b) (hb12 : b ≤ 12) (gain : 0 ≤ income-cost) :
    b ≤ controlledBudget b income cost ∧ controlledBudget b income cost ≤ 12 := by
  constructor
  · exact (le_min hb12 (by linarith)).trans (le_max_right _ _)
  · exact max_le (by norm_num) (min_le_left _ _)

theorem controlledBudget_increases_before_cap (b income cost : ℝ)
    (hb : b < 12) (gain : 0 < income-cost) :
    b < controlledBudget b income cost :=
  (lt_min hb (by linarith)).trans_le (le_max_right _ _)

/-- A verified invariant carrier supplies an infinite orbit by induction;
no finite simulation horizon is promoted to an all-time statement. -/
theorem controlled_shell_all_iterates {X : Type*} (F : X → X) (S : Set X)
    (invariant : ∀ x, x ∈ S → F x ∈ S) {x : X} (start : x ∈ S) :
    ∀ n : ℕ, (F^[n]) x ∈ S := by
  intro n
  induction n with
  | zero => simpa using start
  | succ n ih =>
      rw [Function.iterate_succ_apply']
      exact invariant _ ih

theorem controlled_shell_root_anchor :
    Real.log (20 : ℝ) - (1/3)*Real.log 1000 = Real.log 2 := by
  have h1000 : Real.log (1000 : ℝ) = 3*Real.log 10 := by
    rw [show (1000 : ℝ) = (10 : ℝ)^3 by norm_num, Real.log_pow]
    norm_num
  have h20 : Real.log (20 : ℝ) = Real.log 2+Real.log 10 := by
    rw [show (20 : ℝ) = 2*10 by norm_num, Real.log_mul (by norm_num) (by norm_num)]
  rw [h1000,h20]
  ring

/-- On the constructed carrier K_ij >= .01 is derived from the targets,
not introduced as a new minorization operator. Together with the original
q bounds, this gives the displayed secants and the s=1 row bound. The exact
20-state interval dataset itself is not imported as Lean terms here. -/
theorem controlled_shell_pressure_root (P : ℝ → ℝ)
    (at_zero : P 0 = Real.log 20)
    (at_one : P 1 ≤ -Real.log (5/4))
    (secant : ∀ s t, 0 ≤ s → s ≤ t →
      (t-s)*(-Real.log 1000) ≤ P t-P s ∧ P t-P s ≤ (t-s)*(-Real.log (5/4))) :
    ∃ s ∈ Set.Ioo (1/3 : ℝ) 1, P s = 0 ∧ ∀ t, 0 ≤ t → P t = 0 → t = s := by
  have log_pos : 0 < Real.log (5/4 : ℝ) := Real.log_pos (by norm_num)
  have log_order : -Real.log (1000 : ℝ) ≤ -Real.log (5/4) := by
    exact neg_le_neg (Real.log_le_log (by norm_num) (by norm_num))
  have positive : 0 < P (1/3) := by
    have h := (secant 0 (1/3) (by norm_num) (by norm_num)).1
    rw [at_zero] at h
    have anchor := controlled_shell_root_anchor
    have log_two : 0 < Real.log (2 : ℝ) := Real.log_pos (by norm_num)
    nlinarith
  obtain ⟨s,hs,hz,unique⟩ := pressure_unique_zero P _ _ log_order (by linarith)
    secant (by rw [at_zero]; exact Real.log_pos (by norm_num)) (by linarith)
  have lower : (1/3 : ℝ) < s := by
    by_contra h
    have le : s ≤ 1/3 := le_of_not_gt h
    rcases lt_or_eq_of_le le with lt | eq
    · have anti := pressure_strictAnti P _ _ (show -Real.log (5/4 : ℝ)<0 by linarith)
        secant hs.1.le (show (0 : ℝ) ≤ 1/3 by norm_num) lt
      linarith
    · rw [eq] at hz
      linarith
  exact ⟨s,⟨lower,hs.2⟩,hz,unique⟩

end
end CantorAudit
