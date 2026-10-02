import MatrixPressure
import KernelLawfulness
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-! Pressure applicability for ORIGINAL stochastic kernels with zeros.
Uniform positive-entry minorization is unnecessary for existence. Each row
has an entry >=1/d, giving a positive row floor for every finite s>=0.
Zero entries remain absent edges at s=0. The carrier is explicitly nonempty
and F maps it to itself; these hypotheses are not original-shell certificates.
-/
namespace CantorAudit
noncomputable section
open Filter
open scoped Topology
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass
variable {d : ℕ} [NeZero d] {X : Type*} [Nonempty X]

theorem stochastic_row_entry_bound (k : Fin d → ℝ) (hk : ∀ j, 0 ≤ k j)
    (mass : ∑ j, k j = 1) :
    (∀ j, k j ≤ 1) ∧ ∃ j, 1/(d:ℝ) ≤ k j := by
  have hd : (0:ℝ) < d := by exact_mod_cast (NeZero.pos d)
  constructor
  · intro j
    rw [← mass]
    exact Finset.single_le_sum (fun i _ => hk i) (Finset.mem_univ j)
  · obtain ⟨j, _, hj⟩ := Finset.exists_max_image Finset.univ k Finset.univ_nonempty
    refine ⟨j, (div_le_iff hd).mpr ?_⟩
    have h : ∑ i, k i ≤ ∑ _i : Fin d, k j :=
      Finset.sum_le_sum fun i _ => hj i (Finset.mem_univ i)
    simpa only [mass, Finset.sum_const, Finset.card_univ, Fintype.card_fin,
      nsmul_eq_mul, mul_comm] using h

def sparseSelectorMatrix (K : X → Matrix (Fin d) (Fin d) ℝ)
    (q : X → ℝ) (s : ℝ) (x : X) : Matrix (Fin d) (Fin d) ℝ :=
  fun i j => if K x i j = 0 then 0 else Real.exp (-s*q x)*(K x i j)^s

theorem sparseSelectorMatrix_nonnegative (K : X → Matrix (Fin d) (Fin d) ℝ)
    (q : X → ℝ) (s : ℝ) (hK : ∀ x i j, 0 ≤ K x i j) :
    ∀ x i j, 0 ≤ sparseSelectorMatrix K q s x i j := by
  intro x i j
  simp only [sparseSelectorMatrix]
  split_ifs
  · exact le_refl _
  · exact mul_nonneg (Real.exp_pos _).le (Real.rpow_nonneg (hK x i j) _)

/-- Coarse bounds suffice for finite pressure, including permutations and
singular stochastic kernels. Sharper Jensen bounds are not required here. -/
theorem sparseSelectorMatrix_row_bounds (K : X → Matrix (Fin d) (Fin d) ℝ)
    (q : X → ℝ) (s lo hi : ℝ) (hs : 0 ≤ s)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x ∧ q x ≤ hi) (x : X) (i : Fin d) :
    Real.exp (-s*hi)*(1/(d:ℝ))^s ≤ ∑ j, sparseSelectorMatrix K q s x i j ∧
      (∑ j, sparseSelectorMatrix K q s x i j) ≤ (d:ℝ)*Real.exp (-s*lo) := by
  have hd : (0:ℝ) < d := by exact_mod_cast (NeZero.pos d)
  have hdInv : 0 < 1/(d:ℝ) := one_div_pos.mpr hd
  obtain ⟨upper, j, hj⟩ := stochastic_row_entry_bound (K x i) (hK x i) (mass x i)
  have hnonneg := sparseSelectorMatrix_nonnegative K q s hK x i
  constructor
  · have positive : 0 < K x i j := hdInv.trans_le hj
    have e : Real.exp (-s*hi) ≤ Real.exp (-s*q x) :=
      Real.exp_le_exp.mpr (by nlinarith [(hq x).2])
    have p : (1/(d:ℝ))^s ≤ (K x i j)^s := Real.rpow_le_rpow hdInv.le hj hs
    calc
      _ ≤ Real.exp (-s*q x)*(K x i j)^s :=
        mul_le_mul e p (Real.rpow_nonneg hdInv.le _) (Real.exp_pos _).le
      _ = sparseSelectorMatrix K q s x i j := by
        simp only [sparseSelectorMatrix, if_neg positive.ne']
      _ ≤ _ := Finset.single_le_sum (fun k _ => hnonneg k) (Finset.mem_univ j)
  · have one : ∀ j, sparseSelectorMatrix K q s x i j ≤ Real.exp (-s*lo) := by
      intro j
      simp only [sparseSelectorMatrix]
      split_ifs with hz
      · exact (Real.exp_pos _).le
      · have e : Real.exp (-s*q x) ≤ Real.exp (-s*lo) :=
          Real.exp_le_exp.mpr (by nlinarith [(hq x).1])
        have p : (K x i j)^s ≤ 1 := by
          simpa only [Real.one_rpow] using Real.rpow_le_rpow (hK x i j) (upper j) hs
        have h := mul_le_mul e p (Real.rpow_nonneg (hK x i j) _) (Real.exp_pos _).le
        simpa only [mul_one] using h
    calc
      _ ≤ ∑ _j : Fin d, Real.exp (-s*lo) := Finset.sum_le_sum fun j _ => one j
      _ = _ := by simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]

