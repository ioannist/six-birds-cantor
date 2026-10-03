import CompletionForcing

/-! Original-target obstruction: genuine finite initial-law conditioning of
the SAME positive history matrix cannot create a pressure gap. No likelihood
ratio, auxiliary channel, or changed path potential is used here.
This does not identify the paper's unspecified conditional profiles with this
interpretation, or prove original-shell membership for the split example.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass

variable {d : ℕ} [NeZero d]

/-- The correct pressure law for a genuine TWO-fiber disintegration with
fixed strictly positive probabilities. The global pressure is the maximum
conditional pressure, not their weighted mean. Separation still needs an
independent proof; structural non-factorization supplies no such input. -/
theorem binary_disintegration_pressure (Z₀ Z₁ : ℕ → ℝ) (w P₀ P₁ : ℝ)
    (hw : 0 < w) (hw1 : w < 1)
    (positive₀ : ∀ n, 0 < Z₀ n) (positive₁ : ∀ n, 0 < Z₁ n)
    (limit₀ : Tendsto (fun n => Real.log (Z₀ n) / n) atTop (𝓝 P₀))
    (limit₁ : Tendsto (fun n => Real.log (Z₁ n) / n) atTop (𝓝 P₁)) :
    Tendsto (fun n => Real.log (w*Z₀ n + (1-w)*Z₁ n) / n)
      atTop (𝓝 (max P₀ P₁)) := by
  have maximum : Tendsto (fun n => Real.log (max (Z₀ n) (Z₁ n)) / n)
      atTop (𝓝 (max P₀ P₁)) := by
    apply (limit₀.max limit₁).congr'
    filter_upwards [eventually_gt_atTop (0:ℕ)] with n hn
    have hnR : (0:ℝ) ≤ n := by positivity
    change max (Real.log (Z₀ n) / n) (Real.log (Z₁ n) / n) = _
    rw [max_div_div_right hnR]
    congr 1
    rcases le_total (Z₀ n) (Z₁ n) with h | h
    · rw [max_eq_right h, max_eq_right (Real.log_le_log (positive₀ n) h)]
    · rw [max_eq_left h, max_eq_left (Real.log_le_log (positive₁ n) h)]
  apply bounded_factor_same_pressure (fun n => max (Z₀ n) (Z₁ n))
    (fun n => w*Z₀ n+(1-w)*Z₁ n) (min w (1-w)) (max P₀ P₁)
    (lt_min hw (by linarith))
    (fun n => (positive₀ n).trans_le (le_max_left _ _)) ?_ maximum
  intro n
  change min w (1-w) * max (Z₀ n) (Z₁ n) ≤ w*Z₀ n+(1-w)*Z₁ n ∧
    w*Z₀ n+(1-w)*Z₁ n ≤ max (Z₀ n) (Z₁ n)
  constructor
  · rcases le_total (Z₀ n) (Z₁ n) with h | h
    · rw [max_eq_right h]
      have hlow := mul_le_mul_of_nonneg_right (min_le_right w (1-w)) (positive₁ n).le
      have hn := mul_nonneg hw.le (positive₀ n).le
      linarith
    · rw [max_eq_left h]
      have hlow := mul_le_mul_of_nonneg_right (min_le_left w (1-w)) (positive₀ n).le
      have hn := mul_nonneg (by linarith : (0:ℝ) ≤ 1-w) (positive₁ n).le
      linarith
  · have h0 := mul_le_mul_of_nonneg_left (le_max_left (Z₀ n) (Z₁ n)) hw.le
    have h1 := mul_le_mul_of_nonneg_left (le_max_right (Z₀ n) (Z₁ n))
      (by linarith : (0:ℝ) ≤ 1-w)
    nlinarith

