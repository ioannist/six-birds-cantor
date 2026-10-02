import CompletionDynamics

/-! Saturation for original nonnegative completion operators. A positive
finite power suffices; strict positivity of the one-step kernel is not
required. Stationary existence is constructed from a Cauchy iteration,
not supplied as a field or assumed as the desired fixed-point conclusion.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
variable {d : ℕ} [NeZero d]

theorem completionIterate_nonnegative (M : Fin d → Fin d → ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (μ : Fin d → ℝ) (hμ : ∀ i, 0 ≤ μ i)
    (n : ℕ) (j : Fin d) : 0 ≤ completionIterate M μ n j := by
  induction n generalizing j with
  | zero => exact hμ j
  | succ n ih => exact Finset.sum_nonneg fun i _ => mul_nonneg (ih i) (nonneg i j)

theorem completionIterate_succ_initial (M : Fin d → Fin d → ℝ)
    (μ : Fin d → ℝ) (n : ℕ) (j : Fin d) :
    completionIterate M μ (n+1) j = completionIterate M (completionIterate M μ 1) n j := by
  induction n generalizing j with
  | zero => rfl
  | succ n ih =>
    change (∑ i, completionIterate M μ (n+1) i*M i j) =
      ∑ i, completionIterate M (completionIterate M μ 1) n i*M i j
    simp only [ih]

theorem completionIterate_distance (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (ε : ℝ) (floor : ∀ i j, ε ≤ M i j)
    (hc : 0 ≤ 1-(d:ℝ)*ε) (μ ν : Fin d → ℝ)
    (massμ : ∑ i, μ i = 1) (massν : ∑ i, ν i = 1) (n : ℕ) :
    (∑ j, |completionIterate M μ n j-completionIterate M ν n j|) ≤
      (1-(d:ℝ)*ε)^n * ∑ j, |μ j-ν j| := by
  induction n with
  | zero => simp [completionIterate]
  | succ n ih =>
    have mass : ∑ i, (completionIterate M μ n i-completionIterate M ν n i) = 0 := by
      rw [Finset.sum_sub_distrib, completionIterate_mass M rows μ n,
        completionIterate_mass M rows ν n, massμ, massν]; ring
    have h := stochastic_zero_mass_contraction M rows ε floor
      (fun i => completionIterate M μ n i-completionIterate M ν n i) mass
    have eq : ∀ j, completionIterate M μ (n+1) j-completionIterate M ν (n+1) j =
        ∑ i, (completionIterate M μ n i-completionIterate M ν n i)*M i j := by
      intro j
      simp only [completionIterate, sub_mul, Finset.sum_sub_distrib]
    simp only [eq]
    calc
      _ ≤ (1-(d:ℝ)*ε)*∑ j, |completionIterate M μ n j-completionIterate M ν n j| := h
      _ ≤ (1-(d:ℝ)*ε)*((1-(d:ℝ)*ε)^n*∑ j, |μ j-ν j|) :=
        mul_le_mul_of_nonneg_left ih hc
      _ = _ := by rw [pow_succ]; ring

/-- Existence of the stationary distribution, derived from geometric
increment bounds and completeness of the reals. -/
theorem positive_completion_stationary_exists (M : Fin d → Fin d → ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (ε : ℝ) (hε : 0 < ε)
    (floor : ∀ i j, ε ≤ M i j) :
    ∃ p : Fin d → ℝ, (∀ j, 0 < p j) ∧ (∑ j, p j = 1) ∧
      (∀ j, ∑ i, p i*M i j = p j) := by
  have hd : (0:ℝ) < d := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne d)
  have hc : 0 ≤ 1-(d:ℝ)*ε := by
    have h := Finset.sum_le_sum (s := Finset.univ) (fun j _ => floor 0 j)
    simp only [Finset.sum_const, Finset.card_fin, nsmul_eq_mul, rows] at h
    linarith
  have hc1 : 1-(d:ℝ)*ε < 1 := by nlinarith
  let μ : Fin d → ℝ := fun _ => 1/(d:ℝ)
  have mass : ∑ i, μ i = 1 := by simp [μ, hd.ne']
  have nonneg : ∀ i j, 0 ≤ M i j := fun i j => hε.le.trans (floor i j)
  have limits : ∀ j, ∃ a : ℝ, Tendsto (fun n => completionIterate M μ n j) atTop (𝓝 a) := by
    intro j
    apply cauchySeq_tendsto_of_complete
    apply cauchySeq_of_le_geometric (1-(d:ℝ)*ε)
      (∑ i, |completionIterate M μ 1 i-μ i|) hc1
    intro n
    have h := completionIterate_distance M rows ε floor hc
      (completionIterate M μ 1) μ ((completionIterate_mass M rows μ 1).trans mass) mass n
    have coordinate := Finset.single_le_sum
      (fun i _ => abs_nonneg (completionIterate M (completionIterate M μ 1) n i-
        completionIterate M μ n i)) (Finset.mem_univ j)
    rw [Real.dist_eq]
    rw [abs_sub_comm, completionIterate_succ_initial]
    exact coordinate.trans (by simpa only [mul_comm] using h)
  choose p lim using limits
  have massp : ∑ i, p i = 1 := by
    have h := tendsto_finset_sum Finset.univ (fun i _ => lim i)
    have eq : (fun n => ∑ i, completionIterate M μ n i) = fun _ : ℕ => (1:ℝ) := by
      funext n; exact (completionIterate_mass M rows μ n).trans mass
    rw [eq] at h
    exact tendsto_nhds_unique h tendsto_const_nhds
  have fixed : ∀ j, ∑ i, p i*M i j = p j := by
    intro j
    have h := tendsto_finset_sum Finset.univ (fun i _ => (lim i).mul_const (M i j))
    have shift := (lim j).comp (tendsto_add_atTop_nat 1)
    exact tendsto_nhds_unique h shift
  have nonnegp : ∀ j, 0 ≤ p j := by
    intro j
    apply ge_of_tendsto (lim j)
    exact Filter.eventually_of_forall fun n => completionIterate_nonnegative M nonneg μ
      (fun _ => (div_pos zero_lt_one hd).le) n j
  refine ⟨p, ?_, massp, fixed⟩
  intro j
  have h : ε ≤ ∑ i, p i*M i j := by
    calc
      ε = ∑ i, p i*ε := by rw [← Finset.sum_mul, massp, one_mul]
      _ ≤ _ := Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (floor i j) (nonnegp i)
  rw [fixed j] at h
  exact hε.trans_le h

theorem completionIterate_eq_vecMul (M : Matrix (Fin d) (Fin d) ℝ)
    (μ : Fin d → ℝ) (n : ℕ) : completionIterate M μ n = Matrix.vecMul μ (M^n) := by
  induction n with
  | zero => simp [completionIterate]
  | succ n ih =>
    change Matrix.vecMul (completionIterate M μ n) M = Matrix.vecMul μ (M^(n+1))
    rw [ih, Matrix.vecMul_vecMul, pow_succ]

theorem completionIterate_add (M : Matrix (Fin d) (Fin d) ℝ)
    (μ : Fin d → ℝ) (a b : ℕ) :
    completionIterate M μ (a+b) = completionIterate M (completionIterate M μ a) b := by
  simp only [completionIterate_eq_vecMul, Matrix.vecMul_vecMul, pow_add]

theorem completionIterate_pow (M : Matrix (Fin d) (Fin d) ℝ)
    (μ : Fin d → ℝ) (m n : ℕ) :
    completionIterate (M^m) μ n = completionIterate M μ (m*n) := by
  simp only [completionIterate_eq_vecMul, pow_mul]

theorem completionIterate_fixed (M : Matrix (Fin d) (Fin d) ℝ)
    (p : Fin d → ℝ) (fixed : ∀ j, ∑ i, p i*M i j = p j) (n : ℕ) :
    completionIterate M p n = p := by
  induction n with
  | zero => rfl
  | succ n ih => funext j; simp only [completionIterate, ih, fixed]

theorem stochastic_power_rows (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (i : Fin d) : ∑ j, (M^m) i j = 1 := by
  have h := matrixHistory_rows (id : Unit → Unit) (fun _ => M) (fun _ => nonneg)
    1 1 (by norm_num) (by norm_num) (fun _ j => by rw [rows j]; exact ⟨le_rfl,le_rfl⟩) m () i
  simp only [constant_matrixHistory, one_pow] at h
  exact le_antisymm h.2 h.1

/-- The all-horizon bound includes remainder steps. A contractive block
subsequence alone would not justify convergence of the full iteration. -/
theorem primitive_completion_error (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (ε : ℝ) (floor : ∀ i j, ε ≤ (M^m) i j)
    (hc : 0 ≤ 1-(d:ℝ)*ε) (μ p : Fin d → ℝ)
    (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixed : ∀ j, ∑ i, p i*M i j = p j) (n : ℕ) :
    (∑ j, |completionIterate M μ n j-p j|) ≤
      (1-(d:ℝ)*ε)^(n/m)*∑ j, |μ j-p j| := by
  have rowsN := stochastic_power_rows M nonneg rows m
  have fixedN : ∀ j, ∑ i, p i*(M^m) i j = p j := by
    have h := completionIterate_fixed M p fixed m
    rw [completionIterate_eq_vecMul] at h
    intro j; exact congrFun h j
  have block := completionIterate_error (M^m) rowsN ε floor hc μ p massμ massp fixedN (n/m)
  rw [completionIterate_pow] at block
  have remainder := completionIterate_error M rows 0 nonneg (by norm_num)
    (completionIterate M μ (m*(n/m))) p
    ((completionIterate_mass M rows μ _).trans massμ) massp fixed (n%m)
  simp only [mul_zero, sub_zero, one_pow, one_mul] at remainder
  rw [← completionIterate_add, Nat.div_add_mod] at remainder
  exact remainder.trans block

/-- Primitive stochastic completion has a strictly positive stationary
distribution and every real mass-one input converges to it. The one-step
operator may have zero entries, as in the original clipped pilot kernels. -/
theorem primitive_completion_saturates (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (hm : 0 < m) (positive : ∀ i j, 0 < (M^m) i j) :
    ∃ p : Fin d → ℝ, (∀ j, 0 < p j) ∧ (∑ j, p j = 1) ∧
      (∀ j, ∑ i, p i*M i j = p j) ∧
      (∀ μ : Fin d → ℝ, (∑ i, μ i = 1) → ∀ j,
        Tendsto (fun n => completionIterate M μ n j) atTop (𝓝 (p j))) := by
  obtain ⟨ε, b, hε, entries⟩ := finite_positive_matrix_bounds (M^m) positive
  have floor : ∀ i j, ε ≤ (M^m) i j := fun i j => (entries i j).1
  have rowsN := stochastic_power_rows M nonneg rows m
  have hd : (0:ℝ) < d := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne d)
  have hc : 0 ≤ 1-(d:ℝ)*ε := by
    have h := Finset.sum_le_sum (s := Finset.univ) (fun j _ => floor 0 j)
    simp only [Finset.sum_const, Finset.card_fin, nsmul_eq_mul, rowsN] at h
    linarith
  have hc1 : 1-(d:ℝ)*ε < 1 := by nlinarith
  obtain ⟨p, hp, massp, fixedN⟩ := positive_completion_stationary_exists (M^m) rowsN ε hε floor
  have vectorFixedN : Matrix.vecMul p (M^m) = p := funext fixedN
  have commute : M*(M^m) = (M^m)*M := by rw [← pow_succ', ← pow_succ]
  let r := completionIterate M p 1
  have massr : ∑ i, r i = 1 := (completionIterate_mass M rows p 1).trans massp
  have fixedr : ∀ j, ∑ i, r i*(M^m) i j = r j := by
    have eq : Matrix.vecMul r (M^m) = r := by
      change Matrix.vecMul (Matrix.vecMul p M) (M^m) = Matrix.vecMul p M
      rw [Matrix.vecMul_vecMul, commute, ← Matrix.vecMul_vecMul, vectorFixedN]
    intro j; exact congrFun eq j
  have rp : r = p := completion_fixed_unique (M^m) rowsN ε floor hc1 r p
    massr massp fixedr fixedN
  have fixedM : ∀ j, ∑ i, p i*M i j = p j := fun j => congrFun rp j
  refine ⟨p, hp, massp, fixedM, ?_⟩
  intro μ massμ j
  have divlim : Tendsto (fun n : ℕ => n/m) atTop atTop := by
    apply tendsto_atTop.2
    intro a
    filter_upwards [eventually_ge_atTop (a*m)] with n hn
    exact (Nat.le_div_iff_mul_le hm).mpr hn
  have geometric : Tendsto (fun n : ℕ => (1-(d:ℝ)*ε)^(n/m)*∑ i, |μ i-p i|)
      atTop (𝓝 0) := by
    simpa using ((tendsto_pow_atTop_nhds_zero_of_lt_one hc hc1).comp divlim).mul_const
      (∑ i, |μ i-p i|)
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  apply squeeze_zero (fun _ => norm_nonneg _) _ geometric
  intro n
  rw [Real.norm_eq_abs]
  exact (Finset.single_le_sum (fun i _ => abs_nonneg (completionIterate M μ n i-p i))
    (Finset.mem_univ j)).trans
    (primitive_completion_error M nonneg rows m ε floor hc μ p massμ massp fixedM n)

theorem primitive_completion_unique (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (hm : 0 < m) (positive : ∀ i j, 0 < (M^m) i j)
    (μ ν : Fin d → ℝ) (massμ : ∑ i, μ i = 1) (massν : ∑ i, ν i = 1)
    (fixedμ : ∀ j, ∑ i, μ i*M i j = μ j)
    (fixedν : ∀ j, ∑ i, ν i*M i j = ν j) : μ = ν := by
  obtain ⟨p, _, _, _, lim⟩ := primitive_completion_saturates M nonneg rows m hm positive
  funext j
  have lμ := lim μ massμ j
  have lν := lim ν massν j
  simp only [completionIterate_fixed M μ fixedμ] at lμ
  simp only [completionIterate_fixed M ν fixedν] at lν
  exact (tendsto_nhds_unique tendsto_const_nhds lμ).trans
    (tendsto_nhds_unique tendsto_const_nhds lν).symm

/-- The block residual, rather than the consecutive-iterate residual alone,
controls stationary error with the positive-power minorization denominator. -/
theorem primitive_completion_stationary_error (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (ε : ℝ) (floor : ∀ i j, ε ≤ (M^m) i j) (hδ : 0 < (d:ℝ)*ε)
    (μ p : Fin d → ℝ) (massμ : ∑ i, μ i = 1) (massp : ∑ i, p i = 1)
    (fixed : ∀ j, ∑ i, p i*M i j = p j) :
    (∑ j, |μ j-p j|) ≤ (∑ j, |μ j-completionIterate M μ m j|) / ((d:ℝ)*ε) := by
  have fixedN : ∀ j, ∑ i, p i*(M^m) i j = p j := by
    have h := completionIterate_fixed M p fixed m
    rw [completionIterate_eq_vecMul] at h
    intro j; exact congrFun h j
  have h := completion_stationary_error_of_residual (M^m)
    (stochastic_power_rows M nonneg rows m) ε floor hδ μ p massμ massp fixedN
  simpa only [completionIterate_eq_vecMul, Matrix.vecMul, Matrix.dotProduct] using h

/-- The finite informant remains strictly positive when every kernel column
has a positive entry. This does not replace its finite cutoff by stationarity. -/
theorem completionIterate_positive_columns (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (columns : ∀ j, ∃ i, 0 < M i j)
    (μ : Fin d → ℝ) (positiveμ : ∀ i, 0 < μ i) (n : ℕ) (j : Fin d) :
    0 < completionIterate M μ n j := by
  induction n generalizing j with
  | zero => exact positiveμ j
  | succ n ih =>
    obtain ⟨i, hi⟩ := columns j
    have term := mul_pos (ih i) hi
    have lower := Finset.single_le_sum
      (fun h _ => mul_nonneg (ih h).le (nonneg h j)) (Finset.mem_univ i)
    exact term.trans_le lower

theorem nonnegative_matrix_product (A B : Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ i j, 0 ≤ A i j) (hB : ∀ i j, 0 ≤ B i j) (i j : Fin d) :
    0 ≤ (A*B) i j := by
  change 0 ≤ ∑ k, A i k*B k j
  exact Finset.sum_nonneg fun k _ => mul_nonneg (hA i k) (hB k j)

theorem stochastic_matrix_product (A B : Matrix (Fin d) (Fin d) ℝ)
    (rowsA : ∀ i, ∑ j, A i j = 1) (rowsB : ∀ i, ∑ j, B i j = 1) (i : Fin d) :
    ∑ j, (A*B) i j = 1 := by
  simp only [Matrix.mul_apply]
  rw [Finset.sum_comm]
  simp only [← Finset.mul_sum, rowsB, mul_one, rowsA]

/-- A prototype lift with positive diagonal retains every positive transport
edge. The actual B Q U operator is B times this block-prototype matrix. -/
theorem prototype_lift_retains_transport (B U : Matrix (Fin d) (Fin d) ℝ)
    (hB : ∀ i j, 0 ≤ B i j) (hU : ∀ i j, 0 ≤ U i j)
    (β : ℝ) (diagonal : ∀ j, β ≤ U j j) (i j : Fin d) :
    β*B i j ≤ (B*U) i j := by
  have term := mul_le_mul_of_nonneg_left (diagonal j) (hB i j)
  have lower := Finset.single_le_sum
    (fun h _ => mul_nonneg (hB i h) (hU h j)) (Finset.mem_univ j)
  have rewriteTerm : β*B i j ≤ B i j*U j j := by simpa only [mul_comm] using term
  exact rewriteTerm.trans lower

theorem matrix_power_domination (A B : Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ i j, 0 ≤ A i j)
    (β : ℝ) (hβ : 0 ≤ β) (bound : ∀ i j, β*A i j ≤ B i j)
    (n : ℕ) (i j : Fin d) : β^n*(A^n) i j ≤ (B^n) i j := by
  have powersA : ∀ (n : ℕ) (i j : Fin d), 0 ≤ (A^n) i j := by
    intro n i j
    have h := matrixHistory_nonnegative (id : Unit → Unit) (fun _ => A) (fun _ => hA) n () i j
    simpa only [constant_matrixHistory] using h
  induction n generalizing i j with
  | zero => simp
  | succ n ih =>
    calc
      β^(n+1)*(A^(n+1)) i j = ∑ k, (β^n*(A^n) i k)*(β*A k j) := by
        rw [pow_succ, pow_succ, Matrix.mul_apply, Finset.mul_sum]
        apply Finset.sum_congr rfl; intro k _; ring
      _ ≤ ∑ k, (B^n) i k*B k j := by
        apply Finset.sum_le_sum; intro k _
        exact mul_le_mul (ih i k) (bound k j)
          (mul_nonneg hβ (hA k j))
          ((mul_nonneg (pow_nonneg hβ n) (powersA n i k)).trans (ih i k))
      _ = (B^(n+1)) i j := by rw [pow_succ, Matrix.mul_apply]

/-- Return to the actual completion constructor: primitive transport plus
positive prototype diagonal yields primitive B Q U, and hence saturation.
Neither stationary existence nor completion convergence is an input. -/
theorem primitive_transport_completion_saturates (B U : Matrix (Fin d) (Fin d) ℝ)
    (hB : ∀ i j, 0 ≤ B i j) (hU : ∀ i j, 0 ≤ U i j)
    (rowsB : ∀ i, ∑ j, B i j = 1) (rowsU : ∀ i, ∑ j, U i j = 1)
    (β : ℝ) (hβ : 0 < β) (diagonal : ∀ j, β ≤ U j j)
    (m : ℕ) (hm : 0 < m) (positive : ∀ i j, 0 < (B^m) i j) :
    ∃ p : Fin d → ℝ, (∀ j, 0 < p j) ∧ (∑ j, p j = 1) ∧
      (∀ j, ∑ i, p i*(B*U) i j = p j) ∧
      (∀ μ : Fin d → ℝ, (∑ i, μ i = 1) → ∀ j,
        Tendsto (fun n => completionIterate (B*U) μ n j) atTop (𝓝 (p j))) := by
  have hE := nonnegative_matrix_product B U hB hU
  apply primitive_completion_saturates (B*U) hE (stochastic_matrix_product B U rowsB rowsU) m hm
  intro i j
  have bound := matrix_power_domination B (B*U) hB β hβ.le
    (prototype_lift_retains_transport B U hB hU β diagonal) m i j
  exact (mul_pos (pow_pos hβ m) (positive i j)).trans_le bound

/-- Exact finite-path certificates give positive powers. The support verifier
uses this implication; numeric closeness to stationarity is irrelevant. -/
theorem matrix_power_positive_of_path (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (n : ℕ) (path : ℕ → Fin d)
    (edges : ∀ k, k < n → 0 < M (path k) (path (k+1))) :
    0 < (M^n) (path 0) (path n) := by
  have powers : ∀ (n : ℕ) (i j : Fin d), 0 ≤ (M^n) i j := by
    intro n i j
    have h := matrixHistory_nonnegative (id : Unit → Unit) (fun _ => M) (fun _ => nonneg) n () i j
    simpa only [constant_matrixHistory] using h
  induction n generalizing path with
  | zero => simp
  | succ n ih =>
    have tail := ih (fun k => path (k+1)) (fun k hk => edges (k+1) (Nat.succ_lt_succ hk))
    have first := edges 0 (Nat.zero_lt_succ n)
    have positive := mul_pos first tail
    have lower : M (path 0) (path 1)*(M^n) (path 1) (path (n+1)) ≤
        (M^(n+1)) (path 0) (path (n+1)) := by
      rw [pow_succ', Matrix.mul_apply]
      exact Finset.single_le_sum (fun k _ => mul_nonneg (nonneg (path 0) k)
        (powers n k (path (n+1)))) (Finset.mem_univ (path 1))
    exact positive.trans_le lower

/-- If the exact base descriptor determines the primitive completion
operator, all exact completed readouts factor through it. Multiple rounded
transient outputs of the same operator cannot certify strict extension. -/
theorem primitive_completion_readout_factorizes {X B : Type*} (base : X → B)
    (E : B → Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ b i j, 0 ≤ E b i j) (rows : ∀ b i, ∑ j, E b i j = 1)
    (m : B → ℕ) (hm : ∀ b, 0 < m b) (positive : ∀ b i j, 0 < ((E b)^(m b)) i j)
    (readout : X → Fin d → ℝ) (mass : ∀ x, ∑ i, readout x i = 1)
    (fixed : ∀ x j, ∑ i, readout x i*E (base x) i j = readout x j) :
    ∃ f : B → Fin d → ℝ, readout = f ∘ base := by
  have existsP : ∀ b, ∃ p : Fin d → ℝ, (∑ i, p i = 1) ∧
      (∀ j, ∑ i, p i*E b i j = p j) := by
    intro b
    obtain ⟨p, _, massp, fixedp, _⟩ := primitive_completion_saturates
      (E b) (nonneg b) (rows b) (m b) (hm b) (positive b)
    exact ⟨p, massp, fixedp⟩
  choose p properties using existsP
  refine ⟨p, ?_⟩
  funext x
  exact primitive_completion_unique (E (base x)) (nonneg (base x)) (rows (base x))
    (m (base x)) (hm (base x)) (positive (base x)) (readout x) (p (base x))
    (mass x) (properties (base x)).1 (fixed x) (properties (base x)).2

def completionLimitClosure (p : Fin d → ℝ) : Matrix (Fin d) (Fin d) ℝ := fun _ j => p j

theorem completionLimitClosure_idempotent (p : Fin d → ℝ) (mass : ∑ i, p i = 1) :
    completionLimitClosure p*completionLimitClosure p = completionLimitClosure p := by
  ext i j
  simp only [Matrix.mul_apply, completionLimitClosure, ← Finset.sum_mul, mass, one_mul]

theorem completionLimitClosure_absorbs (M : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, M i j = 1) (p : Fin d → ℝ)
    (fixed : ∀ j, ∑ i, p i*M i j = p j) :
    M*completionLimitClosure p = completionLimitClosure p ∧
      completionLimitClosure p*M = completionLimitClosure p := by
  constructor
  · ext i j
    simp only [Matrix.mul_apply, completionLimitClosure, ← Finset.sum_mul, rows, one_mul]
  · ext i j
    simp only [Matrix.mul_apply, completionLimitClosure, fixed]

/-- It is the LIMIT closure that is idempotent; the actual one-step B Q U
need not be. Existence and full convergence come from primitive saturation. -/
theorem primitive_completion_idempotent_limit (M : Matrix (Fin d) (Fin d) ℝ)
    (nonneg : ∀ i j, 0 ≤ M i j) (rows : ∀ i, ∑ j, M i j = 1)
    (m : ℕ) (hm : 0 < m) (positive : ∀ i j, 0 < (M^m) i j) :
    ∃ C : Matrix (Fin d) (Fin d) ℝ, C*C = C ∧ M*C = C ∧ C*M = C ∧
      (∀ i j, 0 < C i j) ∧
      (∀ μ : Fin d → ℝ, (∑ i, μ i = 1) → ∀ i j,
        Tendsto (fun n => completionIterate M μ n j) atTop (𝓝 (C i j))) := by
  obtain ⟨p, hp, mass, fixed, lim⟩ := primitive_completion_saturates M nonneg rows m hm positive
  have absorption := completionLimitClosure_absorbs M rows p fixed
  exact ⟨completionLimitClosure p, completionLimitClosure_idempotent p mass,
    absorption.1, absorption.2, fun _ j => hp j, fun μ h _ j => lim μ h j⟩

end
end CantorAudit
