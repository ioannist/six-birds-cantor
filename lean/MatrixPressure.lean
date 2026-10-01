import KernelCocycle
import AffinityPressure
import Mathlib.Analysis.Matrix

/-! Concrete nonnegative finite-matrix history pressure.  The matrix norm here
is explicitly the maximum absolute row sum, not mathlib's default entrywise
matrix norm.  Exponential bounds are derived from one-step row bounds.
This does not assert that the simulator or its historical shell meets them.
-/
namespace CantorAudit
noncomputable section
open Filter Set
open scoped Topology NNReal

attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass

variable {X : Type*} [Nonempty X] {d : ℕ} [NeZero d]

theorem positiveMatrix_row_le_norm (M : Matrix (Fin d) (Fin d) ℝ)
    (hM : ∀ i j, 0 ≤ M i j) (i : Fin d) :
    (∑ j, M i j) ≤ ‖M‖ := by
  have h := Finset.le_sup (f := fun i => ∑ j, ‖M i j‖₊) (Finset.mem_univ i)
  have hR := NNReal.coe_le_coe.mpr h
  simpa only [Matrix.linfty_opNorm_def, NNReal.coe_sum, coe_nnnorm,
    Real.norm_eq_abs, abs_of_nonneg (hM _ _)] using hR

theorem positiveMatrix_norm_le (M : Matrix (Fin d) (Fin d) ℝ)
    (hM : ∀ i j, 0 ≤ M i j) (b : ℝ) (hb : 0 ≤ b)
    (rows : ∀ i, ∑ j, M i j ≤ b) : ‖M‖ ≤ b := by
  rw [Matrix.linfty_opNorm_def]
  change ((Finset.univ.sup fun i => ∑ j, ‖M i j‖₊ : ℝ≥0) : ℝ) ≤ (⟨b, hb⟩ : ℝ≥0)
  apply NNReal.coe_le_coe.mpr
  apply Finset.sup_le
  intro i _
  apply NNReal.coe_le_coe.mp
  simpa only [NNReal.coe_sum, coe_nnnorm, Real.norm_eq_abs,
    abs_of_nonneg (hM _ _), NNReal.coe_mk] using rows i

theorem matrixHistory_nonnegative (F : X → X)
    (A : X → Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ x i j, 0 ≤ A x i j) (n : ℕ) (x : X) (i j : Fin d) :
    0 ≤ kernelProduct F A n x i j := by
  induction n generalizing x i j with
  | zero => simp [kernelProduct, Matrix.one_apply]; split_ifs <;> norm_num
  | succ n ih =>
    simp only [kernelProduct, Matrix.mul_apply]
    exact Finset.sum_nonneg (fun k _ => mul_nonneg (hA x i k) (ih (F x) k j))