/-- Exact separation criterion for that genuine disintegration. It is a
mathematical criterion, not evidence that the original fibers satisfy it. -/
theorem binary_disintegration_gap_positive_iff (w P₀ P₁ : ℝ)
    (hw : 0 < w) (hw1 : w < 1) :
    0 < max P₀ P₁ - (w*P₀+(1-w)*P₁) ↔ P₀ ≠ P₁ := by
  rcases lt_trichotomy P₀ P₁ with h | h | h
  · have formula : max P₀ P₁-(w*P₀+(1-w)*P₁) = w*(P₁-P₀) := by
      rw [max_eq_right h.le]; ring
    rw [formula]
    exact ⟨fun _ => ne_of_lt h, fun _ => mul_pos hw (sub_pos.mpr h)⟩
  · subst P₁
    have formula : max P₀ P₀-(w*P₀+(1-w)*P₀) = 0 := by rw [max_self]; ring
    rw [formula]; simp
  · have formula : max P₀ P₁-(w*P₀+(1-w)*P₁) = (1-w)*(P₀-P₁) := by
      rw [max_eq_left h.le]; ring
    rw [formula]
    exact ⟨fun _ => ne_of_gt h, fun _ => mul_pos (by linarith) (sub_pos.mpr h)⟩

/-- Quantitative endpoint for a genuine equal-weight TWO-WORLD law.
This does not identify the paper's packaged fibers with those worlds. -/
theorem binary_equal_weight_gap (P₀ P₁ : ℝ) :
    max P₀ P₁ - ((1/2)*P₀+(1/2)*P₁) = |P₁-P₀|/2 := by
  rcases le_total P₀ P₁ with h | h
  · rw [max_eq_right h,abs_of_nonneg (sub_nonneg.mpr h)]
    ring
  · rw [max_eq_left h,abs_of_nonpos (sub_nonpos.mpr h)]
    ring

theorem separated_original_continuations_gap_bound (P₀ P₁ : ℝ)
    (separation : (1/1000 : ℝ) < P₁-P₀) :
    (1/2000 : ℝ) < max P₀ P₁ - ((1/2)*P₀+(1/2)*P₁) := by
  rw [binary_equal_weight_gap,abs_of_nonneg (by linarith : 0 ≤ P₁-P₀)]
  linarith

/-- A single pressure works for EVERY initial probability law, including
zeros in that law. The proof derives the common norm limit from entry bounds.
Thus choosing distinct completion fixed objects as initial laws cannot
produce the original gap, for ANY strictly positive matrix potential. -/
theorem initial_conditioning_common_pressure (M : Matrix (Fin d) (Fin d) ℝ)
    (positive : ∀ i j, 0 < M i j) :
    ∃ P : ℝ, ∀ p : Fin d → ℝ, (∀ i, 0 ≤ p i) → (∑ i, p i = 1) →
      Tendsto (fun n => Real.log (positiveMatrixPartition M p n) / n)
        atTop (𝓝 P) := by
  obtain ⟨a, b, ha, entries⟩ := finite_positive_matrix_bounds M positive
  have hab : a ≤ b := (entries 0 0).1.trans (entries 0 0).2
  have hb : 0 < b := ha.trans_le hab
  have hd : (0 : ℝ) < d := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne d)
  have hM : ∀ i j, 0 ≤ M i j := fun i j => (positive i j).le
  have rows : ∀ (_ : Unit) i, (d:ℝ)*a ≤ ∑ j, M i j ∧ (∑ j, M i j) ≤ (d:ℝ)*b := by
    intro _ i
    constructor
    · simpa using Finset.sum_le_sum (s := Finset.univ) (fun j _ => (entries i j).1)
    · simpa using Finset.sum_le_sum (s := Finset.univ) (fun j _ => (entries i j).2)
  obtain ⟨P, hP⟩ := matrix_pressure_exists (id : Unit → Unit) (fun _ => M)
    (fun _ => hM) ((d:ℝ)*a) ((d:ℝ)*b) (mul_pos hd ha) (mul_pos hd hb).le rows
  simp only [constant_matrixHistoryEnvelope] at hP
  refine ⟨P, ?_⟩
  intro p hp mass
  apply bounded_factor_same_pressure (fun n => ‖M^n‖)
    (positiveMatrixPartition M p) (a/b) P (div_pos ha hb) ?_ ?_ hP
  · intro n
    have bounds := matrixHistory_rows (id : Unit → Unit) (fun _ => M)
      (fun _ => hM) ((d:ℝ)*a) ((d:ℝ)*b) (mul_pos hd ha).le (mul_pos hd hb).le rows n () 0
    have hnorm := positiveMatrix_row_le_norm _
      (matrixHistory_nonnegative (id : Unit → Unit) (fun _ => M) (fun _ => hM) n ()) 0
    have pos := lt_of_lt_of_le (pow_pos (mul_pos hd ha) n) (bounds.1.trans hnorm)
    simpa only [constant_matrixHistory] using pos
  · exact positiveMatrixPartition_bounds M p a b ha entries hp mass

