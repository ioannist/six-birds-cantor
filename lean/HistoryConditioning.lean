import ConditionalPressure

/-! Conditioning the original NONAUTONOMOUS history cocycle. Full support
of a fixed initial probability law is sufficient; neither one-step nor
all-time strict positivity of the kernels is required. This covers the same
history potential and future evolution. Restricting the hybrid-state carrier
or imposing an every-time history event is a different conditioning operation.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass
variable {d : ℕ} [NeZero d] {X : Type*} [Nonempty X]

def rowHistoryPartition (C : Matrix (Fin d) (Fin d) ℝ) (p : Fin d → ℝ) : ℝ :=
  ∑ i, p i*(∑ j, C i j)

theorem full_support_history_bounds (C : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ C i j) (p : Fin d → ℝ) (c : ℝ) (hc : 0 < c)
    (floor : ∀ i, c ≤ p i) (mass : ∑ i, p i = 1) :
    c*‖C‖ ≤ rowHistoryPartition C p ∧ rowHistoryPartition C p ≤ ‖C‖ := by
  have hp : ∀ i, 0 ≤ p i := fun i => hc.le.trans (floor i)
  have rowspos : ∀ i, 0 ≤ ∑ j, C i j := fun i => Finset.sum_nonneg fun j _ => nonneg i j
  have partitionpos : 0 ≤ rowHistoryPartition C p :=
    Finset.sum_nonneg fun i _ => mul_nonneg (hp i) (rowspos i)
  have lower : ∀ i, c*(∑ j, C i j) ≤ rowHistoryPartition C p := by
    intro i
    have h := mul_le_mul_of_nonneg_right (floor i) (rowspos i)
    exact h.trans (Finset.single_le_sum (fun j _ => mul_nonneg (hp j) (rowspos j))
      (Finset.mem_univ i))
  have normbound := positiveMatrix_norm_le C nonneg (rowHistoryPartition C p/c)
    (div_nonneg partitionpos hc.le) (fun i => (le_div_iff hc).mpr (by simpa [mul_comm] using lower i))
  refine ⟨?_, ?_⟩
  · have h := (le_div_iff hc).mp normbound
    simpa only [mul_comm] using h
  · calc
      _ ≤ ∑ i, p i*‖C‖ := Finset.sum_le_sum fun i _ =>
        mul_le_mul_of_nonneg_left (positiveMatrix_row_le_norm C nonneg i) (hp i)
      _ = ‖C‖ := by rw [← Finset.sum_mul, mass, one_mul]

theorem full_support_history_same_pressure (C : ℕ → Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ n i j, 0 ≤ C n i j) (positive_norm : ∀ n, 0 < ‖C n‖)
    (p : Fin d → ℝ) (positive_p : ∀ i, 0 < p i) (mass : ∑ i, p i = 1)
    (P : ℝ) (limit : Tendsto (fun n => Real.log ‖C n‖/n) atTop (𝓝 P)) :
    Tendsto (fun n => Real.log (rowHistoryPartition (C n) p)/n) atTop (𝓝 P) := by
  obtain ⟨i, _, hi⟩ := Finset.exists_min_image Finset.univ p Finset.univ_nonempty
  apply bounded_factor_same_pressure (fun n => ‖C n‖) (fun n => rowHistoryPartition (C n) p)
    (p i) P (positive_p i) positive_norm ?_ limit
  intro n
  exact full_support_history_bounds (C n) (nonneg n) p (p i) (positive_p i)
    (fun j => hi j (Finset.mem_univ j)) mass

def scalarHistory (F : X → X) (c : X → ℝ) : ℕ → X → ℝ
  | 0, _ => 1
  | n+1, x => c x*scalarHistory F c n (F x)

def stochasticWeightedMatrix (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ)
    (x : X) : Matrix (Fin d) (Fin d) ℝ := fun i j => Real.exp (-q x)*K x i j

theorem scalar_row_history (F : X → X) (A : X → Matrix (Fin d) (Fin d) ℝ)
    (c : X → ℝ) (rows : ∀ x i, ∑ j, A x i j = c x)
    (n : ℕ) (x : X) (i : Fin d) :
    ∑ j, kernelProduct F A n x i j = scalarHistory F c n x := by
  induction n generalizing x i with
  | zero => simp [kernelProduct, scalarHistory, Matrix.one_apply]
  | succ n ih =>
    simp only [kernelProduct, scalarHistory, Matrix.mul_apply]
    rw [Finset.sum_comm]
    simp only [← Finset.mul_sum, ih, ← Finset.sum_mul, rows]

/-- At s=1 the ORIGINAL weighted stochastic cocycle has a scalar row sum
at every step. Even zero coordinates of the initial law cannot change ANY
finite-horizon partition. This includes every selector/noise history in F. -/
theorem stochastic_cocycle_initial_law_independent (F : X → X)
    (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ)
    (nonneg : ∀ x i j, 0 ≤ K x i j) (rows : ∀ x i, ∑ j, K x i j = 1)
    (n : ℕ) (x : X) (p : Fin d → ℝ) (mass : ∑ i, p i = 1) :
    rowHistoryPartition (kernelProduct F (stochasticWeightedMatrix K q) n x) p =
      ‖kernelProduct F (stochasticWeightedMatrix K q) n x‖ := by
  let A : X → Matrix (Fin d) (Fin d) ℝ := stochasticWeightedMatrix K q
  let c : X → ℝ := fun x => Real.exp (-q x)
  have rowsA : ∀ x i, ∑ j, A x i j = c x := by
    intro x i; simp only [A, stochasticWeightedMatrix, c, ← Finset.mul_sum, rows, mul_one]
  have hA : ∀ x i j, 0 ≤ A x i j := fun x i j => mul_nonneg (Real.exp_pos _).le (nonneg x i j)
  have roweq := scalar_row_history F A c rowsA n x
  have hc : ∀ n x, 0 ≤ scalarHistory F c n x := by
    intro n x
    induction n generalizing x with
    | zero => norm_num [scalarHistory]
    | succ n ih => exact mul_nonneg (Real.exp_pos _).le (ih (F x))
  have hC := matrixHistory_nonnegative F A hA n x
  have equal : ‖kernelProduct F A n x‖ = scalarHistory F c n x := by
    apply le_antisymm
    · exact positiveMatrix_norm_le _ hC _ (hc n x) (fun i => (roweq i).le)
    · rw [← roweq 0]; exact positiveMatrix_row_le_norm _ hC 0
  change rowHistoryPartition (kernelProduct F A n x) p = ‖kernelProduct F A n x‖
  simp only [rowHistoryPartition, roweq, ← Finset.sum_mul, mass, one_mul, equal]

end
end CantorAudit
