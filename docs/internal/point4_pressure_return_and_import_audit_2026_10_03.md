# Point 4: exact finite pressure return and imported-theorem audit

The fourth original theorem's four premises do not imply its conclusion.
The newer Six Birds results examined below do not supply the missing pressure
separation. They do support the surviving structural result. The paper has
not been edited, and this audit does not adopt a replacement for its claims.

## The valid finite-family statement

Fix ONE probability law, ONE path potential and ONE finite nonempty family
of positively charged object fibers. Write their fixed probabilities as
w_i>0 with sum w_i=1, and let Z_i,n>0 be the actual normalized conditional
partition integrals. Total expectation gives the global partition

`Z_n = sum_i w_i Z_i,n`.

Assume each logarithmic growth limit P_i=lim_n log(Z_i,n)/n exists. Then

`P_reference = lim_n log(Z_n)/n = max_i P_i = M`,

`Delta = M - sum_i w_i P_i = sum_i w_i (M-P_i) >= 0`.

Consequently Delta=0 iff every P_i equals M, and Delta>0 iff some pair of
conditional pressures differs. For every index j,

`Delta >= w_j (M-P_j)`.

The result needs fixed probabilities and a fixed finite family. It is not a
claim about a countably infinite family, horizon-dependent empirical weights,
or a growing family of strata. Zero-probability objects must be excluded from
the charged index set. Structural inequality of object values is insufficient.

For completeness, the pressure proof has two independent inequalities. A
maximizing index j gives Z_n>=w_j Z_j,n, whose logarithmic rate is M. For every
epsilon>0, all conditional rates are eventually at most M+epsilon. Finiteness
permits one common horizon, giving Z_n<=exp(n(M+epsilon)). These bounds prove
the limit. The gap criterion follows from a finite sum of nonnegative terms
with strictly positive weights. This is a substantive derivation rather than
an assignment of pressure values to object labels.

All six statements above are mechanized in
[`FiniteDisintegration.lean`](../../lean/FiniteDisintegration.lean). The actual
conditional integrals, pressure existence and family recognition are supplied
inputs. In particular, `P_reference=P_S` for the supremum over all shell states
requires a separate return theorem; it does not follow from total expectation.
The earlier [all-word construction](all_word_pressure_disintegration_2026_10_03.md)
provides that return for its explicitly constructed two-fiber law.

## Imported endpoints and their exact scope

The source paths, theorem anchors and content hashes are recorded in
[`point4_import_audit_2026_10_03.json`](point4_import_audit_2026_10_03.json).
The corresponding theorem statements and proofs were read, rather than
inferring their strength from titles or theorem names. This is an audit of
the listed candidate routes, not a claim to have exhausted every corpus paper.

* **Foundations III, Theorems 12 and 13:** strict nonfactorization is equivalent
  to an actual split pair for the declared object maps. Neither theorem
  contains a probability law, pressure functional or pressure inequality.
  Its refinement definition expressly excludes automatic improvement of a
  closure deficit. The result returns structural strictness, not scalar
  pressure separation.
* **Foundations IV, F8:** strict extension requires retention of the old
  quotient and a split old fiber. For a hybrid object `(pi_0,Gamma)`, retention
  is the first projection. The same pair witnessing distinct current Gamma
  in the common-input construction therefore satisfies this stronger
  retentive definition as well. F8 has no thermodynamic conclusion.
* **Foundations IV, F39:** the optional identification of unresolved targets
  with nonzero mixing explicitly assumes that mixing vanishes exactly when
  the refined and original quotients have the same fibers. The finite
  conditional-Shannon-entropy instance establishes this property for its own
  fiber-volume functional. It does not establish it for logarithmic path
  pressure or for Delta. Taking pressure as that functional would require
  precisely the faithful-separation bridge contradicted by the common-input
  example. A strictly positive entropy of the current package can coexist
  with an identically zero pressure gap.