/-- Exact finite disintegration at every horizon: the joint path weight is
the mixture of conditional path weights, with fixed package probabilities.
No asymptotic entropy correction is inserted. -/
theorem initial_conditioning_disintegration {Z : Type*} [Fintype Z]
    (M : Matrix (Fin d) (Fin d) ℝ) (w : Z → ℝ) (p : Z → Fin d → ℝ) (n : ℕ) :
    positiveMatrixPartition M (fun i => ∑ z, w z * p z i) n =
      ∑ z, w z * positiveMatrixPartition M (p z) n := by
  simp only [positiveMatrixPartition, Finset.sum_mul, Finset.mul_sum, mul_assoc]
  exact Finset.sum_comm

theorem equal_conditional_pressures_gap_zero {Z : Type*} [Fintype Z]
    (w Q : Z → ℝ) (P : ℝ) (mass : ∑ z, w z = 1) (same : ∀ z, Q z = P) :
    P - ∑ z, w z * Q z = 0 := by
  simp only [same, ← Finset.sum_mul, mass, one_mul, sub_self]

/-- Profiles extracted from genuine fixed initial-law disintegration all
equal the derived pressure. This includes the mixture law itself. -/
theorem initial_conditioning_gap_zero {Z : Type*} [Fintype Z]
    (M : Matrix (Fin d) (Fin d) ℝ) (positive : ∀ i j, 0 < M i j)
    (w : Z → ℝ) (nonneg : ∀ z, 0 ≤ w z) (wmass : ∑ z, w z = 1)
    (p : Z → Fin d → ℝ) (pnonneg : ∀ z i, 0 ≤ p z i)
    (pmass : ∀ z, ∑ i, p z i = 1) :
    ∃ P : ℝ,
      Tendsto (fun n => Real.log
        (positiveMatrixPartition M (fun i => ∑ z, w z * p z i) n) / n) atTop (𝓝 P) ∧
      (∀ z, Tendsto (fun n => Real.log (positiveMatrixPartition M (p z) n) / n)
        atTop (𝓝 P)) ∧ P - ∑ z, w z * P = 0 := by
  obtain ⟨P, common⟩ := initial_conditioning_common_pressure M positive
  refine ⟨P, common _ ?_ ?_, fun z => common _ (pnonneg z) (pmass z), ?_⟩
  · intro i
    exact Finset.sum_nonneg fun z _ => mul_nonneg (nonneg z) (pnonneg z i)
  · rw [Finset.sum_comm]
    simp only [← Finset.mul_sum, pmass, mul_one, wmass]
  · rw [← Finset.sum_mul, wmass, one_mul, sub_self]

/-- Uniqueness prevents an alternative scalar assignment to the conditional
profiles once the actual SAME-potential pressure limits are required. -/
theorem initial_conditioning_profiles_equal {Z : Type*} [Fintype Z]
    (M : Matrix (Fin d) (Fin d) ℝ) (positive : ∀ i j, 0 < M i j)
    (p : Z → Fin d → ℝ) (pnonneg : ∀ z i, 0 ≤ p z i)
    (pmass : ∀ z, ∑ i, p z i = 1) (Q : Z → ℝ)
    (limits : ∀ z, Tendsto (fun n => Real.log (positiveMatrixPartition M (p z) n) / n)
      atTop (𝓝 (Q z))) : ∃ P : ℝ, ∀ z, Q z = P := by
  obtain ⟨P, common⟩ := initial_conditioning_common_pressure M positive
  exact ⟨P, fun z => tendsto_nhds_unique (limits z) (common _ (pnonneg z) (pmass z))⟩