/-- Original nonnegative stochasticity and bounded q supply all exponential
inputs to the actual Fekete cocycle theorem; no entry floor is a premise. -/
theorem sparse_selector_pressure_exists (F : X → X)
    (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ) (s lo hi : ℝ) (hs : 0 ≤ s)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x ∧ q x ≤ hi) :
    ∃ P : ℝ, Tendsto (fun n =>
      Real.log (matrixHistoryEnvelope F (sparseSelectorMatrix K q s) n)/n) atTop (𝓝 P) := by
  have hd : (0:ℝ) < d := by exact_mod_cast (NeZero.pos d)
  apply matrix_pressure_exists F (sparseSelectorMatrix K q s)
    (sparseSelectorMatrix_nonnegative K q s hK)
    (Real.exp (-s*hi)*(1/(d:ℝ))^s) ((d:ℝ)*Real.exp (-s*lo))
  · exact mul_pos (Real.exp_pos _) (Real.rpow_pos_of_pos (one_div_pos.mpr hd) _)
  · exact (mul_pos hd (Real.exp_pos _)).le
  · exact fun x i => sparseSelectorMatrix_row_bounds K q s lo hi hs hK mass hq x i

theorem sparseSelectorMatrix_parameter_bound (K : X → Matrix (Fin d) (Fin d) ℝ)
    (q : X → ℝ) (s t lo : ℝ) (_hs : 0 ≤ s) (hst : s ≤ t)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x) (x : X) (i j : Fin d) :
    sparseSelectorMatrix K q t x i j ≤
      Real.exp (-(t-s)*lo)*sparseSelectorMatrix K q s x i j := by
  by_cases hz : K x i j = 0
  · simp [sparseSelectorMatrix, hz]
  have positive : 0 < K x i j := lt_of_le_of_ne (hK x i j) (Ne.symm hz)
  have upper := (stochastic_row_entry_bound (K x i) (hK x i) (mass x i)).1 j
  have factor : Real.exp (-(t-s)*q x)*(K x i j)^(t-s) ≤ Real.exp (-(t-s)*lo) := by
    have e : Real.exp (-(t-s)*q x) ≤ Real.exp (-(t-s)*lo) :=
      Real.exp_le_exp.mpr (by nlinarith [hq x])
    have p : (K x i j)^(t-s) ≤ 1 := by
      simpa only [Real.one_rpow] using Real.rpow_le_rpow positive.le upper (sub_nonneg.mpr hst)
    simpa only [mul_one] using
      mul_le_mul e p (Real.rpow_nonneg positive.le _) (Real.exp_pos _).le
  have poweq : (K x i j)^t = (K x i j)^s*(K x i j)^(t-s) := by
    calc
      _ = (K x i j)^(s+(t-s)) := by congr 1; ring
      _ = _ := Real.rpow_add positive _ _
  have expeq : Real.exp (-t*q x) = Real.exp (-s*q x)*Real.exp (-(t-s)*q x) := by
    rw [← Real.exp_add]; congr 1; ring
  simp only [sparseSelectorMatrix, if_neg hz]
  calc
    _ = (Real.exp (-(t-s)*q x)*(K x i j)^(t-s))*(Real.exp (-s*q x)*(K x i j)^s) := by
      rw [poweq, expeq]; ring
    _ ≤ _ := mul_le_mul_of_nonneg_right factor
      (mul_nonneg (Real.exp_pos _).le (Real.rpow_nonneg positive.le _))