/-- Both all-horizon row estimates come from actual ordered multiplication. -/
theorem matrixHistory_rows (F : X → X) (A : X → Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ x i j, 0 ≤ A x i j) (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (rows : ∀ x i, a ≤ ∑ j, A x i j ∧ (∑ j, A x i j) ≤ b)
    (n : ℕ) (x : X) (i : Fin d) :
    a^n ≤ ∑ j, kernelProduct F A n x i j ∧
      (∑ j, kernelProduct F A n x i j) ≤ b^n := by
  induction n generalizing x i with
  | zero => simp [kernelProduct, Matrix.one_apply]
  | succ n ih =>
    have eq : (∑ j, kernelProduct F A (n+1) x i j) =
        ∑ k, A x i k * ∑ j, kernelProduct F A n (F x) k j := by
      simp only [kernelProduct, Matrix.mul_apply]
      rw [Finset.sum_comm]
      simp only [Finset.mul_sum]
    rw [eq]
    constructor
    · calc
        a^(n+1) = a * a^n := by rw [pow_succ]; ring
        _ ≤ (∑ k, A x i k) * a^n :=
          mul_le_mul_of_nonneg_right (rows x i).1 (pow_nonneg ha n)
        _ = ∑ k, A x i k * a^n := by rw [Finset.sum_mul]
        _ ≤ _ := Finset.sum_le_sum fun k _ =>
          mul_le_mul_of_nonneg_left (ih (F x) k).1 (hA x i k)
    · calc
        _ ≤ ∑ k, A x i k * b^n := Finset.sum_le_sum fun k _ =>
          mul_le_mul_of_nonneg_left (ih (F x) k).2 (hA x i k)
        _ = (∑ k, A x i k) * b^n := by rw [Finset.sum_mul]
        _ ≤ b * b^n := mul_le_mul_of_nonneg_right (rows x i).2 (pow_nonneg hb n)
        _ = b^(n+1) := by rw [pow_succ]; ring

noncomputable def matrixHistoryEnvelope (F : X → X)
    (A : X → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) : ℝ :=
  kernelEnvelope F A n

theorem matrix_pressure_exists (F : X → X) (A : X → Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ x i j, 0 ≤ A x i j) (a b : ℝ) (ha : 0 < a) (hb : 0 ≤ b)
    (rows : ∀ x i, a ≤ ∑ j, A x i j ∧ (∑ j, A x i j) ≤ b) :
    ∃ P : ℝ, Tendsto (fun n => Real.log (matrixHistoryEnvelope F A n) / n)
      atTop (𝓝 P) := by
  apply kernel_pressure_exists F A a b ha
  · intro n x
    exact ((matrixHistory_rows F A hA a b ha.le hb rows n x 0).1).trans
      (positiveMatrix_row_le_norm _ (matrixHistory_nonnegative F A hA n x) 0)
  · intro n x
    exact positiveMatrix_norm_le _ (matrixHistory_nonnegative F A hA n x)
      (b^n) (pow_nonneg hb n)
      (fun i => (matrixHistory_rows F A hA a b ha.le hb rows n x i).2)

theorem constant_matrixHistory (M : Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (x : Unit) :
    kernelProduct id (fun _ => M) n x = M^n := by
  induction n with
  | zero => simp [kernelProduct]
  | succ n ih => simp [kernelProduct, ih, pow_succ']

theorem constant_matrixHistoryEnvelope (M : Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    matrixHistoryEnvelope (id : Unit → Unit) (fun _ => M) n = ‖M^n‖ := by
  simp [matrixHistoryEnvelope, kernelEnvelope, constant_matrixHistory, Set.range_const]

theorem matrixPathValue_eq_row (M : Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (i : Fin d) :
    matrixPathValue M n i = ∑ j, (M^n) i j := by
  induction n generalizing i with
  | zero => simp [matrixPathValue, Matrix.one_apply]
  | succ n ih =>
    simp only [matrixPathValue, ih, pow_succ', Matrix.mul_apply]
    rw [Finset.sum_comm]
    simp only [Finset.mul_sum]

noncomputable def positiveMatrixPartition (M : Matrix (Fin d) (Fin d) ℝ)
    (p : Fin d → ℝ) (n : ℕ) : ℝ := ∑ i, p i * matrixPathValue M n i

/-- Positive entries make any initial probability law, even one with zeros,
comparable to the maximum-row history partition. -/
theorem positiveMatrixPartition_bounds (M : Matrix (Fin d) (Fin d) ℝ)
    (p : Fin d → ℝ) (a b : ℝ) (ha : 0 < a)
    (entries : ∀ i j, a ≤ M i j ∧ M i j ≤ b)
    (hp : ∀ i, 0 ≤ p i) (mass : ∑ i, p i = 1) (n : ℕ) :
    a / b * ‖M^n‖ ≤ positiveMatrixPartition M p n ∧
      positiveMatrixPartition M p n ≤ ‖M^n‖ := by
  have hab : a ≤ b := (entries 0 0).1.trans (entries 0 0).2
  have hb : 0 < b := ha.trans_le hab
  have hM : ∀ i j, 0 ≤ M i j := fun i j => ha.le.trans (entries i j).1
  have powerpos : ∀ (n : ℕ) (i j : Fin d), 0 ≤ (M^n) i j := by
    intro n i j
    have h := matrixHistory_nonnegative (id : Unit → Unit) (fun _ => M)
      (fun _ => hM) n () i j
    simpa only [constant_matrixHistory] using h
  have pathpos : ∀ n i, 0 ≤ matrixPathValue M n i := by
    intro n i
    rw [matrixPathValue_eq_row]
    exact Finset.sum_nonneg fun j _ => powerpos n i j
  have partitionpos : 0 ≤ positiveMatrixPartition M p n :=
    Finset.sum_nonneg fun i _ => mul_nonneg (hp i) (pathpos n i)
  have upper : positiveMatrixPartition M p n ≤ ‖M^n‖ := by
    calc
      _ ≤ ∑ i, p i * ‖M^n‖ := by
        apply Finset.sum_le_sum; intro i _
        apply mul_le_mul_of_nonneg_left _ (hp i)
        rw [matrixPathValue_eq_row]
        exact positiveMatrix_row_le_norm _ (powerpos n) i
      _ = ‖M^n‖ := by rw [← Finset.sum_mul, mass, one_mul]
  refine ⟨?_, upper⟩
  cases n with
  | zero =>
    simpa [positiveMatrixPartition, matrixPathValue, mass] using (div_le_one hb).mpr hab
  | succ n =>
    have compare : ∀ i k, a / b * matrixPathValue M (n+1) k ≤
        matrixPathValue M (n+1) i := by
      intro i k
      simp only [matrixPathValue, Finset.mul_sum]
      apply Finset.sum_le_sum; intro j _
      rw [← mul_assoc]
      apply mul_le_mul_of_nonneg_right _ (pathpos n j)
      calc
        a / b * M k j ≤ a / b * b :=
          mul_le_mul_of_nonneg_left (entries k j).2 (div_nonneg ha.le hb.le)
        _ = a := by field_simp
        _ ≤ M i j := (entries i j).1
    have rows : ∀ k, matrixPathValue M (n+1) k ≤
        positiveMatrixPartition M p (n+1) / (a/b) := by
      intro k
      apply (le_div_iff (div_pos ha hb)).mpr
      calc
        matrixPathValue M (n+1) k * (a/b) =
            ∑ i, p i * (a/b * matrixPathValue M (n+1) k) := by
          rw [← Finset.sum_mul, mass, one_mul]; ring
        _ ≤ positiveMatrixPartition M p (n+1) :=
          Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (compare i k) (hp i)
    have normbound := positiveMatrix_norm_le (M^(n+1)) (powerpos (n+1))
      (positiveMatrixPartition M p (n+1) / (a/b))
      (div_nonneg (Finset.sum_nonneg fun i _ => mul_nonneg (hp i) (pathpos (n+1) i))
        (div_nonneg ha.le hb.le))
      (fun k => by simpa [matrixPathValue_eq_row] using rows k)
    have h := (le_div_iff (div_pos ha hb)).mp normbound
    simpa [mul_comm] using h

/-- Existence for the actual path partition, without assuming a pressure
limit or strictly positive initial density. -/
theorem positiveMatrixPartition_pressure_exists (M : Matrix (Fin d) (Fin d) ℝ)
    (p : Fin d → ℝ) (a b : ℝ) (ha : 0 < a)
    (entries : ∀ i j, a ≤ M i j ∧ M i j ≤ b)
    (hp : ∀ i, 0 ≤ p i) (mass : ∑ i, p i = 1) :
    ∃ P : ℝ, Tendsto (fun n => Real.log (positiveMatrixPartition M p n) / n)
      atTop (𝓝 P) := by
  have hab : a ≤ b := (entries 0 0).1.trans (entries 0 0).2
  have hb : 0 < b := ha.trans_le hab
  have hd : (0 : ℝ) < d := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne d)
  have hM : ∀ i j, 0 ≤ M i j := fun i j => ha.le.trans (entries i j).1
  have rows : ∀ (_ : Unit) i, (d:ℝ)*a ≤ ∑ j, M i j ∧ (∑ j, M i j) ≤ (d:ℝ)*b := by
    intro _ i
    constructor
    · simpa using Finset.sum_le_sum (s := Finset.univ) (fun j _ => (entries i j).1)
    · simpa using Finset.sum_le_sum (s := Finset.univ) (fun j _ => (entries i j).2)
  obtain ⟨P, hP⟩ := matrix_pressure_exists (id : Unit → Unit) (fun _ => M)
    (fun _ => hM) ((d:ℝ)*a) ((d:ℝ)*b) (mul_pos hd ha) (mul_pos hd hb).le rows
  simp only [constant_matrixHistoryEnvelope] at hP
  refine ⟨P, bounded_factor_same_pressure (fun n => ‖M^n‖)
    (positiveMatrixPartition M p) (a/b) P (div_pos ha hb) ?_ ?_ hP⟩
  · intro n
    have bounds := matrixHistory_rows (id : Unit → Unit) (fun _ => M)
      (fun _ => hM) ((d:ℝ)*a) ((d:ℝ)*b) (mul_pos hd ha).le (mul_pos hd hb).le rows n () 0
    have hnorm := positiveMatrix_row_le_norm _
      (matrixHistory_nonnegative (id : Unit → Unit) (fun _ => M) (fun _ => hM) n ()) 0
    have pos := lt_of_lt_of_le (pow_pos (mul_pos hd ha) n) (bounds.1.trans hnorm)
    simpa only [constant_matrixHistory] using pos
  · exact positiveMatrixPartition_bounds M p a b ha entries hp mass

theorem finite_positive_matrix_bounds (M : Matrix (Fin d) (Fin d) ℝ)
    (positive : ∀ i j, 0 < M i j) :
    ∃ a b : ℝ, 0 < a ∧ ∀ i j, a ≤ M i j ∧ M i j ≤ b := by
  obtain ⟨lo, _, hlo⟩ := Finset.exists_min_image Finset.univ
    (fun ij : Fin d × Fin d => M ij.1 ij.2) Finset.univ_nonempty
  obtain ⟨hi, _, hhi⟩ := Finset.exists_max_image Finset.univ
    (fun ij : Fin d × Fin d => M ij.1 ij.2) Finset.univ_nonempty
  exact ⟨M lo.1 lo.2, M hi.1 hi.2, positive _ _, fun i j =>
    ⟨hlo (i,j) (Finset.mem_univ _), hhi (i,j) (Finset.mem_univ _)⟩⟩

theorem matrixPathValue_positive (M : Matrix (Fin d) (Fin d) ℝ)
    (positive : ∀ i j, 0 < M i j) (n : ℕ) (i : Fin d) :
    0 < matrixPathValue M n i := by
  induction n generalizing i with
  | zero => simp [matrixPathValue]
  | succ n ih =>
    exact Finset.sum_pos (fun j _ => mul_pos (positive i j) (ih j)) Finset.univ_nonempty

theorem positiveMatrixPartition_positive (M : Matrix (Fin d) (Fin d) ℝ)
    (positive : ∀ i j, 0 < M i j) (p : Fin d → ℝ)
    (hp : ∀ i, 0 ≤ p i) (mass : ∑ i, p i = 1) (n : ℕ) :
    0 < positiveMatrixPartition M p n := by
  have hex : ∃ i, 0 < p i := by
    by_contra h
    push_neg at h
    have zero : ∀ i, p i = 0 := fun i => le_antisymm (h i) (hp i)
    simp only [zero, Finset.sum_const_zero] at mass
    norm_num at mass
  obtain ⟨i, hi⟩ := hex
  apply Finset.sum_pos'
  · intro j _; exact mul_nonneg (hp j) (matrixPathValue_positive M positive n j).le
  · exact ⟨i, Finset.mem_univ i, mul_pos hi (matrixPathValue_positive M positive n i)⟩

theorem positiveMatrixPartition_pressure_exists_of_positive
    (M : Matrix (Fin d) (Fin d) ℝ) (positive : ∀ i j, 0 < M i j)
    (p : Fin d → ℝ) (hp : ∀ i, 0 ≤ p i) (mass : ∑ i, p i = 1) :
    ∃ P : ℝ, Tendsto (fun n => Real.log (positiveMatrixPartition M p n) / n)
      atTop (𝓝 P) := by
  obtain ⟨a,b,ha,entries⟩ := finite_positive_matrix_bounds M positive
  exact positiveMatrixPartition_pressure_exists M p a b ha entries hp mass

noncomputable def affinityMatrix (E R : Matrix (Fin d) (Fin d) ℝ) :
    Matrix (Fin d) (Fin d) ℝ := fun i j => Real.sqrt (E i j) * Real.sqrt (R i j)

/-- The concrete completed-path pressure exists and is strictly negative.
The one-step discrepancy is the visible, target-specific premise; neither
existence nor an all-horizon pressure loss is assumed. -/
theorem affinity_pressure_exists_strict (E R : Matrix (Fin d) (Fin d) ℝ)
    (hE : ∀ i j, 0 < E i j) (hR : ∀ i j, 0 < R i j)
    (massE : ∀ i, ∑ j, E i j = 1) (massR : ∀ i, ∑ j, R i j = 1)
    (p : Fin d → ℝ) (hp : ∀ i, 0 ≤ p i) (massp : ∑ i, p i = 1)
    (ell : ℝ) (hell : 0 < ell)
    (loss : ∀ i, ell ≤ (∑ j, |E i j - R i j|)^2 / 8) :
    ∃ Q : ℝ,
      Tendsto (fun n => Real.log (positiveMatrixPartition (affinityMatrix E R) p n) / n)
        atTop (𝓝 Q) ∧ Q ≤ Real.log (1-ell) ∧ Q < 0 := by
  have hM : ∀ i j, 0 < affinityMatrix E R i j := fun i j =>
    mul_pos (Real.sqrt_pos.mpr (hE i j)) (Real.sqrt_pos.mpr (hR i j))
  have rows : ∀ i, ∑ j, affinityMatrix E R i j ≤ 1-ell := by
    intro i
    have h := sqrt_affinity_row_loss (E i) (R i) (fun j => (hE i j).le)
      (fun j => (hR i j).le) (massE i) (massR i)
    exact h.trans (by linarith [loss i])
  have hc : 0 < 1-ell := (Finset.sum_pos (fun j _ => hM 0 j)
    Finset.univ_nonempty).trans_le (rows 0)
  obtain ⟨Q, hQ⟩ := positiveMatrixPartition_pressure_exists_of_positive
    (affinityMatrix E R) hM p hp massp
  have hbound : Q ≤ Real.log (1-ell) := pressure_upper_of_exponential
    (positiveMatrixPartition (affinityMatrix E R) p) (1-ell) Q hc
    (positiveMatrixPartition_positive _ hM p hp massp)
    (fun n => matrix_partition_exponential_loss _ p (1-ell) (fun i j => (hM i j).le)
      hc.le rows hp massp n) hQ
  exact ⟨Q, hQ, hbound, hbound.trans_lt (Real.log_neg hc (by linarith))⟩

/-- The reference channel and the equal-operator control have zero pressure. -/
theorem stochasticMatrix_partition_one (M : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (p : Fin d → ℝ) (mass : ∑ i, p i = 1)
    (n : ℕ) : positiveMatrixPartition M p n = 1 := by
  have h : ∀ n i, matrixPathValue M n i = 1 := by
    intro n i
    induction n generalizing i with
    | zero => rfl
    | succ n ih => simpa only [matrixPathValue, ih, mul_one] using rows i
  simpa only [positiveMatrixPartition, h, mul_one] using mass

theorem stochasticMatrix_pressure_zero (M : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (p : Fin d → ℝ) (mass : ∑ i, p i = 1) :
    Tendsto (fun n => Real.log (positiveMatrixPartition M p n) / n) atTop (𝓝 0) := by
  simp only [stochasticMatrix_partition_one M rows p mass, Real.log_one, zero_div]
  exact tendsto_const_nhds

theorem affinityMatrix_self (E : Matrix (Fin d) (Fin d) ℝ)
    (hE : ∀ i j, 0 ≤ E i j) : affinityMatrix E E = E := by
  funext i j
  exact Real.mul_self_sqrt (hE i j)

/-- A common row discrepancy yields a strictly positive weighted pressure
gap for every probability weighting, including weights with zero entries. -/
theorem weighted_affinity_pressure_gap {Z : Type*} [Fintype Z]
    (Q w : Z → ℝ) (ell : ℝ) (hell : 0 < ell) (hc : 0 < 1-ell)
    (hw : ∀ z, 0 ≤ w z) (mass : ∑ z, w z = 1)
    (bound : ∀ z, Q z ≤ Real.log (1-ell)) :
    ell ≤ -(∑ z, w z * Q z) ∧ 0 < -(∑ z, w z * Q z) := by
  have hsum : (∑ z, w z * Q z) ≤ Real.log (1-ell) := by
    calc
      _ ≤ ∑ z, w z * Real.log (1-ell) := Finset.sum_le_sum fun z _ =>
        mul_le_mul_of_nonneg_left (bound z) (hw z)
      _ = Real.log (1-ell) := by rw [← Finset.sum_mul, mass, one_mul]
  have hlog := Real.log_le_sub_one_of_pos hc
  have hgap : ell ≤ -(∑ z, w z * Q z) := by linarith
  exact ⟨hgap, hell.trans_le hgap⟩

end
end CantorAudit
