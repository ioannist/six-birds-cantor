import KernelEscape
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-! A true relative-likelihood history pressure loss, separate from merely
conditioning a fixed positive history matrix by its initial probability law.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology

theorem affinity_row_loss {d : ℕ} (u v : Fin d → ℝ)
    (hu : ∀ i, 0 ≤ u i) (hv : ∀ i, 0 ≤ v i)
    (hu2 : ∑ i, (u i)^2 = 1) (hv2 : ∑ i, (v i)^2 = 1) :
    (∑ i, u i * v i) ≤ 1 - (∑ i, |(u i)^2 - (v i)^2|)^2 / 8 := by
  have hm : (∑ i, (u i - v i)^2) = 2 - 2 * (∑ i, u i * v i) := by
    calc
      _ = ∑ i, ((u i)^2 + (v i)^2 - 2 * (u i * v i)) := by
        apply Finset.sum_congr rfl; intro i _; ring
      _ = _ := by simp [Finset.sum_sub_distrib, Finset.sum_add_distrib,
        ← Finset.mul_sum, hu2, hv2]; ring
  have hp : (∑ i, (u i + v i)^2) = 2 + 2 * (∑ i, u i * v i) := by
    calc
      _ = ∑ i, ((u i)^2 + (v i)^2 + 2 * (u i * v i)) := by
        apply Finset.sum_congr rfl; intro i _; ring
      _ = _ := by simp [Finset.sum_add_distrib, ← Finset.mul_sum, hu2, hv2]; ring
  have hmpos : 0 ≤ 2 - 2 * (∑ i, u i * v i) := by
    rw [← hm]; exact Finset.sum_nonneg (fun _ _ => sq_nonneg _)
  have hple : (∑ i, (u i + v i)^2) ≤ 4 := by rw [hp]; linarith
  have habs : (∑ i, |(u i)^2 - (v i)^2|) = ∑ i, |u i - v i| * (u i + v i) := by
    apply Finset.sum_congr rfl
    intro i _
    rw [show (u i)^2 - (v i)^2 = (u i - v i) * (u i + v i) by ring,
      abs_mul, abs_of_nonneg (add_nonneg (hu i) (hv i))]
  have hcs := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ
    (fun i => |u i - v i|) (fun i => u i + v i)
  simp only [sq_abs] at hcs
  rw [← habs, hm] at hcs
  have hbound := mul_le_mul_of_nonneg_left hple hmpos
  have hfinal := hcs.trans hbound
  nlinarith only [hfinal]

theorem sqrt_affinity_row_loss {d : ℕ} (p q : Fin d → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hq : ∀ i, 0 ≤ q i)
    (pmass : ∑ i, p i = 1) (qmass : ∑ i, q i = 1) :
    (∑ i, Real.sqrt (p i) * Real.sqrt (q i)) ≤
      1 - (∑ i, |p i - q i|)^2 / 8 := by
  have h := affinity_row_loss (fun i => Real.sqrt (p i)) (fun i => Real.sqrt (q i))
    (fun _ => Real.sqrt_nonneg _) (fun _ => Real.sqrt_nonneg _)
    (by simpa only [Real.sq_sqrt (hp _)] using pmass)
    (by simpa only [Real.sq_sqrt (hq _)] using qmass)
  simpa only [Real.sq_sqrt (hp _), Real.sq_sqrt (hq _)] using h

def matrixPathValue {d : ℕ} (M : Fin d → Fin d → ℝ) : ℕ → Fin d → ℝ
  | 0, _ => 1
  | n + 1, i => ∑ j, M i j * matrixPathValue M n j

/-- Derive the exponential all-horizon loss from a row bound; it is not
supplied as a pressure-gap-shaped premise. -/
theorem matrixPathValue_upper {d : ℕ} (M : Fin d → Fin d → ℝ) (c : ℝ)
    (hM : ∀ i j, 0 ≤ M i j) (hc : 0 ≤ c)
    (rows : ∀ i, ∑ j, M i j ≤ c) (n : ℕ) (i : Fin d) :
    matrixPathValue M n i ≤ c^n := by
  induction n generalizing i with
  | zero => simp [matrixPathValue]
  | succ n ih =>
    calc
      matrixPathValue M (n+1) i ≤ ∑ j, M i j * c^n := by
        apply Finset.sum_le_sum; intro j _
        exact mul_le_mul_of_nonneg_left (ih j) (hM i j)
      _ = (∑ j, M i j) * c^n := by rw [Finset.sum_mul]
      _ ≤ c * c^n := mul_le_mul_of_nonneg_right (rows i) (pow_nonneg hc n)
      _ = c^(n+1) := by rw [pow_succ]; ring

theorem matrix_partition_exponential_loss {d : ℕ} (M : Fin d → Fin d → ℝ)
    (p : Fin d → ℝ) (c : ℝ) (hM : ∀ i j, 0 ≤ M i j) (hc : 0 ≤ c)
    (rows : ∀ i, ∑ j, M i j ≤ c)
    (hp : ∀ i, 0 ≤ p i) (mass : ∑ i, p i = 1) (n : ℕ) :
    ∑ i, p i * matrixPathValue M n i ≤ c^n := by
  calc
    _ ≤ ∑ i, p i * c^n := by
      apply Finset.sum_le_sum; intro i _
      exact mul_le_mul_of_nonneg_left (matrixPathValue_upper M c hM hc rows n i) (hp i)
    _ = (∑ i, p i) * c^n := by rw [Finset.sum_mul]
    _ = c^n := by rw [mass, one_mul]

/-- The limit step is separate from existence, now supplied for concrete
positive matrices by MatrixPressure. Its exponential input comes from the
theorem above. -/
theorem pressure_upper_of_exponential (Z : ℕ → ℝ) (c Q : ℝ)
    (_hc : 0 < c) (positive : ∀ n, 0 < Z n) (upper : ∀ n, Z n ≤ c^n)
    (limit : Tendsto (fun n => Real.log (Z n) / n) atTop (𝓝 Q)) :
    Q ≤ Real.log c := by
  apply le_of_tendsto limit
  filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  have h := Real.log_le_log (positive n) (upper n)
  rw [Real.log_pow] at h
  exact (div_le_iff hnR).mpr (by nlinarith)

end
end CantorAudit
