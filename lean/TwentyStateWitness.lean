import TwentyStateData

/-! Exact original-dimensional instance for structural pressure blindness.
Candidate rational data are checked against the actual lazy B Q U formula.
Source realization, real-score selector guards and the infinite controlled
carrier are separate analytic/interval proofs; they are not assumed to be
certified by this finite matrix instance. -/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass
set_option maxHeartbeats 8000000
set_option maxRecDepth 4000

theorem warm_forward_positive (i j : Fin 20) : 0 < warmForward i j := by
  unfold warmForward
  positivity

theorem warm_kernel_stochastic (z : Bool) (i : Fin 20) :
    (∀ j, 0 < warmKernel z i j) ∧ ∑ j, warmKernel z i j = 1 := by
  constructor
  · intro j
    cases z
    · exact warm_forward_positive i j
    · exact warm_forward_positive j i
  · cases z <;> fin_cases i <;>
      norm_num [warmKernel, warmForward, Fin.sum_univ_succ, Fin.succ_mk]

theorem warm_kernel_uniform_informant (z : Bool) (j : Fin 20) :
    (∑ i, (1/20 : ℚ)*warmKernel z i j) = 1/20 := by
  cases z <;> fin_cases j <;>
    norm_num [warmKernel, warmForward, Fin.sum_univ_succ, Fin.succ_mk]

def warmTransport (z : Bool) (i j : Fin 20) : ℚ :=
  (93/125)*(if i = j then 1 else 0)+(32/125)*warmKernel z i j

theorem warm_lazy_blend_parameter :
    max (18/100 : ℚ) (min (78/100) (22/100+(18/100)*min 1 ((3/5)/3))) = 32/125 := by
  norm_num

theorem warm_transport_stochastic (z : Bool) (i : Fin 20) :
    ∑ j, warmTransport z i j = 1 := by
  simp only [warmTransport, Finset.sum_add_distrib, ← Finset.mul_sum]
  rw [(warm_kernel_stochastic z i).2]
  simp
  norm_num

theorem warm_core_coefficient_formula (z : Bool) (i : Fin 20) :
    warmCoreCoefficient z i = ∑ h, if warmAuditCore h then warmTransport z i h else 0 := by
  cases z <;> fin_cases i <;>
    norm_num [warmCoreCoefficient, warmTransport, warmKernel, warmForward,
      warmAuditCore, Fin.sum_univ_succ, Fin.succ_mk, Fin.ext_iff]

def warmReinstatement (h j : Fin 20) : ℚ :=
  if warmAuditCore j then
    (if warmAuditCore h then warmPrototype j/warmCoreMass else 0)
  else (if warmAuditCore h then 0 else warmPrototype j/warmOtherMass)

theorem warm_core_mass_value : warmCoreMass = (500299/2000000 : ℚ) := by
  norm_num [warmCoreMass, warmPrototype, warmForward, warmAuditCore,
    Fin.sum_univ_succ, Fin.succ_mk]

theorem warm_other_mass_value : warmOtherMass = (599987/800000 : ℚ) := by
  norm_num [warmOtherMass, warmPrototype, warmForward, warmAuditCore,
    Fin.sum_univ_succ, Fin.succ_mk]

theorem warm_core_coefficient_bounds (z : Bool) (i : Fin 20) :
    (3/50 : ℚ) ≤ warmCoreCoefficient z i ∧ warmCoreCoefficient z i ≤ 81/100 := by
  cases z <;> fin_cases i <;> norm_num [warmCoreCoefficient]

theorem warm_prototype_ratio_bounds (j : Fin 20) :
    (1/6 : ℚ) ≤ warmPrototype j/warmCoreMass ∧
    (1/19 : ℚ) ≤ warmPrototype j/warmOtherMass := by
  rw [warm_core_mass_value, warm_other_mass_value]
  fin_cases j <;> norm_num [warmPrototype, warmForward]

