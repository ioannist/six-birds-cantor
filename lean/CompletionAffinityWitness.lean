import MatrixPressure
import PressureExtension

/-! Apply the pressure-existence and affinity-loss theorems to the actual
rational B Q U completion operators of the transpose split pair. This is the
changed relative-likelihood path potential on FROZEN completion channels,
not initial conditioning of the physical kernel or persistence under outer F.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
set_option maxHeartbeats 2000000

def pressurePredictor (i j : Fin 4) : ℚ :=
  (pressureFixed false i * pressureCompletion false i j +
    pressureFixed true i * pressureCompletion true i j) /
    (pressureFixed false i + pressureFixed true i)

def pressureAffinityLoss : ℚ := 3283594060761 / 134912463042781250

theorem pressureFixed_positive (z : Bool) (i : Fin 4) : 0 < pressureFixed z i := by
  cases z <;> fin_cases i <;> norm_num [pressureFixed]

theorem pressureCompletion_stochastic (z : Bool) (i : Fin 4) :
    ∑ j, pressureCompletion z i j = 1 := by
  simp only [pressureCompletion_formula]
  cases z <;> fin_cases i <;>
    norm_num [pressureCompletionTable, Fin.sum_univ_succ, Fin.succ_mk]

theorem pressurePredictor_positive (i j : Fin 4) : 0 < pressurePredictor i j :=
  div_pos (add_pos (mul_pos (pressureFixed_positive false i) (pressureCompletion_positive false i j))
    (mul_pos (pressureFixed_positive true i) (pressureCompletion_positive true i j)))
    (add_pos (pressureFixed_positive false i) (pressureFixed_positive true i))

theorem pressurePredictor_stochastic (i : Fin 4) : ∑ j, pressurePredictor i j = 1 := by
  simp only [pressurePredictor]
  rw [← Finset.sum_div, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum,
    pressureCompletion_stochastic, pressureCompletion_stochastic, mul_one, mul_one]
  exact div_self (add_pos (pressureFixed_positive false i) (pressureFixed_positive true i)).ne'

/-- Exact rational loss from the actual completed channels and their common
stationary predictor. No square-root rounding or finite-horizon inference. -/
theorem pressurePredictor_loss (z : Bool) (i : Fin 4) :
    pressureAffinityLoss ≤ (∑ j, |pressureCompletion z i j - pressurePredictor i j|)^2 / 8 := by
  simp only [pressurePredictor, pressureCompletion_formula]
  cases z <;> fin_cases i <;>
    norm_num [pressureAffinityLoss, pressureFixed, pressureCompletionTable,
      Fin.sum_univ_succ, Fin.succ_mk] <;> norm_num [abs_div]

def completedChannel (z : Bool) : Matrix (Fin 4) (Fin 4) ℝ :=
  fun i j => (pressureCompletion z i j : ℝ)

def commonCompletionPredictor : Matrix (Fin 4) (Fin 4) ℝ :=
  fun i j => (pressurePredictor i j : ℝ)

def completedInitial (z : Bool) : Fin 4 → ℝ := fun i => (pressureFixed z i : ℝ)

theorem completedInitial_stationary (z : Bool) :
    (∑ i, completedInitial z i = 1) ∧
      (∀ j, ∑ i, completedInitial z i * completedChannel z i j = completedInitial z j) := by
  constructor
  · unfold completedInitial; exact_mod_cast (pressureFixed_stationary z).1
  · intro j
    unfold completedInitial completedChannel
    exact_mod_cast (pressureFixed_stationary z).2 j

theorem completion_affinity_witness_gap :
    ∃ Q : Bool → ℝ,
      (∀ z, Tendsto (fun n => Real.log (positiveMatrixPartition
        (affinityMatrix (completedChannel z) commonCompletionPredictor) (completedInitial z) n) / n)
        atTop (𝓝 (Q z))) ∧
      (∀ z, Q z ≤ Real.log (1-(pressureAffinityLoss : ℝ))) ∧
      (∀ w : Bool → ℝ, (∀ z, 0 ≤ w z) → (∑ z, w z = 1) →
        (pressureAffinityLoss : ℝ) ≤ -(∑ z, w z * Q z) ∧ 0 < -(∑ z, w z * Q z)) := by
  have hloss : ∀ z i, (pressureAffinityLoss : ℝ) ≤
      (∑ j, |completedChannel z i j - commonCompletionPredictor i j|)^2 / 8 := by
    intro z i
    unfold completedChannel commonCompletionPredictor
    exact_mod_cast pressurePredictor_loss z i
  have h : ∀ z : Bool, ∃ Q : ℝ,
      Tendsto (fun n => Real.log (positiveMatrixPartition
        (affinityMatrix (completedChannel z) commonCompletionPredictor) (completedInitial z) n) / n)
        atTop (𝓝 Q) ∧ Q ≤ Real.log (1-(pressureAffinityLoss : ℝ)) ∧ Q < 0 := by
    intro z
    apply affinity_pressure_exists_strict
    · intro i j; unfold completedChannel; exact_mod_cast pressureCompletion_positive z i j
    · intro i j; unfold commonCompletionPredictor; exact_mod_cast pressurePredictor_positive i j
    · intro i; unfold completedChannel; exact_mod_cast pressureCompletion_stochastic z i
    · intro i; unfold commonCompletionPredictor; exact_mod_cast pressurePredictor_stochastic i
    · intro i; unfold completedInitial; exact_mod_cast (pressureFixed_positive z i).le
    · exact (completedInitial_stationary z).1
    · norm_num [pressureAffinityLoss]
    · exact hloss z
  choose Q hlimit hbound _hnegative using h
  refine ⟨Q, hlimit, hbound, ?_⟩
  intro w hw hmass
  exact weighted_affinity_pressure_gap Q w (pressureAffinityLoss : ℝ)
    (by norm_num [pressureAffinityLoss]) (by norm_num [pressureAffinityLoss]) hw hmass hbound

theorem completion_reference_pressure_zero (p : Fin 4 → ℝ) (mass : ∑ i, p i = 1) :
    Tendsto (fun n => Real.log (positiveMatrixPartition commonCompletionPredictor p n) / n)
      atTop (𝓝 0) := by
  apply stochasticMatrix_pressure_zero _ _ p mass
  intro i; unfold commonCompletionPredictor; exact_mod_cast pressurePredictor_stochastic i

end
end CantorAudit
