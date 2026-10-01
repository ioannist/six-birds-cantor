import CantorAudit

/-!
A concrete rational completion instance. The base descriptor here is exactly
(K,tau), omitting the active package. It is not asserted to equal the paper's
unspecified exact cocycle object, or to be realized in its stronger shell.
The two fixed distributions belong to DIFFERENT completion operators.
-/
namespace CantorAudit

def witnessKernel : Fin 4 → Fin 4 → ℚ :=
  ![![3/5, 1/5, 1/10, 1/10], ![1/5, 2/5, 1/5, 1/5],
    ![1/10, 1/5, 2/5, 3/10], ![1/10, 1/5, 3/10, 2/5]]

def witnessLazyTransport (i j : Fin 4) : ℚ :=
  (18/25) * (if i.val = j.val then 1 else 0) + (7/25) * witnessKernel i j

def witnessUniform : Fin 4 → ℚ := ![1/4, 1/4, 1/4, 1/4]
def witnessFullFixed : Fin 4 → ℚ := ![97/336, 239/1008, 239/1008, 239/1008]
def witnessFullCompletion (_i j : Fin 4) : ℚ := witnessFullFixed j

theorem witnessKernel_stochastic (i : Fin 4) :
    (∀ j, 0 < witnessKernel i j) ∧ ∑ j : Fin 4, witnessKernel i j = 1 := by
  constructor
  · intro j; fin_cases i <;> fin_cases j <;> norm_num [witnessKernel]
  · fin_cases i <;> norm_num [witnessKernel, Fin.sum_univ_succ, Fin.succ_mk]

def witnessPrototype (i : Fin 4) : ℚ :=
  (55/100) * witnessUniform i + (25/100) * ((witnessUniform i + witnessKernel i i) / 2)
    + (20/100) * witnessKernel i i

theorem witnessLazyTransport_stochastic (i : Fin 4) :
    ∑ j : Fin 4, witnessLazyTransport i j = 1 := by
  fin_cases i <;> norm_num [witnessLazyTransport, witnessKernel, Fin.sum_univ_succ, Fin.succ_mk]

/-- Bridge to the actual all-state evolve/forget/reinstate formula, using
exact rational prototypes rather than postulating a desired output vector. -/
theorem witnessFullCompletion_formula (i j : Fin 4) :
    (∑ h : Fin 4, witnessLazyTransport i h *
      (witnessPrototype j / (∑ k : Fin 4, witnessPrototype k))) =
        witnessFullCompletion i j := by
  rw [← Finset.sum_mul, witnessLazyTransport_stochastic, one_mul]
  fin_cases j <;> norm_num [witnessPrototype, witnessUniform, witnessKernel,
    witnessFullCompletion, witnessFullFixed, Fin.sum_univ_succ]

/-- Singleton reinstatement is the identity; its completion is the lazy
transport itself, independently of the strictly positive prototype weights. -/
theorem witnessSingletonCompletion_formula (i j : Fin 4) :
    (∑ h : Fin 4, witnessLazyTransport i h *
      (if h = j then witnessPrototype j / witnessPrototype j else 0)) =
        witnessLazyTransport i j := by
  classical
  have hp : witnessPrototype j ≠ 0 := by
    fin_cases j <;> norm_num [witnessPrototype, witnessUniform, witnessKernel]
  simp [hp]

theorem witnessFullFixed_mass : ∑ i : Fin 4, witnessFullFixed i = 1 := by
  norm_num [witnessFullFixed, Fin.sum_univ_succ]

/-- The all-state package saturates after one completion, for every mass-one
input. This is exact idempotence, unlike the three-start counting heuristic. -/
theorem witnessFullCompletion_saturates (μ : Fin 4 → ℚ)
    (mass : ∑ i : Fin 4, μ i = 1) (j : Fin 4) :
    ∑ i : Fin 4, μ i * witnessFullCompletion i j = witnessFullFixed j := by
  simp only [witnessFullCompletion]
  rw [← Finset.sum_mul, mass, one_mul]

theorem witnessUniform_stationary (j : Fin 4) :
    ∑ i : Fin 4, witnessUniform i * witnessLazyTransport i j = witnessUniform j := by
  fin_cases j <;> norm_num [witnessUniform, witnessLazyTransport, witnessKernel, Fin.sum_univ_succ, Fin.succ_mk]

/-- The singleton-package completion has exactly one mass-one fixed vector. -/
theorem witnessSingleton_unique (μ : Fin 4 → ℚ)
    (mass : ∑ i : Fin 4, μ i = 1)
    (stationary : ∀ j, ∑ i : Fin 4, μ i * witnessLazyTransport i j = μ j) :
    μ = witnessUniform := by
  have h0 := stationary 0
  have h1 := stationary 1
  have h2 := stationary 2
  norm_num [witnessLazyTransport, witnessKernel, Fin.sum_univ_succ, Fin.succ_mk] at h0 h1 h2 mass
  have hu0 : μ 0 = 1/4 := by linarith
  have hu1 : μ 1 = 1/4 := by linarith
  have hu2 : μ 2 = 1/4 := by linarith
  have hu3 : μ (Fin.succ (2 : Fin 3)) = 1/4 := by linarith
  funext j
  fin_cases j
  · exact hu0
  · exact hu1
  · exact hu2
  · exact hu3

/-- Non-factorization through the explicitly chosen instantaneous descriptor.
If the descriptor also retains the package, this conclusion does not follow. -/
theorem witness_package_extension :
    ¬ ∃ f : ((Fin 4 → Fin 4 → ℚ) × ℚ) → (Fin 4 → ℚ),
      (fun b : Bool => if b then witnessUniform else witnessFullFixed) =
        f ∘ (fun _ : Bool => (witnessKernel, 1)) := by
  apply collision_obstructs_factorization (fun _ : Bool => (witnessKernel, (1 : ℚ)))
    (fun b : Bool => if b then witnessUniform else witnessFullFixed) (x := false) (y := true) rfl
  intro eq
  have h := congrFun eq 0
  norm_num [witnessUniform, witnessFullFixed] at h

/-- Actual strong-lumpability obstruction for the partition {0,1},{2,3}. -/
theorem witness_pair_lumpability_obstruction :
    (witnessLazyTransport 0 0 + witnessLazyTransport 0 1) -
      (witnessLazyTransport 1 0 + witnessLazyTransport 1 1) = 7/125 := by
  norm_num [witnessLazyTransport, witnessKernel]

end CantorAudit
