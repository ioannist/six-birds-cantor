import CompletionWitness
import Mathlib.Data.Matrix.Basic

/-!
Strict extension of a declared scalar partition-family base. The base retains
the entire frozen-kernel family, the same lens, tau and package. It does NOT
retain the labelled kernel or the full cocycle of the six-mechanism evolution.
-/
namespace CantorAudit
set_option maxHeartbeats 2000000
noncomputable section
open Matrix

def historyTotal {d : ℕ} (A : Matrix (Fin d) (Fin d) ℝ) (n : ℕ) : ℝ :=
  ∑ i, ∑ j, (A ^ n) i j

/-- Equality of all scalar history partitions, not just a rounded pressure
or a finite parameter grid. Applies to every real entrywise weight function. -/
theorem transpose_historyTotal {d : ℕ} (A : Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    historyTotal A.transpose n = historyTotal A n := by
  simp only [historyTotal, ← Matrix.transpose_pow, Matrix.transpose_apply]
  rw [Finset.sum_comm]

def pressureKernel : Matrix (Fin 4) (Fin 4) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => 40/100
  | 0, 1 => 30/100
  | 0, 2 => 20/100
  | 0, 3 => 10/100
  | 1, 0 => 10/100
  | 1, 1 => 35/100
  | 1, 2 => 25/100
  | 1, 3 => 30/100
  | 2, 0 => 25/100
  | 2, 1 => 15/100
  | 2, 2 => 30/100
  | 2, 3 => 30/100
  | 3, 0 => 25/100
  | 3, 1 => 20/100
  | 3, 2 => 25/100
  | 3, 3 => 30/100
  | _, _ => 0

def pressureKernelChoice (z : Bool) : Matrix (Fin 4) (Fin 4) ℚ :=
  if z then pressureKernel.transpose else pressureKernel

def pressurePrototype (i : Fin 4) : ℚ :=
  (55/100) * (1/4) + (25/100) * (((1/4) + pressureKernel i i) / 2)
    + (20/100) * pressureKernel i i

def pressureReinstate (i j : Fin 4) : ℚ :=
  if (i.val < 2 ↔ j.val < 2) then
    pressurePrototype j / (if j.val < 2 then pressurePrototype 0 + pressurePrototype 1
      else pressurePrototype 2 + pressurePrototype 3)
  else 0

def pressureTransport (z : Bool) (i j : Fin 4) : ℚ :=
  (18/25) * (if i = j then 1 else 0) + (7/25) * pressureKernelChoice z i j

def pressureCompletion (z : Bool) (i j : Fin 4) : ℚ :=
  ∑ h : Fin 4, pressureTransport z i h * pressureReinstate h j

def pressureFixed (z : Bool) : Fin 4 → ℚ :=
  if z then ![4063/15849,3842/15849,1324/5283,1324/5283]
  else ![4063/15745,3842/15745,784/3149,784/3149]

theorem pressureKernelChoice_stochastic (z : Bool) (i : Fin 4) :
    (∀ j, (1/10 : ℚ) ≤ pressureKernelChoice z i j) ∧
      ∑ j : Fin 4, pressureKernelChoice z i j = 1 := by
  constructor
  · intro j; cases z <;> fin_cases i <;> fin_cases j <;>
      norm_num [pressureKernelChoice, pressureKernel, Matrix.transpose_apply]
  · cases z <;> fin_cases i <;>
      norm_num [pressureKernelChoice, pressureKernel, Matrix.transpose_apply, Fin.sum_univ_succ, Fin.succ_mk]

/-- The prototype bridge uses the actual finite informant: both kernels
preserve the uniform vector already at its first iterate. -/
theorem pressureKernelChoice_uniform (z : Bool) (j : Fin 4) :
    ∑ i : Fin 4, (1/4 : ℚ) * pressureKernelChoice z i j = 1/4 := by
  cases z <;> fin_cases j <;>
    norm_num [pressureKernelChoice, pressureKernel, Matrix.transpose_apply, Fin.sum_univ_succ, Fin.succ_mk]

def pressureCompletionTable (z : Bool) : Matrix (Fin 4) (Fin 4) ℚ :=
  if z then
    ![![10277/23250,4859/11625,7/100,7/100],
      ![107789/232500,50963/116250,49/1000,49/1000],
      ![5019/77500,2373/38750,437/1000,437/1000],
      ![3346/58125,3164/58125,111/250,111/250]]
  else
    ![![54731/116250,25877/58125,21/500,21/500],
      ![33699/77500,15933/38750,77/1000,77/1000],
      ![3346/58125,3164/58125,111/250,111/250],
      ![5019/77500,2373/38750,437/1000,437/1000]]

/-- Kernel reduction checks the table against B Q U, not against an assumed
completion output. No native_decide or compiler trust axiom is used. -/
theorem pressureCompletion_formula (z : Bool) (i j : Fin 4) :
    pressureCompletion z i j = pressureCompletionTable z i j := by
  cases z <;> fin_cases i <;> fin_cases j <;>
    norm_num [pressureCompletion, pressureCompletionTable, pressureTransport,
      pressureReinstate, pressurePrototype, pressureKernelChoice, pressureKernel,
      Matrix.transpose_apply, Fin.sum_univ_succ, Fin.succ_mk, Fin.ext_iff]

theorem pressureFixed_stationary (z : Bool) :
    (∑ i : Fin 4, pressureFixed z i = 1) ∧
    (∀ j, ∑ i : Fin 4, pressureFixed z i * pressureCompletion z i j = pressureFixed z j) := by
  simp only [pressureCompletion_formula]
  constructor
  · cases z <;> norm_num [pressureFixed, Fin.sum_univ_succ, Fin.succ_mk]
  · intro j; cases z <;> fin_cases j <;>
      norm_num [pressureFixed, pressureCompletionTable, Fin.sum_univ_succ, Fin.succ_mk]

theorem pressureCompletion_positive (z : Bool) (i j : Fin 4) :
    0 < pressureCompletion z i j := by
  rw [pressureCompletion_formula]
  cases z <;> fin_cases i <;> fin_cases j <;>
    norm_num [pressureCompletionTable]

theorem pressureFixed_unique (z : Bool) (μ : Fin 4 → ℚ)
    (mass : ∑ i : Fin 4, μ i = 1)
    (stationary : ∀ j, ∑ i : Fin 4, μ i * pressureCompletion z i j = μ j) :
    μ = pressureFixed z := by
  have h0 := stationary 0
  have h1 := stationary 1
  have h2 := stationary 2
  simp only [pressureCompletion_formula] at h0 h1 h2
  cases z <;>
    norm_num [pressureCompletionTable, Fin.sum_univ_succ, Fin.succ_mk] at h0 h1 h2 mass
  · have hu0 : μ 0 = pressureFixed false 0 := by norm_num [pressureFixed]; linarith
    have hu1 : μ 1 = pressureFixed false 1 := by norm_num [pressureFixed]; linarith
    have hu2 : μ 2 = pressureFixed false 2 := by norm_num [pressureFixed]; linarith
    have hu3 : μ (Fin.succ (2 : Fin 3)) = pressureFixed false 3 := by norm_num [pressureFixed]; linarith
    funext j
    fin_cases j
    · exact hu0
    · exact hu1
    · exact hu2
    · exact hu3
  · have hu0 : μ 0 = pressureFixed true 0 := by norm_num [pressureFixed]; linarith
    have hu1 : μ 1 = pressureFixed true 1 := by norm_num [pressureFixed]; linarith
    have hu2 : μ 2 = pressureFixed true 2 := by norm_num [pressureFixed]; linarith
    have hu3 : μ (Fin.succ (2 : Fin 3)) = pressureFixed true 3 := by norm_num [pressureFixed]; linarith
    funext j
    fin_cases j
    · exact hu0
    · exact hu1
    · exact hu2
    · exact hu3

/-- Every real weight function of branch weight, at EVERY horizon, agrees.
In particular w(r)=r^s gives the entire real-parameter partition family. -/
def pressureBase (z : Bool) : (ℝ → ℝ) → ℕ → ℝ := fun w n =>
  historyTotal (fun i j => w ((pressureKernelChoice z i j : ℝ) / 2)) n

theorem pressureBase_equal : pressureBase false = pressureBase true := by
  funext w n
  change historyTotal (fun i j => w ((pressureKernel i j : ℝ) / 2)) n =
    historyTotal (fun i j => w ((pressureKernel j i : ℝ) / 2)) n
  exact (transpose_historyTotal _ n).symm

/-- Retain tau=1, the same actual audit lens, and the ENTIRE identical
reinstatement operator, which in particular retains the partition and its
within-cell prototype weights. No active lens/package is dropped to force
the collision. The labelled transport kernel is omitted explicitly. -/
def pressureRetainedBase (z : Bool) :=
  (pressureBase z, (1 : ℚ), "audit_flow_quantile_lens", pressureReinstate)

theorem pressure_profile_extension :
    ¬ ∃ f, pressureFixed = f ∘ pressureRetainedBase := by
  apply collision_obstructs_factorization pressureRetainedBase pressureFixed
    (x := false) (y := true)
  · simp only [pressureRetainedBase, pressureBase_equal]
  · intro eq
    have h := congrFun eq 0
    norm_num [pressureFixed] at h

end
end CantorAudit