/-- No postulated completion matrix: the candidate table is precisely the
original two-cell prototype-weighted evolve/forget/reinstate operator. -/
theorem warm_completion_bqu (z : Bool) (i j : Fin 20) :
    (∑ h, warmTransport z i h * warmReinstatement h j) = warmCompletion z i j := by
  by_cases hj : warmAuditCore j
  · simp only [warmReinstatement, warmCompletion, if_pos hj]
    rw [warm_core_coefficient_formula, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro h _
    by_cases hh : warmAuditCore h <;> simp [hh]
  · simp only [warmReinstatement, warmCompletion, if_neg hj]
    rw [warm_core_coefficient_formula, ← warm_transport_stochastic z i,
      ← Finset.sum_sub_distrib, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro h _
    by_cases hh : warmAuditCore h <;> simp [hh]

theorem warm_completion_positive_stochastic (z : Bool) (i : Fin 20) :
    (∀ j, (1/100 : ℚ) ≤ warmCompletion z i j) ∧ ∑ j, warmCompletion z i j = 1 := by
  constructor
  · intro j
    have hc := warm_core_coefficient_bounds z i
    have hp := warm_prototype_ratio_bounds j
    unfold warmCompletion
    split_ifs
    · calc
        (1/100 : ℚ) = (3/50)*(1/6) := by norm_num
        _ ≤ _ := mul_le_mul hc.1 hp.1 (by norm_num) (by linarith)
    · calc
        (1/100 : ℚ) = (19/100)*(1/19) := by norm_num
        _ ≤ _ := mul_le_mul (by linarith) hp.2 (by norm_num) (by linarith)
  · have hc : (∑ j, if warmAuditCore j then warmPrototype j/warmCoreMass else 0) = 1 := by
      calc
        _ = (∑ j, if warmAuditCore j then warmPrototype j else 0)/warmCoreMass := by
          rw [Finset.sum_div]
          apply Finset.sum_congr rfl
          intro j _
          by_cases hj : warmAuditCore j <;> simp [hj]
        _ = 1 := by change warmCoreMass/warmCoreMass = 1; rw [warm_core_mass_value]; norm_num
    have ho : (∑ j, if warmAuditCore j then 0 else warmPrototype j/warmOtherMass) = 1 := by
      calc
        _ = (∑ j, if warmAuditCore j then 0 else warmPrototype j)/warmOtherMass := by
          rw [Finset.sum_div]
          apply Finset.sum_congr rfl
          intro j _
          by_cases hj : warmAuditCore j <;> simp [hj]
        _ = 1 := by change warmOtherMass/warmOtherMass = 1; rw [warm_other_mass_value]; norm_num
    have term (j : Fin 20) : warmCompletion z i j =
        warmCoreCoefficient z i*(if warmAuditCore j then warmPrototype j/warmCoreMass else 0)
        +(1-warmCoreCoefficient z i)*(if warmAuditCore j then 0 else warmPrototype j/warmOtherMass) := by
      by_cases hj : warmAuditCore j <;> simp [warmCompletion, hj]
    simp_rw [term]
    rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, hc, ho]
    ring

def warmAuditCoreProbability (z : Bool) : ℚ :=
  if z then 50027481669202471/200109927212425471
  else 150082445020615187/600329781650284187

theorem warm_audit_object_formula (z : Bool) (j : Fin 20) :
    warmAuditObject z j = if warmAuditCore j then
      warmAuditCoreProbability z*(warmPrototype j/warmCoreMass)
    else (1-warmAuditCoreProbability z)*(warmPrototype j/warmOtherMass) := by
  rw [warm_core_mass_value, warm_other_mass_value]
  cases z <;> fin_cases j <;>
    norm_num [warmAuditObject, warmAuditCoreProbability, warmAuditCore,
      warmPrototype, warmForward]

theorem warm_audit_object_mass (z : Bool) : (∑ j, warmAuditObject z j) = 1 := by
  cases z <;> norm_num [warmAuditObject, Fin.sum_univ_succ, Fin.succ_mk]

theorem warm_audit_mean_core (z : Bool) :
    (∑ i, warmAuditObject z i*warmCoreCoefficient z i) = warmAuditCoreProbability z := by
  cases z <;> norm_num [warmAuditObject, warmCoreCoefficient, warmAuditCoreProbability,
    Fin.sum_univ_succ, Fin.succ_mk]

theorem warm_audit_object_stationary (z : Bool) :
    (∀ j, 0 < warmAuditObject z j) ∧ (∑ j, warmAuditObject z j) = 1 ∧
      ∀ j, (∑ i, warmAuditObject z i*warmCompletion z i j) = warmAuditObject z j := by
  constructor
  · intro j
    cases z <;> fin_cases j <;> norm_num [warmAuditObject]
  constructor
  · exact warm_audit_object_mass z
  · intro j
    rw [warm_audit_object_formula z j]
    by_cases hj : warmAuditCore j
    · simp only [warmCompletion, if_pos hj, ← mul_assoc, ← Finset.sum_mul]
      rw [warm_audit_mean_core]
    · simp only [warmCompletion, if_neg hj, ← mul_assoc, ← Finset.sum_mul,
        mul_sub, mul_one, Finset.sum_sub_distrib, warm_audit_object_mass, warm_audit_mean_core]

theorem warm_audit_objects_distinct : warmAuditObject false ≠ warmAuditObject true := by
  intro h
  have h0 := congrFun h 0
  norm_num [warmAuditObject] at h0

def warmCompletionReal (z : Bool) (i j : Fin 20) : ℝ := (warmCompletion z i j : ℝ)
def warmAuditObjectReal (z : Bool) (j : Fin 20) : ℝ := (warmAuditObject z j : ℝ)

theorem warm_completion_real_floor (z : Bool) (i j : Fin 20) :
    (1/100 : ℝ) ≤ warmCompletionReal z i j := by
  have h : ((1/100 : ℚ) : ℝ) ≤ (warmCompletion z i j : ℝ) :=
    Rat.cast_le.mpr ((warm_completion_positive_stochastic z i).1 j)
  norm_num at h
  exact h

theorem warm_audit_completion_converges (z : Bool) (μ : Fin 20 → ℝ)
    (mass : ∑ i, μ i = 1) (j : Fin 20) :
    Tendsto (fun n => completionIterate (warmCompletionReal z) μ n j)
      atTop (𝓝 (warmAuditObjectReal z j)) := by
  apply completionIterate_converges (warmCompletionReal z)
    (fun i => by unfold warmCompletionReal; exact_mod_cast (warm_completion_positive_stochastic z i).2)
    (1/100)
    (warm_completion_real_floor z)
    (by norm_num) (by norm_num) μ (warmAuditObjectReal z) mass
  · unfold warmAuditObjectReal
    exact_mod_cast warm_audit_object_mass z
  · intro k
    unfold warmAuditObjectReal warmCompletionReal
    exact_mod_cast (warm_audit_object_stationary z).2.2 k

theorem warm_audit_completion_unique (z : Bool) (μ : Fin 20 → ℝ)
    (mass : ∑ i, μ i = 1)
    (fixed : ∀ j, ∑ i, μ i*warmCompletionReal z i j = μ j) :
    μ = warmAuditObjectReal z := by
  apply completion_fixed_unique (warmCompletionReal z)
    (fun i => by unfold warmCompletionReal; exact_mod_cast (warm_completion_positive_stochastic z i).2)
    (1/100)
    (warm_completion_real_floor z)
    (by norm_num) μ (warmAuditObjectReal z) mass
  · unfold warmAuditObjectReal
    exact_mod_cast warm_audit_object_mass z
  · exact fixed
  · intro k
    unfold warmAuditObjectReal warmCompletionReal
    exact_mod_cast (warm_audit_object_stationary z).2.2 k

def warmRowSwap (i : Fin 20) : Equiv.Perm (Fin 20) :=
  if i.val = 0 then Equiv.swap 1 2 else
  if i.val = 1 then Equiv.swap 0 2 else
  if i.val = 2 then Equiv.swap 0 1 else Equiv.refl _

theorem warm_kernel_row_permutation (i j : Fin 20) :
    warmKernel false i j = warmKernel true i (warmRowSwap i j) := by
  fin_cases i <;> fin_cases j <;>
    norm_num [warmKernel, warmForward, warmRowSwap, Equiv.swap_apply_def, Fin.ext_iff]

theorem warm_all_weighted_rows (w : ℚ → ℝ) (i : Fin 20) :
    (∑ j, w (warmKernel false i j)) = ∑ j, w (warmKernel true i j) := by
  calc
    _ = ∑ j, w (warmKernel true i (warmRowSwap i j)) := by
      apply Finset.sum_congr rfl
      intro j _
      rw [warm_kernel_row_permutation]
    _ = _ := Equiv.sum_comp (warmRowSwap i) (fun j => w (warmKernel true i j))

theorem warm_kernel_difference_support (i j : Fin 20)
    (hj : j ∉ ({0,1,2} : Set (Fin 20))) : warmKernel false i j = warmKernel true i j := by
  fin_cases i <;> fin_cases j <;>
    norm_num [warmKernel, warmForward, Set.mem_insert_iff, Set.mem_singleton_iff,
      Fin.ext_iff] at hj ⊢

theorem warm_join_common_rows (i : Fin 20) (hi : i ∈ ({0,1,2} : Set (Fin 20)))
    (j : Fin 20) : warmJoin i j = warmJoin 0 j := by
  simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hi
  rcases hi with h | h | h <;> subst i <;> simp [warmJoin]

/-- Direct twenty-state instance: any nonnegative first-step weighting and
any second-step weighting have the same full history-norm observations under
the shared source join, for an arbitrary common future matrix sequence.
The actual original potential is obtained by its source-derived scalars. -/
theorem warm_all_history_norms_equal (w₀ w₁ : ℚ → ℝ)
    (nonneg : ∀ z i j, 0 ≤ w₀ (warmKernel z i j))
    (tail : ℕ → Matrix (Fin 20) (Fin 20) ℝ) (n : ℕ) :
    ‖matchedHistory (fun i j => w₀ (warmKernel false i j))
      (fun i j => w₁ (warmJoin i j)) tail n‖ =
    ‖matchedHistory (fun i j => w₀ (warmKernel true i j))
      (fun i j => w₁ (warmJoin i j)) tail n‖ := by
  apply matchedHistory_norms_equal _ _ _ (nonneg false) (nonneg true)
    (warm_all_weighted_rows w₀)
  apply supported_difference_mul_common_rows _ _ _ ({0,1,2} : Set (Fin 20))
    (fun j => w₁ (warmJoin 0 j)) (warm_all_weighted_rows w₀)
  · intro i j hj
    rw [warm_kernel_difference_support i j hj]
  · intro i hi j
    rw [warm_join_common_rows i hi j]

def warmGrowthDescriptor {T : Type*} (w₀ w₁ : T → ℚ → ℝ)
    (tail : T → ℕ → Matrix (Fin 20) (Fin 20) ℝ) (z : Bool) : T → ℕ → ℝ :=
  fun t n => ‖matchedHistory (fun i j => w₀ t (warmKernel z i j))
    (fun i j => w₁ t (warmJoin i j)) (tail t) n‖

/-- Exact nonfactorization through ALL growth observations in a declared
parameter family, using derived twenty-state completion objects. No pressure
separation hypothesis or probability-law selection is used. -/
theorem twenty_state_pressure_blind_extension {T : Type*} (w₀ w₁ : T → ℚ → ℝ)
    (nonneg : ∀ t z i j, 0 ≤ w₀ t (warmKernel z i j))
    (tail : T → ℕ → Matrix (Fin 20) (Fin 20) ℝ) :
    ¬ ∃ f : (T → ℕ → ℝ) → (Fin 20 → ℚ),
      warmAuditObject = f ∘ warmGrowthDescriptor w₀ w₁ tail := by
  apply collision_obstructs_factorization _ _ (x := false) (y := true)
  · funext t n
    exact warm_all_history_norms_equal (w₀ t) (w₁ t) (nonneg t) (tail t) n
  · exact warm_audit_objects_distinct

theorem warm_audit_objects_real_distinct : warmAuditObjectReal false ≠ warmAuditObjectReal true := by
  intro h
  have h0 := congrFun h 0
  norm_num [warmAuditObjectReal, warmAuditObject] at h0

theorem twenty_state_real_pressure_blind_extension {T : Type*} (w₀ w₁ : T → ℚ → ℝ)
    (nonneg : ∀ t z i j, 0 ≤ w₀ t (warmKernel z i j))
    (tail : T → ℕ → Matrix (Fin 20) (Fin 20) ℝ) :
    ¬ ∃ f : (T → ℕ → ℝ) → (Fin 20 → ℝ),
      warmAuditObjectReal = f ∘ warmGrowthDescriptor w₀ w₁ tail := by
  apply collision_obstructs_factorization _ _ (x := false) (y := true)
  · funext t n
    exact warm_all_history_norms_equal (w₀ t) (w₁ t) (nonneg t) (tail t) n
  · exact warm_audit_objects_real_distinct

theorem warm_original_weight_positive (q s : ℝ) (z : Bool) (i j : Fin 20) :
    0 < (Real.exp (-q)*(warmKernel z i j : ℝ))^s := by
  apply Real.rpow_pos_of_pos
  apply mul_pos (Real.exp_pos _)
  exact_mod_cast (warm_kernel_stochastic z i).1 j

end
end CantorAudit