/-- An actual positive B Q U completion/refinement split coexists with
EXACTLY equal conditional finite-path weights for the SAME original kernel
at s=1 and selector q=log 2. Hence structural strictness and material
completion forcing alone do not entail thermodynamic separation. -/
def originalBranchMatrix (z : Bool) : Matrix (Fin 4) (Fin 4) ℝ :=
  fun i j => (pressureKernelChoice z i j : ℝ) / 2

theorem originalBranchMatrix_rows (z : Bool) (i : Fin 4) :
    ∑ j, originalBranchMatrix z i j = (1/2 : ℝ) := by
  simp only [originalBranchMatrix, ← Finset.sum_div]
  have h : (∑ j, (pressureKernelChoice z i j : ℝ)) = 1 := by
    exact_mod_cast (pressureKernelChoice_stochastic z i).2
  rw [h]

theorem constant_row_partition (M : Matrix (Fin d) (Fin d) ℝ) (c : ℝ)
    (rows : ∀ i, ∑ j, M i j = c) (p : Fin d → ℝ) (mass : ∑ i, p i = 1)
    (n : ℕ) : positiveMatrixPartition M p n = c^n := by
  have h : ∀ n i, matrixPathValue M n i = c^n := by
    intro n i
    induction n generalizing i with
    | zero => rfl
    | succ n ih =>
      simp only [matrixPathValue, ih, ← Finset.sum_mul, rows, pow_succ]
      ring
  simp only [positiveMatrixPartition, h, ← Finset.sum_mul, mass, one_mul]

theorem completion_strictness_with_equal_original_partitions :
    (¬ ∃ f, forcedStrataFamily = f ∘ pressureRetainedBase) ∧
    (∀ z : Bool, ∀ n : ℕ,
      positiveMatrixPartition (originalBranchMatrix z) (completedInitial z) n = (1/2:ℝ)^n ∧
      positiveMatrixPartition (originalBranchMatrix z) forcedCompletedFixed n = (1/2:ℝ)^n) := by
  refine ⟨completion_refinement_family_extension, ?_⟩
  intro z n
  exact ⟨constant_row_partition _ _ (originalBranchMatrix_rows z) _
    (completedInitial_stationary z).1 n,
    constant_row_partition _ _ (originalBranchMatrix_rows z) _
      forcedCompletedFixed_mass n⟩

def originalParameterizedMatrix (z : Bool) (s : ℝ) : Matrix (Fin 4) (Fin 4) ℝ :=
  fun i j => ((pressureKernelChoice z i j : ℝ) / 2) ^ s

theorem originalParameterizedMatrix_positive (z : Bool) (s : ℝ) (i j : Fin 4) :
    0 < originalParameterizedMatrix z s i j := by
  apply Real.rpow_pos_of_pos
  have h : (0:ℚ) < pressureKernelChoice z i j :=
    lt_of_lt_of_le (by norm_num : (0:ℚ) < 1/10) ((pressureKernelChoice_stochastic z i).1 j)
  exact div_pos (Rat.cast_pos.mpr h) (by norm_num)

theorem original_uniform_partitions_equal (s : ℝ) (n : ℕ) :
    positiveMatrixPartition (originalParameterizedMatrix false s) (fun _ => 1/4) n =
    positiveMatrixPartition (originalParameterizedMatrix true s) (fun _ => 1/4) n := by
  have base := congrFun (congrFun pressureBase_equal (fun r => r ^ s)) n
  simp only [positiveMatrixPartition, matrixPathValue_eq_row, ← Finset.mul_sum]
  change (1/4:ℝ) * pressureBase false (fun r => r ^ s) n =
    (1/4:ℝ) * pressureBase true (fun r => r ^ s) n
  rw [base]

