import PrimitiveCompletion

/-! Global object well-posedness from the actual transport and prototype
inputs. The source derives B>=9/5000 and U_jj>=1/2000 on the revised shell;
the finite source-partition construction and those instance bounds remain
separate analytic/interval obligations. -/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
variable {d : ℕ} [NeZero d]

/-- Construct the unique stationary object of B U and derive convergence of
every mass-one start. No desired stationary vector is an input. -/
theorem positive_prototype_completion_object (B U : Matrix (Fin d) (Fin d) ℝ)
    (nonnegB : ∀ i j, 0 ≤ B i j) (nonnegU : ∀ i j, 0 ≤ U i j)
    (rowsB : ∀ i, ∑ j, B i j = 1) (rowsU : ∀ i, ∑ j, U i j = 1)
    (a b : ℝ) (ha : 0 < a) (hb : 0 < b)
    (floorB : ∀ i j, a ≤ B i j) (diagonalU : ∀ j, b ≤ U j j) :
    ∃ p : Fin d → ℝ,
      (∀ j, 0 < p j) ∧ (∑ i, p i = 1) ∧
      (∀ j, ∑ i, p i*(B*U) i j = p j) ∧
      (∀ v : Fin d → ℝ, (∑ i, v i = 1) →
        (∀ j, ∑ i, v i*(B*U) i j = v j) → v = p) ∧
      (∀ v : Fin d → ℝ, (∑ i, v i = 1) → ∀ j,
        Tendsto (fun n => completionIterate (B*U) v n j) atTop (𝓝 (p j))) := by
  have rows := stochastic_matrix_product B U rowsB rowsU
  have positive : 0 < b*a := mul_pos hb ha
  have floor : ∀ i j, b*a ≤ (B*U) i j := fun i j =>
    (mul_le_mul_of_nonneg_left (floorB i j) hb.le).trans
      (prototype_lift_retains_transport B U nonnegB nonnegU b diagonalU i j)
  obtain ⟨p, hp, mass, fixed⟩ := positive_completion_stationary_exists (B*U) rows
    (b*a) positive floor
  have hd : (0:ℝ) < d := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne d)
  have hlt : 1-(d:ℝ)*(b*a) < 1 := by nlinarith [mul_pos hd positive]
  have hnonneg : 0 ≤ 1-(d:ℝ)*(b*a) := by
    have h := Finset.sum_le_sum (s := Finset.univ) (fun j _ => floor 0 j)
    simp only [Finset.sum_const, Finset.card_fin, nsmul_eq_mul, rows] at h
    linarith
  refine ⟨p, hp, mass, fixed, ?_, ?_⟩
  · intro v hv hf
    exact completion_fixed_unique (B*U) rows (b*a) floor hlt v p hv mass hf fixed
  · intro v hv j
    exact completionIterate_converges (B*U) rows (b*a) floor hnonneg hlt v p hv mass fixed j

end
end CantorAudit
