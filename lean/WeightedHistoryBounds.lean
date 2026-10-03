import HistoryConditioning

/-! Collatz bounds for every NONAUTONOMOUS product, using one positive test
vector shared by all allowed blocks. This is the return needed for a continuum
of legal input words; a periodic eigenvalue calculation alone is insufficient.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass
variable {X : Type*} {d : ℕ} [NeZero d]

theorem weighted_matrixHistory_bounds (F : X → X)
    (A : X → Matrix (Fin d) (Fin d) ℝ) (nonneg : ∀ x i j, 0 ≤ A x i j)
    (v : Fin d → ℝ) (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (rows : ∀ x i, a*v i ≤ ∑ j, A x i j*v j ∧
      (∑ j, A x i j*v j) ≤ b*v i)
    (n : ℕ) (x : X) (i : Fin d) :
    a^n*v i ≤ ∑ j, kernelProduct F A n x i j*v j ∧
      (∑ j, kernelProduct F A n x i j*v j) ≤ b^n*v i := by
  induction n generalizing x i with
  | zero => simp [kernelProduct, Matrix.one_apply]
  | succ n ih =>
    have eq : (∑ j, kernelProduct F A (n+1) x i j*v j) =
        ∑ k, A x i k*(∑ j, kernelProduct F A n (F x) k j*v j) := by
      simp only [kernelProduct, Matrix.mul_apply, Finset.sum_mul]
      rw [Finset.sum_comm]
      simp only [Finset.mul_sum, mul_assoc]
    rw [eq]
    constructor
    · calc
        a^(n+1)*v i = a^n*(a*v i) := by rw [pow_succ]; ring
        _ ≤ a^n*(∑ k, A x i k*v k) :=
          mul_le_mul_of_nonneg_left (rows x i).1 (pow_nonneg ha n)
        _ = ∑ k, A x i k*(a^n*v k) := by rw [Finset.mul_sum]; congr 1; ext k; ring
        _ ≤ _ := Finset.sum_le_sum fun k _ =>
          mul_le_mul_of_nonneg_left (ih (F x) k).1 (nonneg x i k)
    · calc
        _ ≤ ∑ k, A x i k*(b^n*v k) := Finset.sum_le_sum fun k _ =>
          mul_le_mul_of_nonneg_left (ih (F x) k).2 (nonneg x i k)
        _ = b^n*(∑ k, A x i k*v k) := by rw [Finset.mul_sum]; congr 1; ext k; ring
        _ ≤ b^n*(b*v i) := mul_le_mul_of_nonneg_left (rows x i).2 (pow_nonneg hb n)
        _ = b^(n+1)*v i := by rw [pow_succ]; ring

theorem weighted_matrixHistory_norm_bounds (F : X → X)
    (A : X → Matrix (Fin d) (Fin d) ℝ) (nonneg : ∀ x i j, 0 ≤ A x i j)
    (v : Fin d → ℝ) (a b c e : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hc : 0 < c) (he : 0 < e) (vbound : ∀ i, c ≤ v i ∧ v i ≤ e)
    (rows : ∀ x i, a*v i ≤ ∑ j, A x i j*v j ∧
      (∑ j, A x i j*v j) ≤ b*v i) (n : ℕ) (x : X) :
    (c/e)*a^n ≤ ‖kernelProduct F A n x‖ ∧
      ‖kernelProduct F A n x‖ ≤ (e/c)*b^n := by
  let C := kernelProduct F A n x
  have hC : ∀ i j, 0 ≤ C i j := matrixHistory_nonnegative F A nonneg n x
  have bounds := weighted_matrixHistory_bounds F A nonneg v a b ha hb rows n x
  have weighted_lower : ∀ i, c*(∑ j, C i j) ≤ ∑ j, C i j*v j := by
    intro i
    rw [Finset.mul_sum]
    exact Finset.sum_le_sum fun j _ => by
      simpa [mul_comm] using mul_le_mul_of_nonneg_left (vbound j).1 (hC i j)
  have weighted_upper : ∀ i, (∑ j, C i j*v j) ≤ e*(∑ j, C i j) := by
    intro i
    rw [Finset.mul_sum]
    exact Finset.sum_le_sum fun j _ => by
      simpa [mul_comm] using mul_le_mul_of_nonneg_left (vbound j).2 (hC i j)
  constructor
  · have h := calc
        a^n*c ≤ a^n*v 0 := mul_le_mul_of_nonneg_left (vbound 0).1 (pow_nonneg ha n)
        _ ≤ ∑ j, C 0 j*v j := (bounds 0).1
        _ ≤ e*(∑ j, C 0 j) := weighted_upper 0
        _ ≤ e*‖C‖ := mul_le_mul_of_nonneg_left (positiveMatrix_row_le_norm C hC 0) he.le
    have eq : (c/e)*a^n = (a^n*c)/e := by ring
    rw [eq]
    exact (div_le_iff he).mpr (by simpa [mul_comm] using h)
  · apply positiveMatrix_norm_le C hC _ (mul_nonneg (div_nonneg he.le hc.le) (pow_nonneg hb n))
    intro i
    have h := calc
        c*(∑ j, C i j) ≤ ∑ j, C i j*v j := weighted_lower i
        _ ≤ b^n*v i := (bounds i).2
        _ ≤ b^n*e := mul_le_mul_of_nonneg_left (vbound i).2 (pow_nonneg hb n)
    have hdiv := (le_div_iff hc).mpr (by simpa [mul_comm] using h)
    convert hdiv using 1
    ring

end
end CantorAudit
