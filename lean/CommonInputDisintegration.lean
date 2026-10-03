import ReferencePressure
import Mathlib.MeasureTheory.Integral.Bochner

/-! Actual reference integrals for the original moving history potential.
Giving two distinct current completion objects the SAME future-input law
leaves their pressure equal whenever their history norms agree. In particular,
matching the reference pressure to the full shell supremum does not repair
the unsupported implication from structural strictness to a positive gap.
The original twenty-state source instance is supplied separately, not axiomatized.
-/
namespace CantorAudit
noncomputable section
open Filter MeasureTheory
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass

variable {Ω : Type*} [MeasurableSpace Ω] {d : ℕ} [NeZero d]

/-- Finite partition restricted to a positive-mass actual object event.
No selected conditional distribution is claimed when the event has mass zero. -/
def fiberReferencePartition {O : Type*} [DecidableEq O] (μ : Measure Ω)
    (package : Ω → O) (o : O) (value : Ω → ℝ) : ℝ :=
  (∫ x, if package x=o then value x else 0 ∂μ)/(μ {x | package x=o}).toReal

/-- If a primitive fixed-input completion sends every allowed start to one
object, its sole positive-mass fiber is the whole reference space. Conditioning
the SAME partition on that fiber changes nothing at ANY finite horizon. -/
theorem constant_package_fiber_partition {O : Type*} [DecidableEq O]
    (μ : Measure Ω) [IsProbabilityMeasure μ] (package : Ω → O) (o : O)
    (constant : ∀ x, package x=o) (value : Ω → ℝ) :
    fiberReferencePartition μ package o value = ∫ x, value x ∂μ := by
  simp [fiberReferencePartition,constant]

def expectedRowHistory (μ : Measure Ω)
    (C : ℕ → Ω → Matrix (Fin d) (Fin d) ℝ) (p : Fin d → ℝ) (n : ℕ) : ℝ :=
  ∫ x, rowHistoryPartition (C n x) p ∂μ

/-- Integrating a pointwise initial-law/norm comparison under one actual
measure preserves its constants. The two integrability inputs must be
established for the SAME measure and potential. -/
theorem expected_row_history_bounds (μ : Measure Ω)
    (C : Ω → Matrix (Fin d) (Fin d) ℝ) (nonneg : ∀ x i j, 0 ≤ C x i j)
    (p : Fin d → ℝ) (c : ℝ) (hc : 0 < c)
    (floor : ∀ i, c ≤ p i) (mass : ∑ i, p i = 1)
    (norm_integrable : Integrable (fun x => ‖C x‖) μ)
    (partition_integrable : Integrable (fun x => rowHistoryPartition (C x) p) μ) :
    c*(∫ x, ‖C x‖ ∂μ) ≤ ∫ x, rowHistoryPartition (C x) p ∂μ ∧
      (∫ x, rowHistoryPartition (C x) p ∂μ) ≤ ∫ x, ‖C x‖ ∂μ := by
  constructor
  · rw [← integral_mul_left]
    exact integral_mono (norm_integrable.const_mul c) partition_integrable
      (fun x => (full_support_history_bounds (C x) (nonneg x) p c hc floor mass).1)
  · exact integral_mono partition_integrable norm_integrable
      (fun x => (full_support_history_bounds (C x) (nonneg x) p c hc floor mass).2)

theorem expected_row_history_same_pressure (μ : Measure Ω)
    (C : ℕ → Ω → Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ n x i j, 0 ≤ C n x i j)
    (p : Fin d → ℝ) (positive_p : ∀ i, 0 < p i) (mass : ∑ i, p i = 1)
    (norm_integrable : ∀ n, Integrable (fun x => ‖C n x‖) μ)
    (partition_integrable : ∀ n, Integrable (fun x => rowHistoryPartition (C n x) p) μ)
    (positive_norm_integral : ∀ n, 0 < ∫ x, ‖C n x‖ ∂μ)
    (P : ℝ)
    (limit : Tendsto (fun n => Real.log (∫ x, ‖C n x‖ ∂μ)/n) atTop (𝓝 P)) :
    Tendsto (fun n => Real.log (expectedRowHistory μ C p n)/n) atTop (𝓝 P) := by
  obtain ⟨i, _, hi⟩ := Finset.exists_min_image Finset.univ p Finset.univ_nonempty
  apply bounded_factor_same_pressure (fun n => ∫ x, ‖C n x‖ ∂μ)
    (expectedRowHistory μ C p) (p i) P (positive_p i) positive_norm_integral ?_ limit
  intro n
  exact expected_row_history_bounds μ (C n) (nonneg n) p (p i) (positive_p i)
    (fun j => hi j (Finset.mem_univ j)) mass (norm_integrable n) (partition_integrable n)

