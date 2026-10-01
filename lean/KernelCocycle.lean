import CantorAudit

/-!
An actual operator cocycle envelope, with its comparison derived from
multiplication and forward evolution. Uniform exponential bounds are visible
premises; this file does not assert that the simulator satisfies them.
-/

namespace CantorAudit
open Filter Set
open scoped Topology

variable {X V : Type*} [Nonempty X] [NormedRing V] [NormOneClass V]

def kernelProduct (F : X → X) (A : X → V) : ℕ → X → V
  | 0, _ => 1
  | n + 1, x => A x * kernelProduct F A n (F x)

theorem kernelProduct_split (F : X → X) (A : X → V) (n m : ℕ) (x : X) :
    kernelProduct F A (n + m) x =
      kernelProduct F A n x * kernelProduct F A m (F^[n] x) := by
  induction n generalizing x with
  | zero => simp [kernelProduct]
  | succ n ih =>
    simpa [Nat.succ_add, kernelProduct, Function.iterate_succ_apply, mul_assoc] using
      congrArg (fun z => A x * z) (ih (F x))

noncomputable def kernelEnvelope (F : X → X) (A : X → V) (n : ℕ) : ℝ :=
  sSup (range fun x => ‖kernelProduct F A n x‖)

theorem kernelEnvelope_bdd (F : X → X) (A : X → V) (b : ℝ)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) (n : ℕ) :
    BddAbove (range fun x => ‖kernelProduct F A n x‖) := by
  refine ⟨b ^ n, ?_⟩
  rintro y ⟨x, rfl⟩
  exact upper n x

theorem kernelNorm_le_envelope (F : X → X) (A : X → V) (b : ℝ)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) (n : ℕ) (x : X) :
    ‖kernelProduct F A n x‖ ≤ kernelEnvelope F A n :=
  le_csSup (kernelEnvelope_bdd F A b upper n) (mem_range_self x)

theorem kernelEnvelope_positive (F : X → X) (A : X → V) (c b : ℝ)
    (hc : 0 < c)
    (lower : ∀ n x, c ^ n ≤ ‖kernelProduct F A n x‖)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) (n : ℕ) :
    0 < kernelEnvelope F A n := by
  let x : X := Classical.choice inferInstance
  exact lt_of_lt_of_le (pow_pos hc n)
    ((lower n x).trans (kernelNorm_le_envelope F A b upper n x))

theorem kernelEnvelope_submultiplicative (F : X → X) (A : X → V) (c b : ℝ)
    (hc : 0 < c)
    (lower : ∀ n x, c ^ n ≤ ‖kernelProduct F A n x‖)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) (n m : ℕ) :
    kernelEnvelope F A (n + m) ≤ kernelEnvelope F A n * kernelEnvelope F A m := by
  apply csSup_le (range_nonempty _)
  rintro y ⟨x, rfl⟩
  change ‖kernelProduct F A (n + m) x‖ ≤ _
  rw [kernelProduct_split]
  calc
    ‖kernelProduct F A n x * kernelProduct F A m (F^[n] x)‖ ≤
        ‖kernelProduct F A n x‖ * ‖kernelProduct F A m (F^[n] x)‖ := norm_mul_le _ _
    _ ≤ kernelEnvelope F A n * kernelEnvelope F A m :=
      mul_le_mul (kernelNorm_le_envelope F A b upper n x)
        (kernelNorm_le_envelope F A b upper m (F^[n] x)) (norm_nonneg _)
        (kernelEnvelope_positive F A c b hc lower upper n).le

theorem kernel_log_envelope_subadditive (F : X → X) (A : X → V) (c b : ℝ)
    (hc : 0 < c)
    (lower : ∀ n x, c ^ n ≤ ‖kernelProduct F A n x‖)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) :
    Subadditive (fun n => Real.log (kernelEnvelope F A n)) := by
  intro n m
  have hn := kernelEnvelope_positive F A c b hc lower upper n
  have hm := kernelEnvelope_positive F A c b hc lower upper m
  have hnm := kernelEnvelope_positive F A c b hc lower upper (n + m)
  have h := Real.log_le_log hnm (kernelEnvelope_submultiplicative F A c b hc lower upper n m)
  simpa [Real.log_mul hn.ne' hm.ne'] using h

theorem kernel_pressure_exists (F : X → X) (A : X → V) (c b : ℝ)
    (hc : 0 < c)
    (lower : ∀ n x, c ^ n ≤ ‖kernelProduct F A n x‖)
    (upper : ∀ n x, ‖kernelProduct F A n x‖ ≤ b ^ n) :
    ∃ P : ℝ, Tendsto (fun n => Real.log (kernelEnvelope F A n) / n) atTop (𝓝 P) := by
  have h := kernel_log_envelope_subadditive F A c b hc lower upper
  refine ⟨h.lim, h.tendsto_lim ?_⟩
  refine ⟨min 0 (Real.log c), ?_⟩
  rintro y ⟨n, rfl⟩
  by_cases hn : n = 0
  · simp only [hn, Nat.cast_zero, div_zero]
    exact min_le_left _ _
  · have hnR : (0 : ℝ) < n := by exact_mod_cast Nat.pos_of_ne_zero hn
    let x : X := Classical.choice inferInstance
    have hl := (lower n x).trans (kernelNorm_le_envelope F A b upper n x)
    have hlog := Real.log_le_log (pow_pos hc n) hl
    rw [Real.log_pow] at hlog
    have hd : Real.log c ≤ Real.log (kernelEnvelope F A n) / n :=
      (le_div_iff hnR).mpr (by nlinarith)
    exact (min_le_right _ _).trans hd

end CantorAudit
