import HistoryConditioning

/-! Finite disintegration by an ACTUAL object-valued readout. The two objects
must be distinct; their names are not latent continuation labels. This module
does not derive a reference world law, shell membership, or the paper's base.
Those are separate instance obligations. -/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology

variable {O D : Type*} [DecidableEq O]

def binaryPackageMass (package : Bool → O) (w : ℝ) (o : O) : ℝ :=
  (if package false = o then w else 0) +
    (if package true = o then 1-w else 0)

def binaryPackageIntegral (package : Bool → O) (w : ℝ)
    (value : Bool → ℝ) (o : O) : ℝ :=
  (if package false = o then w*value false else 0) +
    (if package true = o then (1-w)*value true else 0)

def binaryPackageConditional (package : Bool → O) (w : ℝ)
    (value : Bool → ℝ) (o : O) : ℝ :=
  binaryPackageIntegral package w value o / binaryPackageMass package w o

theorem binary_actual_package_mass (package : Bool → O) (w : ℝ)
    (distinct : package false ≠ package true) (z : Bool) :
    binaryPackageMass package w (package z) = if z then 1-w else w := by
  cases z <;> simp [binaryPackageMass, distinct, Ne.symm distinct]

theorem binary_actual_package_conditional (package : Bool → O) (w : ℝ)
    (distinct : package false ≠ package true) (hw : 0 < w) (hw1 : w < 1)
    (value : Bool → ℝ) (z : Bool) :
    binaryPackageConditional package w value (package z) = value z := by
  cases z <;>
    simp [binaryPackageConditional, binaryPackageIntegral, binaryPackageMass,
      distinct, Ne.symm distinct, ne_of_gt hw, ne_of_gt (show 0 < 1-w by linarith)]

/-- The finite law of total expectation is conditioned on the object readout.
The same value is used before and after conditioning. -/
theorem binary_actual_package_disintegration (package : Bool → O) (w : ℝ)
    (distinct : package false ≠ package true) (hw : 0 < w) (hw1 : w < 1)
    (value : Bool → ℝ) :
    w*binaryPackageConditional package w value (package false) +
      (1-w)*binaryPackageConditional package w value (package true) =
      w*value false + (1-w)*value true := by
  rw [binary_actual_package_conditional package w distinct hw hw1 value false,
    binary_actual_package_conditional package w distinct hw hw1 value true]

theorem binary_package_nonfactor (base : Bool → D) (package : Bool → O)
    (same_base : base false = base true) (distinct : package false ≠ package true) :
    ¬ ∃ f : D → O, package = f ∘ base := by
  rintro ⟨f, h⟩
  apply distinct
  calc
    package false = f (base false) := congrFun h false
    _ = f (base true) := congrArg f same_base
    _ = package true := (congrFun h true).symm

/-- Return from genuine finite object conditioning to its pressure limit.
Pressure separation remains an explicit input, not a consequence of strictness.
The global pressure here is that of the specified world law. Identification
with a larger shell supremum requires a further theorem. -/
theorem binary_actual_package_pressure (package : Bool → O)
    (distinct : package false ≠ package true) (Z : Bool → ℕ → ℝ) (P : Bool → ℝ)
    (positive : ∀ z n, 0 < Z z n)
    (limits : ∀ z, Tendsto (fun n => Real.log (Z z n)/n) atTop (𝓝 (P z)))
    (separation : (1/1000 : ℝ) < P true-P false) :
    Tendsto (fun n => Real.log ((1/2)*Z false n+(1/2)*Z true n)/n)
      atTop (𝓝 (max (P false) (P true))) ∧
    (∀ z, Tendsto (fun n => Real.log (binaryPackageConditional package (1/2)
      (fun h => Z h n) (package z))/n) atTop (𝓝 (P z))) ∧
    (1/2000 : ℝ) < max (P false) (P true)-((1/2)*P false+(1/2)*P true) := by
  refine ⟨?_, ?_, separated_original_continuations_gap_bound _ _ separation⟩
  · convert binary_disintegration_pressure (Z false) (Z true) (1/2)
      (P false) (P true) (by norm_num) (by norm_num)
      (positive false) (positive true) (limits false) (limits true) using 1
    norm_num
  · intro z
    simpa only [binary_actual_package_conditional package (1/2) distinct
      (by norm_num) (by norm_num)] using limits z

end
end CantorAudit
