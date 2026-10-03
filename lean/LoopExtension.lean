import HistoryConditioning

/-! Moving-history extension bridge. Equal weighted ROW moments followed by
one shared rank-one step give identical ordered products from horizon two
onward. This is stronger than a frozen transpose-pressure comparison.
The concrete original 20-state construction and its source-selector bridge
are checked separately; original infinite-shell membership is not assumed
to have been supplied by these matrix lemmas. -/
namespace CantorAudit
noncomputable section
attribute [local instance] Matrix.linftyOpNormedRing Matrix.linfty_opNormOneClass
variable {d : ℕ} [NeZero d]

def rankOneRows (r : Fin d → ℝ) : Matrix (Fin d) (Fin d) ℝ := fun _ j => r j

theorem equal_rows_mul_rankOne (A B : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ) :
    A * rankOneRows r = B * rankOneRows r := by
  ext i j
  simp only [Matrix.mul_apply, rankOneRows, ← Finset.sum_mul, rows]

theorem equal_rows_norm (A B : Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ i j, 0 ≤ A i j) (hB : ∀ i j, 0 ≤ B i j)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) : ‖A‖ = ‖B‖ := by
  apply le_antisymm
  · exact positiveMatrix_norm_le A hA ‖B‖ (norm_nonneg _)
      (fun i => (rows i).le.trans (positiveMatrix_row_le_norm B hB i))
  · exact positiveMatrix_norm_le B hB ‖A‖ (norm_nonneg _)
      (fun i => (rows i).ge.trans (positiveMatrix_row_le_norm A hA i))

/-- Only the columns on which the first matrices differ need common rows
in the second matrix. This preserves the moving-history split with much
smaller ORIGINAL legal noise and an unsaturated initial budget. -/
theorem supported_difference_mul_common_rows (A B R : Matrix (Fin d) (Fin d) ℝ)
    (S : Set (Fin d)) (r : Fin d → ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j)
    (outside : ∀ i k, k ∉ S → A i k = B i k)
    (common : ∀ k, k ∈ S → ∀ j, R k j = r j) : A*R = B*R := by
  classical
  ext i j
  have h : (∑ k, (A i k-B i k)*R k j) = (∑ k, (A i k-B i k))*r j := by
    rw [Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro k _
    by_cases hk : k ∈ S
    · rw [common k hk j]
    · rw [outside i k hk,sub_self,zero_mul,zero_mul]
  have sum : (∑ k, (A i k-B i k)) = 0 := by
    rw [Finset.sum_sub_distrib,rows i,sub_self]
  apply sub_eq_zero.mp
  simp only [Matrix.mul_apply,← Finset.sum_sub_distrib,← sub_mul]
  rw [h,sum,zero_mul]

def matchedHistory (A R : Matrix (Fin d) (Fin d) ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) : ℕ → Matrix (Fin d) (Fin d) ℝ
  | 0 => 1
  | 1 => A
  | n+2 => A*R*tail n

theorem matchedHistory_equal_from_two (A B R : Matrix (Fin d) (Fin d) ℝ)
    (match_two : A*R = B*R) (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    matchedHistory A R tail (n+2) = matchedHistory B R tail (n+2) := by
  simp only [matchedHistory,match_two]

theorem matchedHistory_norms_equal (A B R : Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ i j, 0 ≤ A i j) (hB : ∀ i j, 0 ≤ B i j)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (match_two : A*R = B*R)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    ‖matchedHistory A R tail n‖ = ‖matchedHistory B R tail n‖ := by
  rcases n with _ | _ | n
  · rfl
  · exact equal_rows_norm A B hA hB rows
  · rw [matchedHistory_equal_from_two A B R match_two tail n]

theorem matchedHistory_partitions_equal (A B R : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (match_two : A*R = B*R)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (p : Fin d → ℝ) :
    rowHistoryPartition (matchedHistory A R tail n) p =
      rowHistoryPartition (matchedHistory B R tail n) p := by
  rcases n with _ | _ | n
  · rfl
  · simp only [rowHistoryPartition,matchedHistory,rows]
  · rw [matchedHistory_equal_from_two A B R match_two tail n]

/-- `tail n` is the common ordered future product after the shared rank-one
second step. It can be nonautonomous and need not itself be rank one. -/
def joinedHistory (A : Matrix (Fin d) (Fin d) ℝ) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) : ℕ → Matrix (Fin d) (Fin d) ℝ
  | 0 => 1
  | 1 => A
  | n+2 => A * rankOneRows r * tail n

theorem joinedHistory_equal_from_two (A B : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    joinedHistory A r tail (n+2) = joinedHistory B r tail (n+2) := by
  simp only [joinedHistory, equal_rows_mul_rankOne A B rows r]

theorem joinedHistory_rows_equal (A B : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (i : Fin d) :
    ∑ j, joinedHistory A r tail n i j = ∑ j, joinedHistory B r tail n i j := by
  rcases n with _ | _ | n
  · rfl
  · exact rows i
  · rw [joinedHistory_equal_from_two A B rows r tail n]

theorem joinedHistory_norms_equal (A B : Matrix (Fin d) (Fin d) ℝ)
    (hA : ∀ i j, 0 ≤ A i j) (hB : ∀ i j, 0 ≤ B i j)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) :
    ‖joinedHistory A r tail n‖ = ‖joinedHistory B r tail n‖ := by
  rcases n with _ | _ | n
  · rfl
  · exact equal_rows_norm A B hA hB rows
  · rw [joinedHistory_equal_from_two A B rows r tail n]

/-- Conditioning which hybrid starting world was used, with a common
initial microstate law, can preserve every finite partition despite distinct
packaged objects. It is not only the old initial-microstate conditioning. -/
theorem joinedHistory_partitions_equal (A B : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (p : Fin d → ℝ) :
    rowHistoryPartition (joinedHistory A r tail n) p =
      rowHistoryPartition (joinedHistory B r tail n) p := by
  simp only [rowHistoryPartition, joinedHistory_rows_equal A B rows r tail n]

/-- A genuine two-world finite disintegration has zero partition defect on
this construction. Pressure existence is a separate obligation. -/
theorem joinedHistory_disintegration_equal (A B : Matrix (Fin d) (Fin d) ℝ)
    (rows : ∀ i, ∑ j, A i j = ∑ j, B i j) (r : Fin d → ℝ)
    (tail : ℕ → Matrix (Fin d) (Fin d) ℝ) (n : ℕ) (p : Fin d → ℝ) (w : ℝ) :
    w * rowHistoryPartition (joinedHistory A r tail n) p +
      (1-w) * rowHistoryPartition (joinedHistory B r tail n) p =
      rowHistoryPartition (joinedHistory A r tail n) p := by
  rw [← joinedHistory_partitions_equal A B rows r tail n p]
  ring

end
end CantorAudit
