import CantorAudit

/-! Exact row-level invariance for clipping noise and optional minorization.
No claim about selector margins, six-fold necessity or noncollapse is made.
-/
namespace CantorAudit
noncomputable section

def clippedRow {d : ℕ} (k e : Fin d → ℝ) (j : Fin d) : ℝ := max 0 (k j + e j)

theorem clippedRow_mass_lower {d : ℕ} (k e : Fin d → ℝ) (σ : ℝ)
    (mass : ∑ j, k j = 1) (noise : ∀ j, -σ ≤ e j) :
    1 - (d : ℝ) * σ ≤ ∑ j, clippedRow k e j := by
  have h : ∑ j : Fin d, (k j - σ) ≤ ∑ j : Fin d, clippedRow k e j := by
    apply Finset.sum_le_sum
    intro j _
    exact (by linarith [noise j] : k j - σ ≤ k j + e j).trans (le_max_right _ _)
  simpa [Finset.sum_sub_distrib, mass] using h

def noiseNormalizedRow {d : ℕ} (k e : Fin d → ℝ) (j : Fin d) : ℝ :=
  clippedRow k e j / ∑ h, clippedRow k e h

theorem noiseNormalizedRow_stochastic {d : ℕ} (k e : Fin d → ℝ) (σ : ℝ)
    (mass : ∑ j, k j = 1) (noise : ∀ j, -σ ≤ e j)
    (small : (d : ℝ) * σ < 1) :
    (∀ j, 0 ≤ noiseNormalizedRow k e j) ∧ ∑ j, noiseNormalizedRow k e j = 1 := by
  have hp : 0 < ∑ j, clippedRow k e j :=
    lt_of_lt_of_le (by linarith : 0 < 1 - (d : ℝ) * σ)
      (clippedRow_mass_lower k e σ mass noise)
  constructor
  · intro j; exact div_nonneg (le_max_left _ _) hp.le
  · simp only [noiseNormalizedRow, ← Finset.sum_div]
    exact div_self hp.ne'

def minorizedRow {d : ℕ} (k : Fin d → ℝ) (ε : ℝ) (j : Fin d) : ℝ :=
  (1 - ε) * k j + ε / d

theorem minorizedRow_stochastic {d : ℕ} (hd : 0 < d) (k : Fin d → ℝ) (ε : ℝ)
    (nonneg : ∀ j, 0 ≤ k j) (mass : ∑ j, k j = 1)
    (_he : 0 ≤ ε) (he1 : ε ≤ 1) :
    (∀ j, ε / d ≤ minorizedRow k ε j) ∧ ∑ j, minorizedRow k ε j = 1 := by
  constructor
  · intro j
    have h := mul_nonneg (sub_nonneg.mpr he1) (nonneg j)
    dsimp [minorizedRow]; linarith
  · simp only [minorizedRow, Finset.sum_add_distrib, ← Finset.mul_sum, mass]
    have hdR : (d : ℝ) ≠ 0 := by exact_mod_cast Nat.ne_of_gt hd
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    field_simp [hdR]

theorem minorizedRow_positive {d : ℕ} (hd : 0 < d) (k : Fin d → ℝ) (ε : ℝ)
    (nonneg : ∀ j, 0 ≤ k j) (mass : ∑ j, k j = 1)
    (he : 0 < ε) (he1 : ε ≤ 1) (j : Fin d) :
    0 < minorizedRow k ε j :=
  lt_of_lt_of_le (div_pos he (by exact_mod_cast hd))
    ((minorizedRow_stochastic hd k ε nonneg mass he.le he1).1 j)

/-- Exact finite-difference identity behind the ideal-noise noncollapse
argument. Its probabilistic all-time step is in the analytic note. -/
theorem normalized_coordinate_difference (S y u v : ℝ)
    (hu : S + y + u ≠ 0) (hv : S + y + v ≠ 0) :
    (y + v) / (S + y + v) - (y + u) / (S + y + u) =
      S * (v - u) / ((S + y + v) * (S + y + u)) := by
  field_simp
  ring

theorem clamped_interval (lo hi x : ℝ) (h : lo ≤ hi) :
    lo ≤ max lo (min hi x) ∧ max lo (min hi x) ≤ hi := by
  exact ⟨le_max_left _ _, max_le h (min_le_left _ _)⟩

end
end CantorAudit
