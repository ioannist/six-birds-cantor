import CantorAudit

/-! The stationary readout bridge for retained-package recoupling. The
analytic construction supplies the common current kernel and actual P5
prototypes. Reachability of the complete simulator is not mechanized here. -/
namespace CantorAudit

/-- A B Q U operator has this row ratio for two states in the same cell;
stationarity transfers it to the fixed distribution. -/
theorem completion_stationary_ratio {d : ℕ} (E : Fin d → Fin d → ℚ)
    (μ w : Fin d → ℚ) (u v : Fin d)
    (row_ratio : ∀ i, E i u * w v = E i v * w u)
    (stationary : ∀ j, ∑ i : Fin d, μ i * E i j = μ j) :
    μ u * w v = μ v * w u := by
  rw [← stationary u, ← stationary v]
  rw [Finset.sum_mul, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  simpa only [mul_assoc] using congrArg (fun x => μ i * x) (row_ratio i)

/-- Change one prototype while keeping a positive anchor in its cell:
the two positive stationary completion outputs MUST differ. This does not
infer utility of an arbitrary scalar observable from object strictness. -/
theorem retained_prototype_split {d : ℕ} (E₀ E₁ : Fin d → Fin d → ℚ)
    (μ₀ μ₁ w₀ w₁ : Fin d → ℚ) (u v : Fin d)
    (ratio₀ : ∀ i, E₀ i u * w₀ v = E₀ i v * w₀ u)
    (ratio₁ : ∀ i, E₁ i u * w₁ v = E₁ i v * w₁ u)
    (fixed₀ : ∀ j, ∑ i : Fin d, μ₀ i * E₀ i j = μ₀ j)
    (fixed₁ : ∀ j, ∑ i : Fin d, μ₁ i * E₁ i j = μ₁ j)
    (anchor : w₀ v = w₁ v) (changed : w₀ u ≠ w₁ u)
    (positive : 0 < μ₀ v) : μ₀ ≠ μ₁ := by
  intro eq
  have h0 := completion_stationary_ratio E₀ μ₀ w₀ u v ratio₀ fixed₀
  have h1 := completion_stationary_ratio E₁ μ₁ w₁ u v ratio₁ fixed₁
  rw [← eq, ← anchor] at h1
  have h : μ₀ v * w₀ u = μ₀ v * w₁ u := h0.symm.trans h1
  exact changed ((mul_left_cancel₀ positive.ne') h)

/-- Noise can join two stochastic preimages exactly if their midpoint
compensations are legal. No approximate collision or rounding is used. -/
theorem midpoint_noise_recouples (W₀ W₁ : ℚ) :
    W₀ + ((W₀ + W₁) / 2 - W₀) =
      W₁ + ((W₀ + W₁) / 2 - W₁) := by ring

end CantorAudit
