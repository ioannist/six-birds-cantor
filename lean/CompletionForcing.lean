import CompletionDynamics

/-! The original saturation -> lens forcing -> persistent new fixed-object
obligation, instantiated on the actual audit/spectral B Q U formulas of the
existing exact witness. Persistence is under each fixed completion operator.
The original audited-shell membership remains an independent open input.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
set_option maxHeartbeats 2000000

def pressureSpectralFixed : Fin 4 → ℚ := ![239/891,226/891,71/297,71/297]

def pressureSpectralCompletion (z : Bool) (i j : Fin 4) : ℚ :=
  ∑ h, pressureTransport z i h * (pressurePrototype j / ∑ k, pressurePrototype k)

theorem pressureTransport_stochastic (z : Bool) (i : Fin 4) :
    ∑ j, pressureTransport z i j = 1 := by
  cases z <;> fin_cases i <;>
    norm_num [pressureTransport, pressureKernelChoice, pressureKernel,
      Matrix.transpose_apply, Fin.sum_univ_succ, Fin.succ_mk, Fin.ext_iff]

/-- Same actual K and tau; the uniform finite informant makes the source
spectral package the all-state cell. Its B Q U operator is computed here. -/
theorem pressureSpectralCompletion_formula (z : Bool) (i j : Fin 4) :
    pressureSpectralCompletion z i j = pressureSpectralFixed j := by
  simp only [pressureSpectralCompletion, ← Finset.sum_mul, pressureTransport_stochastic, one_mul]
  fin_cases j <;> norm_num [pressurePrototype, pressureKernel, pressureSpectralFixed,
    Fin.sum_univ_succ, Fin.succ_mk]

def forcedCompletedChannel (z : Bool) : Fin 4 → Fin 4 → ℝ :=
  fun i j => (pressureSpectralCompletion z i j : ℝ)

def forcedCompletedFixed : Fin 4 → ℝ := fun j => (pressureSpectralFixed j : ℝ)

theorem forcedCompletedFixed_mass : ∑ j, forcedCompletedFixed j = 1 := by
  norm_num [forcedCompletedFixed, pressureSpectralFixed, Fin.sum_univ_succ, Fin.succ_mk]

theorem auditCompletedChannel_floor (z : Bool) (i j : Fin 4) :
    (1/25 : ℝ) ≤ completedChannel z i j := by
  unfold completedChannel
  rw [pressureCompletion_formula]
  cases z <;> fin_cases i <;> fin_cases j <;> norm_num [pressureCompletionTable]

/-- Audit completion saturates at its unique persistent fixed object for
EVERY real mass-one input, not merely the three sampled starting laws. -/
theorem audit_completion_saturates (z : Bool) (μ : Fin 4 → ℝ)
    (mass : ∑ i, μ i = 1) (j : Fin 4) :
    Tendsto (fun n => completionIterate (completedChannel z) μ n j)
      atTop (𝓝 (completedInitial z j)) := by
  apply completionIterate_converges (completedChannel z)
    (fun i => by unfold completedChannel; exact_mod_cast pressureCompletion_stochastic z i)
    (1/25) (auditCompletedChannel_floor z) (by norm_num) (by norm_num)
    μ (completedInitial z) mass (completedInitial_stationary z).1
    (completedInitial_stationary z).2

theorem audit_completion_unique_real (z : Bool) (μ : Fin 4 → ℝ)
    (mass : ∑ i, μ i = 1)
    (fixed : ∀ j, ∑ i, μ i * completedChannel z i j = μ j) :
    μ = completedInitial z := by
  exact completion_fixed_unique (completedChannel z)
    (fun i => by unfold completedChannel; exact_mod_cast pressureCompletion_stochastic z i)
    (1/25) (auditCompletedChannel_floor z) (by norm_num) μ (completedInitial z)
    mass (completedInitial_stationary z).1 fixed (completedInitial_stationary z).2