* **Foundations III, Theorem 8, and To Cast a Stone, the exact decomposition,
  expected-KL and zero-deficit propositions:** these concern a specified finite
  stochastic host, distribution, time lag, abstraction and predictive KL
  loss. The equality is with conditional mutual information. The converse
  from vanishing deficit to structural closure needs full microstate support;
  the minimum-loss result also requires that the admissible macro kernels
  contain the true conditional kernel. Neither result identifies this
  prediction loss with the pressure gap.
* **Foundations VIII, Q9a--Q9c:** block-row compatibility characterizes
  lumpability; support-relative closure is equivalent to vanishing conditional
  mutual information, and full state support permits the structural converse.
  Q9b explicitly allows one-step distinctions to disappear at every later
  lag. These statements do not rule out common long-time pressure. The local
  original warm join likewise removes future history-matrix distinctions
  after two factors, while the actual initial completion objects still differ.

The distinction is mathematically consequential: a finite-horizon predictive
or entropy distinction can contribute only a fixed multiplicative factor to
Z_n, which disappears in log(Z_n)/n. No imported result audited here proves a
positive asymptotic rate for the original pressure observable merely because
the object map does not factor. Supplying an extra recognition record for
strictness cannot fill this missing quantitative input.

## What the existing constructions settle

There are two lawful reference laws on the same original-parameter controlled
twenty-state shell, with the same current completion map and path potential:

1. The constructed correlated law has distinct conditional pressures, returns
   the full-shell pressure and has a certified positive gap at both historical
   positive parameter grids and their stated neighborhoods.
2. The constructed common-input law gives both actual, distinct completion
   objects the same future reference law. Its conditional pressures all equal
   the full-shell pressure, so its genuine gap is identically zero. Its finite
   conditional partition values can nevertheless differ.

These laws are parameter-independent probability constructions. Neither is
an identification with the original independent raw-innovation experiment.
Their comparison shows that the structural premises and pressure
well-posedness alone leave the answer undetermined. See the
[common-input derivation](common_input_disintegration_obstruction_2026_10_03.md)
for the exact source and mechanization boundaries.

Separately, all twelve recorded fixed-kernel sixteen-/twenty-state completion
panels have a unique exact completion fixed vector, hence one exact fiber
with weight 1 in each panel. Rounded transient signatures are not multiple
exact strata. This is a statement about those recorded real-normalized input
tables, not a proof of singleton families throughout an unspecified invariant
shell, or of the entire pre/post-refinement family F(x).

## Repair boundary and self-review

The positive result survives as an explicit existence/instance theorem, with
the reference law and independently established pressure separation specified.
The general finite-family return survives with the exact separation criterion
above. The original assertion that structural strictness entails a positive
pressure gap does not survive as an implication from its four listed premises.
Its claimed uniform empirical multi-fiber support also does not survive the
exact recorded-panel audit. A material change of premises or conclusion is
needed to state point 4 correctly; adding more mechanization cannot prove the
invalid implication.

This is a self-review, not independent review. The new Lean return allows any
finite family and arbitrary positive fixed probabilities; it assumes neither
object nonfactorization nor separation. Its conclusions agree with both the
positive and zero-gap instances. A singleton has zero gap. A zero gap tests
equality of conditional exponential growth rates, and by itself does not
certify predictive sufficiency for the entire packaged future. No claim is
made that the controlled shell is the originally undefined seeded shell, or
that the cross-state current-object fibers have been identified with every
literal F(x) used in the paper. The user has not selected a replacement claim.

Validation: the complete `lake build` succeeds. A fresh
`lake env lean AxiomAudit.lean` checks all 196 exported declarations, including
the six new finite-family results; their only transitive axioms are the
standard `propext`, `Classical.choice` and `Quot.sound`, with no proof holes or
custom axioms. Both existing positive and zero-gap receipt input hashes, all
new corpus source hashes and all recorded theorem anchors match their current
files. No Python mathematics or experiment code changed in this increment.