/-- Entrywise domination propagates through the actual ordered moving
history, with one factor of c per time step. -/
theorem moving_history_scaled_domination (F : X → X)
    (A B : X → Matrix (Fin d) (Fin d) ℝ) (c : ℝ) (hc : 0 ≤ c)
    (hA : ∀ x i j, 0 ≤ A x i j) (hB : ∀ x i j, 0 ≤ B x i j)
    (step : ∀ x i j, B x i j ≤ c*A x i j) (n : ℕ) (x : X) (i j : Fin d) :
    kernelProduct F B n x i j ≤ c^n*kernelProduct F A n x i j := by
  induction n generalizing x i j with
  | zero => simp [kernelProduct]
  | succ n ih =>
    simp only [kernelProduct, Matrix.mul_apply]
    calc
      _ ≤ ∑ k, (c*A x i k)*(c^n*kernelProduct F A n (F x) k j) :=
        Finset.sum_le_sum fun k _ => mul_le_mul (step x i k) (ih (F x) k j)
          (matrixHistory_nonnegative F B hB n (F x) k j) (mul_nonneg hc (hA x i k))
      _ = _ := by
        simp only [pow_succ]
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro k _; ring

theorem moving_envelope_scaled_domination (F : X → X)
    (A B : X → Matrix (Fin d) (Fin d) ℝ) (c b : ℝ) (hc : 0 ≤ c)
    (hA : ∀ x i j, 0 ≤ A x i j) (hB : ∀ x i j, 0 ≤ B x i j)
    (step : ∀ x i j, B x i j ≤ c*A x i j)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b^n) (n : ℕ) :
    matrixHistoryEnvelope F B n ≤ c^n*matrixHistoryEnvelope F A n := by
  apply csSup_le (Set.range_nonempty _)
  rintro y ⟨x,rfl⟩
  have normbound : ‖kernelProduct F B n x‖ ≤ c^n*‖kernelProduct F A n x‖ := by
    apply positiveMatrix_norm_le _ (matrixHistory_nonnegative F B hB n x) _
      (mul_nonneg (pow_nonneg hc n) (norm_nonneg _))
    intro i
    calc
      _ ≤ ∑ j, c^n*kernelProduct F A n x i j := Finset.sum_le_sum fun j _ =>
        moving_history_scaled_domination F A B c hc hA hB step n x i j
      _ = c^n*(∑ j, kernelProduct F A n x i j) := by rw [Finset.mul_sum]
      _ ≤ _ := mul_le_mul_of_nonneg_left
        (positiveMatrix_row_le_norm _ (matrixHistory_nonnegative F A hA n x) i) (pow_nonneg hc n)
  exact normbound.trans (mul_le_mul_of_nonneg_left
    (kernelNorm_le_envelope F A b upper n x) (pow_nonneg hc n))

theorem pressure_comparison_of_scaling (Z W : ℕ → ℝ) (c P Q : ℝ) (hc : 0 < c)
    (hZ : ∀ n, 0 < Z n) (hW : ∀ n, 0 < W n)
    (bound : ∀ n, W n ≤ c^n*Z n)
    (hP : Tendsto (fun n => Real.log (Z n)/n) atTop (𝓝 P))
    (hQ : Tendsto (fun n => Real.log (W n)/n) atTop (𝓝 Q)) :
    Q-P ≤ Real.log c := by
  apply pressure_upper_of_exponential (fun n => W n/Z n) c (Q-P) hc
    (fun n => div_pos (hW n) (hZ n))
    (fun n => (div_le_iff (hZ n)).mpr (bound n))
  have h := hQ.sub hP
  simpa only [Real.log_div (hW _).ne' (hZ _).ne', sub_div] using h

