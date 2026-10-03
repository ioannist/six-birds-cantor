import PackagedDisintegration

/-! Return from one fixed reference law to a supremum pressure. The lower
bound may have an arbitrarily small exponential loss and a loss-dependent
fixed prefactor. It need not be a uniform fraction of the envelope.
The measure construction supplying these bounds is a separate analytic step.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology

theorem reference_pressure_of_arbitrary_small_loss (Z E : ℕ → ℝ) (P : ℝ)
    (positive : ∀ n, 0 < Z n)
    (upper : ∀ n, Z n ≤ E n)
    (envelope_limit : Tendsto (fun n => Real.log (E n)/n) atTop (𝓝 P))
    (lower : ∀ ε : ℝ, 0 < ε → ∃ c : ℝ, 0 < c ∧
      ∀ n : ℕ, c*Real.exp ((n:ℝ)*(P-ε)) ≤ Z n) :
    Tendsto (fun n => Real.log (Z n)/n) atTop (𝓝 P) := by
  apply tendsto_order.2
  constructor
  · intro a ha
    let ε := (P-a)/2
    have he : 0 < ε := by dsimp [ε]; linarith
    obtain ⟨c, hc, bound⟩ := lower ε he
    have hl : Tendsto (fun n : ℕ => Real.log c/n + (P-ε))
        atTop (𝓝 (P-ε)) := by
      simpa using (tendsto_const_div_atTop_nhds_zero_nat (Real.log c)).add tendsto_const_nhds
    have hnear : ∀ᶠ n : ℕ in atTop, a < Real.log c/n+(P-ε) :=
      hl.eventually (eventually_gt_nhds (by dsimp [ε]; linarith))
    filter_upwards [hnear, eventually_gt_atTop (0:ℕ)] with n hn hpos
    have hnR : (0:ℝ) < n := by exact_mod_cast hpos
    have hlog := Real.log_le_log (mul_pos hc (Real.exp_pos _)) (bound n)
    rw [Real.log_mul hc.ne' (Real.exp_pos _).ne', Real.log_exp] at hlog
    have hdiv := div_le_div_of_nonneg_right hlog hnR.le
    have eq : (Real.log c+(n:ℝ)*(P-ε))/(n:ℝ) = Real.log c/n+(P-ε) := by
      field_simp [hnR.ne']
      ring
    rw [eq] at hdiv
    exact hn.trans_le hdiv
  · intro b hb
    have hnear := envelope_limit.eventually (eventually_lt_nhds hb)
    filter_upwards [hnear] with n hn
    exact (div_le_div_of_nonneg_right
      (Real.log_le_log (positive n) (upper n)) (Nat.cast_nonneg n)).trans_lt hn

/-- A dense countable mixture supplies arbitrarily small losses without
changing the reference law when the pressure parameter changes. The component
domination and parameter approximation must come from that SAME law. -/
theorem reference_pressure_of_dense_component_bounds (Z E : ℕ → ℝ) (P : ℝ)
    (c error : ℕ → ℝ) (positive : ∀ n, 0 < Z n)
    (upper : ∀ n, Z n ≤ E n)
    (envelope_limit : Tendsto (fun n => Real.log (E n)/n) atTop (𝓝 P))
    (weights : ∀ j, 0 < c j)
    (components : ∀ j (n : ℕ), c j*Real.exp ((n:ℝ)*(P-error j)) ≤ Z n)
    (arbitrary_small_error : ∀ ε : ℝ, 0 < ε → ∃ j, error j < ε) :
    Tendsto (fun n => Real.log (Z n)/n) atTop (𝓝 P) := by
  apply reference_pressure_of_arbitrary_small_loss Z E P positive upper envelope_limit
  intro ε hε
  obtain ⟨j, hj⟩ := arbitrary_small_error ε hε
  refine ⟨c j, weights j, ?_⟩
  intro n
  apply le_trans ?_ (components j n)
  apply mul_le_mul_of_nonneg_left _ (weights j).le
  apply Real.exp_le_exp.mpr
  exact mul_le_mul_of_nonneg_left (by linarith) (Nat.cast_nonneg n)

/-- Fixed prefactors in a Collatz estimate disappear in pressure limits. -/
theorem pressure_bounds_of_geometric_constants (Z : ℕ → ℝ) (a b c e P : ℝ)
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) (he : 0 < e)
    (positive : ∀ n, 0 < Z n)
    (bounds : ∀ n, c*a^n ≤ Z n ∧ Z n ≤ e*b^n)
    (limit : Tendsto (fun n => Real.log (Z n)/n) atTop (𝓝 P)) :
    Real.log a ≤ P ∧ P ≤ Real.log b := by
  have up_lim : Tendsto (fun n : ℕ => Real.log (Z n)/n-Real.log e/n)
      atTop (𝓝 P) := by
    simpa using limit.sub (tendsto_const_div_atTop_nhds_zero_nat (Real.log e))
  have lower_lim : Tendsto (fun n : ℕ => -(Real.log (Z n)/n)+Real.log c/n)
      atTop (𝓝 (-P)) := by
    simpa using limit.neg.add (tendsto_const_div_atTop_nhds_zero_nat (Real.log c))
  constructor
  · have h : -P ≤ -Real.log a := by
      apply le_of_tendsto lower_lim
      filter_upwards [eventually_gt_atTop (0:ℕ)] with n hn
      have hnR : (0:ℝ) < n := by exact_mod_cast hn
      have hlog := Real.log_le_log (mul_pos hc (pow_pos ha n)) (bounds n).1
      rw [Real.log_mul hc.ne' (pow_pos ha n).ne',Real.log_pow] at hlog
      rw [← neg_div,← add_div]
      exact (div_le_iff hnR).mpr (by nlinarith)
    linarith
  · apply le_of_tendsto up_lim
    filter_upwards [eventually_gt_atTop (0:ℕ)] with n hn
    have hnR : (0:ℝ) < n := by exact_mod_cast hn
    have hlog := Real.log_le_log (positive n) (bounds n).2
    rw [Real.log_mul he.ne' (pow_pos hb n).ne',Real.log_pow] at hlog
    rw [← sub_div]
    exact (div_le_iff hnR).mpr (by nlinarith)