/-- The actual post-forcing operator maps every mass-one start to its new
fixed object in one step. In particular that object persists thereafter. -/
theorem forced_completion_saturates (z : Bool) (μ : Fin 4 → ℝ)
    (mass : ∑ i, μ i = 1) (j : Fin 4) :
    ∑ i, μ i * forcedCompletedChannel z i j = forcedCompletedFixed j := by
  simp only [forcedCompletedChannel, pressureSpectralCompletion_formula, forcedCompletedFixed]
  rw [← Finset.sum_mul, mass, one_mul]

theorem forced_completion_fixed (z : Bool) (j : Fin 4) :
    ∑ i, forcedCompletedFixed i * forcedCompletedChannel z i j = forcedCompletedFixed j :=
  forced_completion_saturates z forcedCompletedFixed forcedCompletedFixed_mass j

theorem forcing_produces_new_fixed_object (z : Bool) :
    completedInitial z ≠ forcedCompletedFixed := by
  intro h
  have h0 := congrFun h 0
  cases z <;> norm_num [completedInitial, pressureFixed, forcedCompletedFixed,
    pressureSpectralFixed] at h0

def forcedStrataFamily (z : Bool) : Set (Fin 4 → ℝ) :=
  {completedInitial z, forcedCompletedFixed}

/-- The extension is a split of the unordered family of genuinely distinct
fixed distributions. Different labels or different traversal order are not
used as a substitute for distinct strata. -/
theorem forcedStrataFamily_split : forcedStrataFamily false ≠ forcedStrataFamily true := by
  have hd : completedInitial false ≠ completedInitial true := by
    intro h
    have h0 := congrFun h 0
    norm_num [completedInitial, pressureFixed] at h0
  intro eq
  have hm : completedInitial false ∈ forcedStrataFamily false := by
    simp [forcedStrataFamily]
  rw [eq] at hm
  simp only [forcedStrataFamily, Set.mem_insert_iff, Set.mem_singleton_iff] at hm
  rcases hm with he | he
  · exact hd he
  · exact forcing_produces_new_fixed_object false he

/-- Exact non-factorization after completion/refinement, with the SAME
scalar-history base as the existing witness. Original-shell membership is
not a conclusion of this application. -/
theorem completion_refinement_family_extension :
    ¬ ∃ f, forcedStrataFamily = f ∘ pressureRetainedBase := by
  apply collision_obstructs_factorization pressureRetainedBase forcedStrataFamily
    (x := false) (y := true)
  · simp only [pressureRetainedBase, pressureBase_equal]
  · exact forcedStrataFamily_split

/-- False-target control: keeping ONLY the final post-forcing output erases
this witness's distinction, so strict extension cannot be claimed for it. -/
theorem final_forced_readout_factorizes :
    ∃ f, (fun _ : Bool => forcedCompletedFixed) = f ∘ pressureRetainedBase := by
  exact ⟨fun _ => forcedCompletedFixed, rfl⟩

/-- Non-lumpability is computed from the SAME pre-forcing transport and
audit cells. It does not serve as a substitute for an exact split pair. -/
theorem audit_transport_macro_obstruction (z : Bool) :
    |(pressureTransport z 0 0 + pressureTransport z 0 1) -
      (pressureTransport z 1 0 + pressureTransport z 1 1)| =
      if z then (21/500 : ℚ) else 7/100 := by
  cases z <;> norm_num [pressureTransport, pressureKernelChoice, pressureKernel,
    Matrix.transpose_apply, abs_div]

theorem saturation_and_material_forcing_support (z : Bool) :
    (∀ μ : Fin 4 → ℝ, (∑ i, μ i = 1) → ∀ j,
      Tendsto (fun n => completionIterate (completedChannel z) μ n j)
        atTop (𝓝 (completedInitial z j))) ∧
    (∀ μ : Fin 4 → ℝ, (∑ i, μ i = 1) → ∀ j,
      ∑ i, μ i * forcedCompletedChannel z i j = forcedCompletedFixed j) ∧
    (∀ j, ∑ i, forcedCompletedFixed i * forcedCompletedChannel z i j = forcedCompletedFixed j) ∧
    completedInitial z ≠ forcedCompletedFixed :=
  ⟨audit_completion_saturates z, forced_completion_saturates z,
    forced_completion_fixed z, forcing_produces_new_fixed_object z⟩

end
end CantorAudit