/-- A genuine pressure secant upper bound, derived from original nonnegative
stochastic kernels and the selector's q floor, not supplied as a hypothesis. -/
theorem sparse_selector_pressure_parameter_bound (F : X → X)
    (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ) (s t lo hi P Q : ℝ)
    (hs : 0 ≤ s) (hst : s ≤ t)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x ∧ q x ≤ hi)
    (hP : Tendsto (fun n => Real.log
      (matrixHistoryEnvelope F (sparseSelectorMatrix K q s) n)/n) atTop (𝓝 P))
    (hQ : Tendsto (fun n => Real.log
      (matrixHistoryEnvelope F (sparseSelectorMatrix K q t) n)/n) atTop (𝓝 Q)) :
    Q-P ≤ -(t-s)*lo := by
  let A := sparseSelectorMatrix K q s
  let B := sparseSelectorMatrix K q t
  let c := Real.exp (-(t-s)*lo)
  have hd : (0:ℝ) < d := by exact_mod_cast (NeZero.pos d)
  have ht : 0 ≤ t := hs.trans hst
  have aPos : ∀ u : ℝ, 0 < Real.exp (-u*hi)*(1/(d:ℝ))^u :=
    fun u => mul_pos (Real.exp_pos _) (Real.rpow_pos_of_pos (one_div_pos.mpr hd) _)
  have bPos : ∀ u : ℝ, 0 < (d:ℝ)*Real.exp (-u*lo) := fun u => mul_pos hd (Real.exp_pos _)
  have hA := sparseSelectorMatrix_nonnegative K q s hK
  have hB := sparseSelectorMatrix_nonnegative K q t hK
  have lower : ∀ u, 0 ≤ u → ∀ n x,
      (Real.exp (-u*hi)*(1/(d:ℝ))^u)^n ≤
        ‖kernelProduct F (sparseSelectorMatrix K q u) n x‖ := by
    intro u hu n x
    exact ((matrixHistory_rows F _ (sparseSelectorMatrix_nonnegative K q u hK)
      _ _ (aPos u).le (bPos u).le
      (fun x i => sparseSelectorMatrix_row_bounds K q u lo hi hu hK mass hq x i)
      n x 0).1).trans (positiveMatrix_row_le_norm _
        (matrixHistory_nonnegative F _ (sparseSelectorMatrix_nonnegative K q u hK) n x) 0)
  have upper : ∀ u, 0 ≤ u → ∀ n x,
      ‖kernelProduct F (sparseSelectorMatrix K q u) n x‖ ≤ ((d:ℝ)*Real.exp (-u*lo))^n := by
    intro u hu n x
    apply positiveMatrix_norm_le _
      (matrixHistory_nonnegative F _ (sparseSelectorMatrix_nonnegative K q u hK) n x)
      _ (pow_nonneg (bPos u).le n)
    intro i
    exact (matrixHistory_rows F _ (sparseSelectorMatrix_nonnegative K q u hK)
      _ _ (aPos u).le (bPos u).le
      (fun x i => sparseSelectorMatrix_row_bounds K q u lo hi hu hK mass hq x i) n x i).2
  have positive : ∀ u, 0 ≤ u → ∀ n,
      0 < matrixHistoryEnvelope F (sparseSelectorMatrix K q u) n := by
    intro u hu n
    exact kernelEnvelope_positive F _ _ _ (aPos u) (lower u hu) (upper u hu) n
  have bound := moving_envelope_scaled_domination F A B c ((d:ℝ)*Real.exp (-s*lo))
    (Real.exp_pos _).le hA hB
    (fun x i j => sparseSelectorMatrix_parameter_bound K q s t lo hs hst hK mass
      (fun x => (hq x).1) x i j) (upper s hs)
  have h := pressure_comparison_of_scaling _ _ c P Q (Real.exp_pos _)
    (positive s hs) (positive t ht) bound hP hQ
  simpa only [c, Real.log_exp] using h

theorem sparse_selector_pressure_strictAnti (F : X → X)
    (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ) (lo hi : ℝ) (hlo : 0 < lo)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x ∧ q x ≤ hi) (P : ℝ → ℝ)
    (limits : ∀ s, 0 ≤ s → Tendsto (fun n => Real.log
      (matrixHistoryEnvelope F (sparseSelectorMatrix K q s) n)/n) atTop (𝓝 (P s))) :
    StrictAntiOn P (Set.Ici 0) := by
  intro s hs t ht hst
  have h := sparse_selector_pressure_parameter_bound F K q s t lo hi (P s) (P t)
    hs hst.le hK mass hq (limits s hs) (limits t ht)
  have positive : 0 < (t-s)*lo := mul_pos (sub_pos.mpr hst) hlo
  linarith