/-- Strictness, genuine positive object fibers, and even a reference integral
with the specified GLOBAL shell pressure coexist with an identically zero
conditional gap under a common future law. The conclusion uses actual
integrals, rather than assigning constant conditional profiles by hand. -/
theorem common_input_actual_package_zero_gap {O D : Type*} [DecidableEq O]
    (μ : Measure Ω) (package : Bool → O) (base : Bool → D)
    (distinct : package false ≠ package true) (same_base : base false = base true)
    (C : Bool → ℕ → Ω → Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ z n x i j, 0 ≤ C z n x i j)
    (same_norm : ∀ n x, ‖C false n x‖ = ‖C true n x‖)
    (p : Bool → Fin d → ℝ) (positive_p : ∀ z i, 0 < p z i)
    (mass : ∀ z, ∑ i, p z i = 1)
    (norm_integrable : ∀ z n, Integrable (fun x => ‖C z n x‖) μ)
    (partition_integrable : ∀ z n,
      Integrable (fun x => rowHistoryPartition (C z n x) (p z)) μ)
    (positive_norm_integral : ∀ n, 0 < ∫ x, ‖C false n x‖ ∂μ)
    (P w : ℝ) (hw : 0 < w) (hw1 : w < 1)
    (limit : Tendsto (fun n => Real.log (∫ x, ‖C false n x‖ ∂μ)/n) atTop (𝓝 P)) :
    let Z := fun z n => expectedRowHistory μ (C z) (p z) n
    (¬ ∃ f : D → O, package = f ∘ base) ∧
    (∀ z, Tendsto (fun n => Real.log (binaryPackageConditional package w
      (fun h => Z h n) (package z))/n) atTop (𝓝 P)) ∧
    Tendsto (fun n => Real.log (w*Z false n+(1-w)*Z true n)/n) atTop (𝓝 P) ∧
    P-(w*P+(1-w)*P)=0 := by
  dsimp only
  have normeq : ∀ z n x, ‖C z n x‖ = ‖C false n x‖ := by
    intro z n x
    cases z
    · rfl
    · exact (same_norm n x).symm
  have limits : ∀ z, Tendsto
      (fun n => Real.log (expectedRowHistory μ (C z) (p z) n)/n) atTop (𝓝 P) := by
    intro z
    apply expected_row_history_same_pressure μ (C z) (nonneg z) (p z)
      (positive_p z) (mass z) (norm_integrable z) (partition_integrable z)
    · intro n
      simpa only [normeq] using positive_norm_integral n
    · simpa only [normeq] using limit
  have positives : ∀ z n, 0 < expectedRowHistory μ (C z) (p z) n := by
    intro z n
    obtain ⟨i, _, hi⟩ := Finset.exists_min_image Finset.univ (p z) Finset.univ_nonempty
    have b := expected_row_history_bounds μ (C z n) (nonneg z n) (p z)
      (p z i) (positive_p z i) (fun j => hi j (Finset.mem_univ j)) (mass z)
      (norm_integrable z n) (partition_integrable z n)
    have pos : 0 < ∫ x, ‖C z n x‖ ∂μ := by
      simpa only [normeq] using positive_norm_integral n
    exact (mul_pos (positive_p z i) pos).trans_le b.1
  refine ⟨binary_package_nonfactor base package same_base distinct, ?_, ?_, by ring⟩
  · intro z
    simpa only [binary_actual_package_conditional package w distinct hw hw1]
      using limits z
  · simpa only [max_self] using binary_disintegration_pressure
      (expectedRowHistory μ (C false) (p false))
      (expectedRowHistory μ (C true) (p true)) w P P hw hw1
      (positives false) (positives true) (limits false) (limits true)

end
end CantorAudit
