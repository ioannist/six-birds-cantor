import ConditionalPressure

/-! Correct pressure return for the paper's finite family of fibers.
The inputs must be the conditional partitions of one fixed probability law,
with a fixed finite, positive-mass family. This module does not construct that
law, identify the family's objects, or equate its pressure to a shell supremum.
In particular, structural strictness supplies no pressure-separation hypothesis.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology

variable {I : Type*} [Fintype I]

/-- The finite law of total expectation becomes a MAXIMUM of conditional
pressures after taking logarithmic growth rates. The maximizer is supplied as
an index, avoiding any nonempty-family or unattained-supremum convention. -/
theorem finite_disintegration_pressure (Z : I → ℕ → ℝ) (P w : I → ℝ)
    (positive : ∀ i n, 0 < Z i n) (weights : ∀ i, 0 < w i)
    (mass : ∑ i, w i = 1)
    (limits : ∀ i, Tendsto (fun n => Real.log (Z i n)/n) atTop (𝓝 (P i)))
    (imax : I) (maximal : ∀ i, P i ≤ P imax) :
    Tendsto (fun n => Real.log (∑ i, w i * Z i n)/n) atTop (𝓝 (P imax)) := by
  have lower_bound (n : ℕ) : w imax * Z imax n ≤ ∑ i, w i * Z i n :=
    Finset.single_le_sum (fun i _ => (mul_pos (weights i) (positive i n)).le)
      (Finset.mem_univ imax)
  have positive_sum (n : ℕ) : 0 < ∑ i, w i * Z i n :=
    (mul_pos (weights imax) (positive imax n)).trans_le (lower_bound n)
  apply tendsto_order.2
  constructor
  · intro a ha
    have lower_limit : Tendsto
        (fun n : ℕ => Real.log (w imax)/n + Real.log (Z imax n)/n)
        atTop (𝓝 (P imax)) := by
      simpa using (tendsto_const_div_atTop_nhds_zero_nat (Real.log (w imax))).add
        (limits imax)
    have near := lower_limit.eventually (eventually_gt_nhds ha)
    filter_upwards [near] with n hn
    have bound := div_le_div_of_nonneg_right
      (Real.log_le_log (mul_pos (weights imax) (positive imax n)) (lower_bound n))
      (Nat.cast_nonneg n)
    rw [Real.log_mul (weights imax).ne' (positive imax n).ne', add_div] at bound
    exact hn.trans_le bound
  · intro b hb
    let middle := (P imax+b)/2
    have hm : P imax < middle := by dsimp [middle]; linarith
    have hmb : middle < b := by dsimp [middle]; linarith
    have near : ∀ᶠ n : ℕ in atTop, ∀ i, Real.log (Z i n)/n < middle :=
      eventually_all.2 fun i => (limits i).eventually
        (eventually_lt_nhds ((maximal i).trans_lt hm))
    filter_upwards [near, eventually_gt_atTop (0:ℕ)] with n hn hpos
    have hnR : (0:ℝ) < n := by exact_mod_cast hpos
    have bound : (∑ i, w i * Z i n) ≤ Real.exp ((n:ℝ)*middle) := by
      calc
        (∑ i, w i * Z i n) ≤ ∑ i, w i * Real.exp ((n:ℝ)*middle) := by
          apply Finset.sum_le_sum
          intro i _
          apply mul_le_mul_of_nonneg_left _ (weights i).le
          apply (Real.log_le_iff_le_exp (positive i n)).mp
          nlinarith [(div_lt_iff hnR).mp (hn i)]
        _ = Real.exp ((n:ℝ)*middle) := by rw [← Finset.sum_mul, mass, one_mul]
    have hlog := Real.log_le_log (positive_sum n) bound
    rw [Real.log_exp] at hlog
    have hdiv : Real.log (∑ i, w i * Z i n)/n ≤ middle :=
      (div_le_iff hnR).mpr (by nlinarith)
    exact hdiv.trans_lt hmb

/-- The gap is a sum of positive-weight deficits from the largest conditional
pressure. A split object fiber can still have zero deficit. -/
theorem finite_disintegration_gap_formula (P w : I → ℝ) (M : ℝ)
    (mass : ∑ i, w i = 1) :
    M - ∑ i, w i * P i = ∑ i, w i * (M-P i) := by
  simp only [mul_sub, Finset.sum_sub_distrib, ← Finset.sum_mul, mass, one_mul]

theorem finite_disintegration_gap_nonnegative (P w : I → ℝ) (imax : I)
    (weights : ∀ i, 0 ≤ w i) (mass : ∑ i, w i = 1)
    (maximal : ∀ i, P i ≤ P imax) :
    0 ≤ P imax - ∑ i, w i * P i := by
  rw [finite_disintegration_gap_formula P w (P imax) mass]
  exact Finset.sum_nonneg fun i _ => mul_nonneg (weights i) (sub_nonneg.mpr (maximal i))

theorem finite_disintegration_gap_zero_iff (P w : I → ℝ) (imax : I)
    (weights : ∀ i, 0 < w i) (mass : ∑ i, w i = 1)
    (maximal : ∀ i, P i ≤ P imax) :
    P imax - ∑ i, w i * P i = 0 ↔ ∀ i, P i = P imax := by
  rw [finite_disintegration_gap_formula P w (P imax) mass]
  rw [Finset.sum_eq_zero_iff_of_nonneg
    (fun i _ => mul_nonneg (weights i).le (sub_nonneg.mpr (maximal i)))]
  simp only [Finset.mem_univ, true_implies, mul_eq_zero, (weights _).ne', false_or,
    sub_eq_zero, eq_comm]

/-- The missing premise is separation of actual conditional pressure limits,
not merely inequality of the objects indexing them. -/
theorem finite_disintegration_gap_positive_iff (P w : I → ℝ) (imax : I)
    (weights : ∀ i, 0 < w i) (mass : ∑ i, w i = 1)
    (maximal : ∀ i, P i ≤ P imax) :
    0 < P imax - ∑ i, w i * P i ↔ ∃ i j, P i ≠ P j := by
  have hnonneg := finite_disintegration_gap_nonnegative P w imax
    (fun i => (weights i).le) mass maximal
  have hzero := finite_disintegration_gap_zero_iff P w imax weights mass maximal
  constructor
  · intro hpos
    have hnot : ¬ ∀ i, P i = P imax := fun h => (ne_of_gt hpos) (hzero.mpr h)
    push_neg at hnot
    obtain ⟨i, hi⟩ := hnot
    exact ⟨i, imax, hi⟩
  · rintro ⟨i, j, hne⟩
    apply lt_of_le_of_ne hnonneg
    intro heq
    have hall := hzero.mp heq.symm
    exact hne ((hall i).trans (hall j).symm)

/-- A quantitative deficit at one positively weighted fiber returns a
quantitative gap; both inputs require independent instance proofs. -/
theorem finite_disintegration_gap_lower_bound (P w : I → ℝ) (imax j : I)
    (weights : ∀ i, 0 ≤ w i) (mass : ∑ i, w i = 1)
    (maximal : ∀ i, P i ≤ P imax) :
    w j * (P imax-P j) ≤ P imax - ∑ i, w i * P i := by
  rw [finite_disintegration_gap_formula P w (P imax) mass]
  exact Finset.single_le_sum
    (fun i _ => mul_nonneg (weights i) (sub_nonneg.mpr (maximal i))) (Finset.mem_univ j)

end
end CantorAudit