theorem sparse_selector_pressure_at_one (F : X → X)
    (K : X → Matrix (Fin d) (Fin d) ℝ) (q : X → ℝ) (lo hi P : ℝ)
    (hK : ∀ x i j, 0 ≤ K x i j) (mass : ∀ x i, ∑ j, K x i j = 1)
    (hq : ∀ x, lo ≤ q x ∧ q x ≤ hi)
    (limit : Tendsto (fun n => Real.log
      (matrixHistoryEnvelope F (sparseSelectorMatrix K q 1) n)/n) atTop (𝓝 P)) :
    P ≤ -lo := by
  let A := sparseSelectorMatrix K q 1
  have hA := sparseSelectorMatrix_nonnegative K q 1 hK
  have rows : ∀ x i, Real.exp (-hi) ≤ ∑ j, A x i j ∧
      (∑ j, A x i j) ≤ Real.exp (-lo) := by
    intro x i
    have eq : ∑ j, A x i j = Real.exp (-q x) := by
      have he : ∀ j, A x i j = Real.exp (-q x)*K x i j := by
        intro j
        by_cases hz : K x i j = 0
        · simp [A, sparseSelectorMatrix, hz]
        · simp [A, sparseSelectorMatrix, hz]
      simp only [he, ← Finset.mul_sum, mass, mul_one]
    rw [eq]
    exact ⟨Real.exp_le_exp.mpr (by linarith [(hq x).2]),
      Real.exp_le_exp.mpr (by linarith [(hq x).1])⟩
  have lower : ∀ n x, (Real.exp (-hi))^n ≤ ‖kernelProduct F A n x‖ := by
    intro n x
    exact ((matrixHistory_rows F A hA _ _ (Real.exp_pos _).le (Real.exp_pos _).le rows n x 0).1).trans
      (positiveMatrix_row_le_norm _ (matrixHistory_nonnegative F A hA n x) 0)
  have upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ (Real.exp (-lo))^n := by
    intro n x
    exact positiveMatrix_norm_le _ (matrixHistory_nonnegative F A hA n x)
      _ (pow_nonneg (Real.exp_pos _).le n)
      (fun i => (matrixHistory_rows F A hA _ _ (Real.exp_pos _).le (Real.exp_pos _).le rows n x i).2)
  have positive := kernelEnvelope_positive F A _ _ (Real.exp_pos _) lower upper
  have envelopeUpper : ∀ n, matrixHistoryEnvelope F A n ≤ (Real.exp (-lo))^n := by
    intro n
    exact csSup_le (Set.range_nonempty _) (fun _ ⟨x,hx⟩ => hx ▸ upper n x)
  have h := pressure_upper_of_exponential _ (Real.exp (-lo)) P
    (Real.exp_pos _) positive envelopeUpper limit
  simpa only [Real.log_exp] using h

/-- The two ORIGINAL scripts have different coefficients. `closure=true`
represents the closure runner; false the pressure-existence/restoration one.
Their identical scalar-input bounds imply a common unclamped q interval. -/
def originalSelectorArgument (closure : Bool) (variation lens packaging budget tau entropy : ℝ) : ℝ :=
  if closure then variation+(25/100)*lens+(30/100)*packaging+(5/100)*(budget/12)
      +(5/100)*tau+(5/100)*entropy
  else variation+(28/100)*lens+(32/100)*packaging+(10/100)*(budget/12)
      +(8/100)*tau+(5/100)*entropy