theorem binary_gap_lower_of_pressure_intervals (P₀ P₁ l₀ u₀ l₁ u₁ g : ℝ)
    (bound₀ : l₀ ≤ P₀ ∧ P₀ ≤ u₀) (bound₁ : l₁ ≤ P₁ ∧ P₁ ≤ u₁)
    (separated : 2*g < l₁-u₀ ∨ 2*g < l₀-u₁) :
    g < max P₀ P₁-((1/2)*P₀+(1/2)*P₁) := by
  rw [binary_equal_weight_gap]
  rcases separated with h | h
  · have habs := le_abs_self (P₁-P₀)
    linarith [bound₀.2,bound₁.1]
  · have habs := neg_le_abs (P₁-P₀)
    linarith [bound₀.1,bound₁.2]

/-- Same actual-object conditioning with a certified gap of either sign.
The conditional limits are supplied by the fixed-reference return above;
the interval separation is a separate, checkable cocycle estimate. -/
theorem binary_actual_package_pressure_from_intervals {O : Type*} [DecidableEq O]
    (package : Bool → O) (distinct : package false ≠ package true)
    (Z : Bool → ℕ → ℝ) (P : Bool → ℝ)
    (positive : ∀ z n, 0 < Z z n)
    (limits : ∀ z, Tendsto (fun n => Real.log (Z z n)/n) atTop (𝓝 (P z)))
    (l₀ u₀ l₁ u₁ g : ℝ)
    (bound₀ : l₀ ≤ P false ∧ P false ≤ u₀)
    (bound₁ : l₁ ≤ P true ∧ P true ≤ u₁)
    (separated : 2*g < l₁-u₀ ∨ 2*g < l₀-u₁) :
    Tendsto (fun n => Real.log ((1/2)*Z false n+(1/2)*Z true n)/n)
      atTop (𝓝 (max (P false) (P true))) ∧
    (∀ z, Tendsto (fun n => Real.log (binaryPackageConditional package (1/2)
      (fun h => Z h n) (package z))/n) atTop (𝓝 (P z))) ∧
    g < max (P false) (P true)-((1/2)*P false+(1/2)*P true) := by
  refine ⟨?_, ?_, binary_gap_lower_of_pressure_intervals _ _ _ _ _ _ _
    bound₀ bound₁ separated⟩
  · convert binary_disintegration_pressure (Z false) (Z true) (1/2)
      (P false) (P true) (by norm_num) (by norm_num)
      (positive false) (positive true) (limits false) (limits true) using 1
    norm_num
  · intro z
    simpa only [binary_actual_package_conditional package (1/2) distinct
      (by norm_num) (by norm_num)] using limits z

end
end CantorAudit
