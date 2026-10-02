import CompletionAffinityWitness

/-! Support for the original fixed-state completion saturation claim.
For a positive stochastic completion operator, every mass-one real initial
vector converges to its stationary vector. The fixed operator is held fixed;
this does not assert persistence under the unrelated outer substrate update.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology

def completionIterate {d : ℕ} (M : Fin d → Fin d → ℝ) (μ : Fin d → ℝ) : ℕ → Fin d → ℝ
  | 0, j => μ j
  | n+1, j => ∑ i, completionIterate M μ n i * M i j

theorem completionIterate_mass {d : ℕ} (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (μ : Fin d → ℝ) (n : ℕ) :
    ∑ j, completionIterate M μ n j = ∑ j, μ j := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [completionIterate]
    rw [Finset.sum_comm]
    simp only [← Finset.mul_sum, rows, mul_one]
    exact ih

/-- The one-step contraction is derived by subtracting the common positive
entry floor and using zero total mass, not assumed as a closure premise. -/
theorem stochastic_zero_mass_contraction {d : ℕ}
    (M : Fin d → Fin d → ℝ) (rows : ∀ i, ∑ j, M i j = 1)
    (ε : ℝ) (floor : ∀ i j, ε ≤ M i j) (v : Fin d → ℝ) (mass : ∑ i, v i = 0) :
    (∑ j, |∑ i, v i * M i j|) ≤ (1-(d:ℝ)*ε) * ∑ i, |v i| := by
  have shifted : ∀ j, (∑ i, v i * M i j) = ∑ i, v i * (M i j - ε) := by
    intro j
    simp only [mul_sub, Finset.sum_sub_distrib, ← Finset.sum_mul, mass, zero_mul, sub_zero]
  calc
    _ = ∑ j, |∑ i, v i * (M i j-ε)| := by simp only [shifted]
    _ ≤ ∑ j, ∑ i, |v i * (M i j-ε)| :=
      Finset.sum_le_sum fun j _ => Finset.abs_sum_le_sum_abs _ _
    _ = ∑ i, |v i| * (1-(d:ℝ)*ε) := by
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro i _
      simp only [abs_mul, abs_of_nonneg (sub_nonneg.mpr (floor i _)),
        ← Finset.mul_sum, Finset.sum_sub_distrib, rows]
      simp
    _ = _ := by rw [← Finset.sum_mul]; ring

theorem completionIterate_error {d : ℕ} (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (ε : ℝ) (floor : ∀ i j, ε ≤ M i j)
    (hc : 0 ≤ 1-(d:ℝ)*ε) (μ p : Fin d → ℝ)
    (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixed : ∀ j, ∑ i, p i * M i j = p j) (n : ℕ) :
    (∑ j, |completionIterate M μ n j - p j|) ≤
      (1-(d:ℝ)*ε)^n * ∑ j, |μ j-p j| := by
  induction n with
  | zero => simp [completionIterate]
  | succ n ih =>
    have mass : ∑ i, (completionIterate M μ n i-p i) = 0 := by
      rw [Finset.sum_sub_distrib, completionIterate_mass M rows μ n, massμ, massp]; ring
    have h := stochastic_zero_mass_contraction M rows ε floor
      (fun i => completionIterate M μ n i-p i) mass
    have eq : ∀ j, completionIterate M μ (n+1) j - p j =
        ∑ i, (completionIterate M μ n i-p i) * M i j := by
      intro j
      simp only [completionIterate, sub_mul, Finset.sum_sub_distrib, fixed]
    simp only [eq]
    calc
      _ ≤ (1-(d:ℝ)*ε) * ∑ j, |completionIterate M μ n j-p j| := h
      _ ≤ (1-(d:ℝ)*ε) * ((1-(d:ℝ)*ε)^n * ∑ j, |μ j-p j|) :=
        mul_le_mul_of_nonneg_left ih hc
      _ = _ := by rw [pow_succ]; ring

/-- Exact saturation: all mass-one real starts have the same fixed-state
completion limit, with no finite sample or rounded-cycle premise. -/
theorem completionIterate_converges {d : ℕ} (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (ε : ℝ) (floor : ∀ i j, ε ≤ M i j)
    (hc : 0 ≤ 1-(d:ℝ)*ε) (hc1 : 1-(d:ℝ)*ε < 1)
    (μ p : Fin d → ℝ) (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixed : ∀ j, ∑ i, p i * M i j = p j) (j : Fin d) :
    Tendsto (fun n => completionIterate M μ n j) atTop (𝓝 (p j)) := by
  have hlim : Tendsto (fun n : ℕ => (1-(d:ℝ)*ε)^n * ∑ k, |μ k-p k|)
      atTop (𝓝 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hc hc1).mul_const (∑ k, |μ k-p k|)
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  apply squeeze_zero (fun n => norm_nonneg _) _ hlim
  intro n
  rw [Real.norm_eq_abs]
  exact (Finset.single_le_sum (fun k _ => abs_nonneg (completionIterate M μ n k-p k))
    (Finset.mem_univ j)).trans
    (completionIterate_error M rows ε floor hc μ p massμ massp fixed n)

theorem completion_fixed_unique {d : ℕ} (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (ε : ℝ) (floor : ∀ i j, ε ≤ M i j)
    (hc1 : 1-(d:ℝ)*ε < 1) (μ p : Fin d → ℝ)
    (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixedμ : ∀ j, ∑ i, μ i * M i j = μ j)
    (fixedp : ∀ j, ∑ i, p i * M i j = p j) : μ = p := by
  have mass : ∑ i, (μ i-p i) = 0 := by rw [Finset.sum_sub_distrib, massμ, massp]; ring
  have h := stochastic_zero_mass_contraction M rows ε floor (fun i => μ i-p i) mass
  simp only [sub_mul, Finset.sum_sub_distrib, fixedμ, fixedp] at h
  have nonneg : 0 ≤ ∑ i, |μ i-p i| := Finset.sum_nonneg fun i _ => abs_nonneg _
  have zero : (∑ i, |μ i-p i|) = 0 := by nlinarith
  funext j
  have hj := Finset.single_le_sum (fun i _ => abs_nonneg (μ i-p i)) (Finset.mem_univ j)
  rw [zero] at hj
  exact sub_eq_zero.mp (abs_eq_zero.mp (le_antisymm hj (abs_nonneg _)))

/-- Residuals need the geometric-tail denominator before they can justify
separation of stationary objects. This is the source feedback comparison's
mathematical error bridge; floating estimates are not exact certificates. -/
theorem completion_stationary_error_of_residual {d : ℕ}
    (M : Fin d → Fin d → ℝ) (rows : ∀ i, ∑ j, M i j = 1)
    (ε : ℝ) (floor : ∀ i j, ε ≤ M i j) (hδ : 0 < (d:ℝ)*ε)
    (μ p : Fin d → ℝ) (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixed : ∀ j, ∑ i, p i * M i j = p j) :
    (∑ j, |μ j-p j|) ≤ (∑ j, |μ j-∑ i, μ i*M i j|) / ((d:ℝ)*ε) := by
  have mass : ∑ i, (μ i-p i) = 0 := by rw [Finset.sum_sub_distrib, massμ, massp]; ring
  have contraction := stochastic_zero_mass_contraction M rows ε floor (fun i => μ i-p i) mass
  have triangle : (∑ j, |μ j-p j|) ≤
      (∑ j, |μ j-∑ i, μ i*M i j|) + ∑ j, |∑ i, (μ i-p i)*M i j| := by
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_le_sum
    intro j _
    have eq : μ j-p j = (μ j-∑ i, μ i*M i j) + ∑ i, (μ i-p i)*M i j := by
      simp only [sub_mul, Finset.sum_sub_distrib, fixed]; ring
    rw [eq]
    exact abs_add _ _
  apply (le_div_iff hδ).mpr
  nlinarith

end
end CantorAudit