theorem original_selector_observable_bounds (closure : Bool)
    (variation lens packaging budget tau entropy : ℝ)
    (hv : 0 ≤ variation ∧ variation ≤ 7) (hl : 39/100 ≤ lens ∧ lens ≤ 5/4)
    (hp : 412/1000 ≤ packaging ∧ packaging ≤ 1) (hb : 0 ≤ budget ∧ budget ≤ 12)
    (ht : 3/5 ≤ tau ∧ tau ≤ 4) (he : 0 ≤ entropy ∧ entropy ≤ 2) :
    Real.log (5/4) ≤ Real.log (1+originalSelectorArgument closure variation lens packaging budget tau entropy) ∧
      Real.log (1+originalSelectorArgument closure variation lens packaging budget tau entropy) ≤ Real.log 10 := by
  have bounds : (5/4:ℝ) ≤ 1+originalSelectorArgument closure variation lens packaging budget tau entropy ∧
      1+originalSelectorArgument closure variation lens packaging budget tau entropy ≤ 10 := by
    cases closure <;> simp only [originalSelectorArgument, Bool.false_eq_true, if_false, if_true] <;>
      constructor <;> nlinarith [hv.1,hv.2,hl.1,hl.2,hp.1,hp.2,hb.1,hb.2,ht.1,ht.2,he.1,he.2]
  have positive : 0 < 1+originalSelectorArgument closure variation lens packaging budget tau entropy :=
    lt_of_lt_of_le (by norm_num : (0:ℝ)<5/4) bounds.1
  exact ⟨Real.log_le_log (by norm_num) bounds.1,Real.log_le_log positive bounds.2⟩

/-- The original phase-8 budget branch's derived P1/P2 core floor survives
ALL legal clipping noise and row normalization for both original dimensions.
The source-to-P1/P2 floor is derived in the analytic sparse-pressure note;
it is not an inserted kernel-minorization operation. -/
theorem original_budget_core_survives_noise (hd : d ≤ 20) (k e : Fin d → ℝ)
    (hk : ∀ j, 0 ≤ k j) (mass : ∑ j, k j = 1)
    (noise : ∀ j, -(9/2000:ℝ) ≤ e j ∧ e j ≤ 9/2000)
    (j : Fin d) (core_floor : (13/20:ℝ)*(501/4000)*(1799/20000)/(79/50) ≤ k j) :
    (1/10000:ℝ) < noiseNormalizedRow k e j := by
  have hdR : (d:ℝ) ≤ 20 := by exact_mod_cast hd
  have lower := clippedRow_mass_lower k e (9/2000) mass (fun j => (noise j).1)
  have positive : 0 < ∑ h, clippedRow k e h := by nlinarith
  have upper : ∑ h, clippedRow k e h ≤ (109/100:ℝ) := by
    have bound : ∀ h, clippedRow k e h ≤ k h+9/2000 := by
      intro h
      exact max_le (by linarith [hk h]) (by linarith [(noise h).2])
    have sum : (∑ h, clippedRow k e h) ≤ ∑ h : Fin d, (k h+9/2000) :=
      Finset.sum_le_sum (fun h _ => bound h)
    simp only [Finset.sum_add_distrib,mass,Finset.sum_const,Finset.card_univ,
      Fintype.card_fin,nsmul_eq_mul] at sum
    nlinarith
  have coord : (13/20:ℝ)*(501/4000)*(1799/20000)/(79/50)-9/2000 ≤ clippedRow k e j := by
    have h := le_max_right (0:ℝ) (k j+e j)
    change _ ≤ max 0 (k j+e j)
    linarith [(noise j).1]
  have strict : (1/10000:ℝ)*(109/100) <
      (13/20:ℝ)*(501/4000)*(1799/20000)/(79/50)-9/2000 := by norm_num
  change (1/10000:ℝ) < clippedRow k e j/(∑ h, clippedRow k e h)
  apply (lt_div_iff positive).mpr
  have product := mul_le_mul_of_nonneg_left upper (by norm_num : (0:ℝ) ≤ 1/10000)
  exact (product.trans_lt strict).trans_le coord

/-- The derived four-column floor recurring every twelve steps gives the
positive-pressure anchor at s=1/32. This checks the actual constants; the
phase-count and row-product return are proved in the analytic note. -/
theorem original_branch_root_anchor :
    (0:ℝ) < (Real.log 4-(1/2)*Real.log 10)/12 := by
  have h : Real.log (10:ℝ) < Real.log 16 := Real.log_lt_log (by norm_num) (by norm_num)
  have h16 : Real.log (16:ℝ) = 2*Real.log 4 := by
    convert Real.log_pow (4:ℝ) 2 using 1
    norm_num
  rw [h16] at h
  nlinarith

end
end CantorAudit