/-- The entire positive transpose carrier has one pressure for each real
parameter, independent of BOTH kernel choice and initial packaged law.
The carrier's completed-object family is nevertheless a strict extension.
This is an operator-level countermodel to the claimed structural-to-scalar
inference, not an original 16/20-state invariant-shell construction. -/
theorem strict_completion_with_common_original_pressure (s : ℝ) :
    (¬ ∃ f, forcedStrataFamily = f ∘ pressureRetainedBase) ∧
    (∃ P : ℝ, ∀ z : Bool, ∀ p : Fin 4 → ℝ,
      (∀ i, 0 ≤ p i) → (∑ i, p i = 1) →
      Tendsto (fun n => Real.log (positiveMatrixPartition (originalParameterizedMatrix z s) p n) / n)
        atTop (𝓝 P)) := by
  refine ⟨completion_refinement_family_extension, ?_⟩
  obtain ⟨P, common0⟩ := initial_conditioning_common_pressure
    (originalParameterizedMatrix false s) (originalParameterizedMatrix_positive false s)
  obtain ⟨Q, common1⟩ := initial_conditioning_common_pressure
    (originalParameterizedMatrix true s) (originalParameterizedMatrix_positive true s)
  have mass : (∑ _ : Fin 4, (1/4:ℝ)) = 1 := by norm_num
  have limit0 := common0 (fun _ => 1/4) (fun _ => by norm_num) mass
  have limit1 := common1 (fun _ => 1/4) (fun _ => by norm_num) mass
  have same : P = Q := by
    simp only [original_uniform_partitions_equal] at limit0
    exact tendsto_nhds_unique limit0 limit1
  refine ⟨P, ?_⟩
  intro z p hp hm
  cases z
  · exact common0 p hp hm
  · rw [same]; exact common1 p hp hm

def originalPackageInitial (z h : Bool) : Fin 4 → ℝ :=
  if h then forcedCompletedFixed else completedInitial z

theorem originalPackageInitial_probability (z h : Bool) :
    (∀ i, 0 ≤ originalPackageInitial z h i) ∧ ∑ i, originalPackageInitial z h i = 1 := by
  cases h
  · refine ⟨?_, (completedInitial_stationary z).1⟩
    intro i
    change 0 ≤ (pressureFixed z i : ℝ)
    exact (Rat.cast_pos.mpr (pressureFixed_positive z i)).le
  · refine ⟨?_, forcedCompletedFixed_mass⟩
    intro i
    change 0 ≤ (pressureSpectralFixed i : ℝ)
    fin_cases i <;> norm_num [pressureSpectralFixed]

/-- Full original-potential countermodel package: exact completion-family
strictness, a genuine finite disintegration, and ZERO weighted gap at EVERY
real parameter and every probability weighting of the two fixed objects.
The missing original-shell realization is deliberately not hidden here. -/
theorem original_strict_completion_zero_gap (s : ℝ) (w : Bool → ℝ)
    (nonneg : ∀ h, 0 ≤ w h) (mass : ∑ h, w h = 1) :
    (¬ ∃ f, forcedStrataFamily = f ∘ pressureRetainedBase) ∧
    (∃ P : ℝ, ∀ z : Bool,
      Tendsto (fun n => Real.log (positiveMatrixPartition (originalParameterizedMatrix z s)
        (fun i => ∑ h, w h * originalPackageInitial z h i) n) / n) atTop (𝓝 P) ∧
      (∀ h, Tendsto (fun n => Real.log (positiveMatrixPartition (originalParameterizedMatrix z s)
        (originalPackageInitial z h) n) / n) atTop (𝓝 P)) ∧
      P - ∑ h, w h * P = 0) := by
  obtain ⟨strict, P, common⟩ := strict_completion_with_common_original_pressure s
  refine ⟨strict, P, ?_⟩
  intro z
  refine ⟨common z _ ?_ ?_, ?_, ?_⟩
  · intro i
    exact Finset.sum_nonneg fun h _ => mul_nonneg (nonneg h)
      ((originalPackageInitial_probability z h).1 i)
  · rw [Finset.sum_comm]
    simp only [← Finset.mul_sum, (originalPackageInitial_probability z _).2, mul_one, mass]
  · intro h
    exact common z _ (originalPackageInitial_probability z h).1
      (originalPackageInitial_probability z h).2
  · rw [← Finset.sum_mul, mass, one_mul, sub_self]

end
end CantorAudit
