import KernelCocycle

/-! The local escape estimate for positive matrix history weights. -/
namespace CantorAudit
open Filter Set
open scoped Topology

/-- Omitting even one intermediate state loses a uniformly positive term. -/
theorem matrix_two_step_escape {d : ℕ} (hd : 0 < d)
    (A B : Fin d → Fin d → ℝ) (S : Finset (Fin d))
    (h : Fin d) (outside : h ∉ S) (a b : ℝ) (ha : 0 < a)
    (hA : ∀ i j, a ≤ A i j ∧ A i j ≤ b)
    (hB : ∀ i j, a ≤ B i j ∧ B i j ≤ b) (i k : Fin d) :
    (1 + a ^ 2 / ((d : ℝ) * b ^ 2)) * (∑ j in S, A i j * B j k) ≤
      ∑ j : Fin d, A i j * B j k := by
  classical
  have hb : 0 < b := lt_of_lt_of_le ha ((hA i k).1.trans (hA i k).2)
  have prodpos : ∀ j, 0 ≤ A i j * B j k := fun j =>
    mul_nonneg (ha.le.trans (hA i j).1) (ha.le.trans (hB j k).1)
  have extra : a ^ 2 ≤ A i h * B h k := by
    have := mul_le_mul (hA i h).1 (hB h k).1 ha.le (ha.le.trans (hA i h).1)
    simpa [pow_two] using this
  have hs : (∑ j in S, A i j * B j k) + A i h * B h k ≤
      ∑ j : Fin d, A i j * B j k := by
    have hh := Finset.sum_le_sum_of_subset_of_nonneg
      (Finset.subset_univ (insert h S)) (fun j _ _ => prodpos j)
    simpa [Finset.sum_insert outside, add_comm] using hh
  have bound : (∑ j in S, A i j * B j k) ≤ (d : ℝ) * b ^ 2 := by
    calc
      (∑ j in S, A i j * B j k) ≤ ∑ j in S, b ^ 2 := by
        apply Finset.sum_le_sum
        intro j _
        have hh := mul_le_mul (hA i j).2 (hB j k).2
          (ha.le.trans (hB j k).1) hb.le
        simpa [pow_two] using hh
      _ = (S.card : ℝ) * b ^ 2 := by simp
      _ ≤ (d : ℝ) * b ^ 2 := by
        have hc : S.card ≤ d := by simpa using Finset.card_le_card (Finset.subset_univ S)
        exact mul_le_mul_of_nonneg_right (by exact_mod_cast hc) (sq_nonneg b)
  have denpos : 0 < (d : ℝ) * b ^ 2 := mul_pos (by exact_mod_cast hd) (pow_pos hb 2)
  have scaled : a ^ 2 / ((d : ℝ) * b ^ 2) * (∑ j in S, A i j * B j k) ≤ a ^ 2 := by
    rw [div_mul_eq_mul_div]
    apply (div_le_iff denpos).mpr
    exact mul_le_mul_of_nonneg_left bound (sq_nonneg a)
  nlinarith

/-- Transfer a derived exponential loss to a strict gap between existing
pressure limits. The comparison is explicit and must be supplied by the
matrix pairing argument; strict object extension alone is not a premise.
-/
theorem pressure_gap_of_even_escape (full restricted : ℕ → ℝ)
    (P R γ : ℝ) (hγ : 0 < γ)
    (hr : ∀ n, 0 < restricted n)
    (comparison : ∀ n, γ ^ n * restricted (2 * n) ≤ full (2 * n))
    (hP : Tendsto (fun n => Real.log (full n) / n) atTop (𝓝 P))
    (hR : Tendsto (fun n => Real.log (restricted n) / n) atTop (𝓝 R)) :
    Real.log γ / 2 ≤ P - R := by
  have even : Tendsto (fun n : ℕ => 2 * n) atTop atTop :=
    tendsto_atTop_mono (fun n => by change n ≤ 2 * n; omega) tendsto_id
  have lim := (hP.comp even).sub (hR.comp even)
  apply ge_of_tendsto lim
  filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
  have h := Real.log_le_log (mul_pos (pow_pos hγ n) (hr (2 * n))) (comparison n)
  rw [Real.log_mul (pow_pos hγ n).ne' (hr (2 * n)).ne', Real.log_pow] at h
  have hd := div_le_div_of_nonneg_right h (show 0 ≤ ((2 * n : ℕ) : ℝ) by positivity)
  simp only [Nat.cast_mul, Nat.cast_ofNat] at hd ⊢
  have heq : ((n : ℝ) * Real.log γ + Real.log (restricted (2 * n))) / (2 * n) =
      Real.log γ / 2 + Real.log (restricted (2 * n)) / (2 * n) := by
    field_simp
    ring
  rw [heq] at hd
  simp only [Function.comp_apply, Nat.cast_mul, Nat.cast_ofNat]
  linarith

/-- Initial conditioning by a fixed bounded positive density does not change
an asymptotic pressure. A positive finite-state completion fixed distribution
has just such bounds; this is distinct from restricting every path step. -/
theorem bounded_factor_same_pressure (Z R : ℕ → ℝ) (c P : ℝ)
    (hc : 0 < c) (hZ : ∀ n, 0 < Z n)
    (bounds : ∀ n, c * Z n ≤ R n ∧ R n ≤ Z n)
    (hP : Tendsto (fun n => Real.log (Z n) / n) atTop (𝓝 P)) :
    Tendsto (fun n => Real.log (R n) / n) atTop (𝓝 P) := by
  have lowerlim : Tendsto (fun n => Real.log c / n + Real.log (Z n) / n)
      atTop (𝓝 P) := by
    simpa using (tendsto_const_div_atTop_nhds_zero_nat (Real.log c)).add hP
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' lowerlim hP
  · filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
    have hnR : (0 : ℝ) < n := by exact_mod_cast hn
    have h := Real.log_le_log (mul_pos hc (hZ n)) (bounds n).1
    rw [Real.log_mul hc.ne' (hZ n).ne'] at h
    simpa [add_div] using div_le_div_of_nonneg_right h hnR.le
  · filter_upwards [eventually_gt_atTop (0 : ℕ)] with n hn
    have hnR : (0 : ℝ) < n := by exact_mod_cast hn
    have hR : 0 < R n := lt_of_lt_of_le (mul_pos hc (hZ n)) (bounds n).1
    exact div_le_div_of_nonneg_right (Real.log_le_log hR (bounds n).2) hnR.le

end CantorAudit
