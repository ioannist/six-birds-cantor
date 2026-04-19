# Theorem Definitions v1

This is an internal definition pack for the theorem program. It fixes the object/assumption vocabulary used by `safe_finite_memory_local_subclass` and `quasi_multiplicative_local_cantor_class`.

## Geometric object

### Admissible words / branches
For a family with symbol set `A`, an admissible word of length `n` is a branch
`w = i_1 ... i_n`
such that every intermediate composition is allowed by the family's admissibility rule. In symbolic families this means word legality in the rule system. In local-IFS families this means every restricted image remains nonempty at each step.

### Cylinder images
For an admissible word `w = i_1 ... i_n`, the cylinder image is the stage-`n` image set produced by composing the branch maps on the allowed seed/domain. In the simplest similarity case this is one interval. In local systems it may be a restricted interval image determined by local domains.

### Upper pressure
For depth `n` and parameter `s`, the upper pressure uses raw admissible branches:
`P_n^U(s) = (1/n) log Z_n^U(s)`, where `Z_n^U(s)` sums branch contraction weights over admissible words.
This is the branch-count / branch-weight object.

### Lower pressure
For geometric families where stage-`n` interval unions are defined, the lower pressure uses packaged stage-`n` geometric pieces:
`P_n^L(s) = (1/n) log Z_n^L(s)`, where `Z_n^L(s)` sums `|I|^s` over packaged intervals `I`.
This is the geometric-union object. It is only part of the theorem program when the packaging rule is admissible as a geometric construction, not just a visualization convenience.

## Assumption vocabulary

### Uniform contraction
Every branch map contracts by a uniform factor strictly less than `1`.

### Finite memory bound
Admissibility is determined by a bounded finite amount of past information, or by an equivalent explicit finite control state.

### Fixed / stationary admissibility rule
The admissibility mechanism itself does not change with stage. A rule may depend on bounded memory and still be stationary. Pure stage-dependent schedules are not stationary.

### Bounded distortion
Cylinder diameters are comparable to their nominal contraction products up to a uniform multiplicative constant. In similarity examples this is effectively automatic.

### Usable separation
Cylinder images admit enough separation or overlap control that covering arguments and lower-pressure packaging are meaningful. This does not force disjointness, but it rules out uncontrolled overlap.

### Quasi-multiplicativity
There is a uniform constant `C >= 1` such that admissible branch weights satisfy a multiplicative comparison of the form
`C^{-1} phi(u) phi(v) <= phi(uv) <= C phi(u) phi(v)`
for concatenations that remain admissible, possibly after a bounded connecting correction.
This is the leading candidate hypothesis for a Bowen-formula theorem beyond the safe class.

### Tempered memory
The complexity of the memory/protocol layer grows slowly enough with depth that pressure objects still have a controlled asymptotic theory. This is a stretch-class hypothesis, not part of the primary class.

## Lens and packaging

### Role of lens
Lens is an observation choice: raw cylinders, coalesced intervals, prefix sectors, or similar coarse views. Lens is not part of the attractor definition in the primary theorem class. If lens feeds back into admissibility, the family is excluded from the primary class.

### Role of packaging
Packaging is how raw geometric pieces are grouped when building lower-pressure objects or reporting geometry. In the primary theorem class, packaging is allowed only if it is fixed and admissible as part of the lower-pressure construction. If packaging feeds back into admissibility, the family is excluded from the primary class.

### Lower-pressure packaging admissibility
A packaging rule is admissible for theorem use when it gives a stage-`n` geometric object that is consistent across depths and can be used in covering/mass estimates. Purely budget-driven or lens-driven packaging is observational/bookkeeping unless proved otherwise.

## Geometric object vs observation / bookkeeping layer

### Part of the geometric object
- branch maps and contraction data
- admissibility rule
- local domains if present
- cylinder images
- lower-pressure packaging only when fixed and theorem-admissible

### Part of the observation / bookkeeping layer
- lens choice
- audit/accounting summaries
- run manifests and diagnostics
- packaging used only for visualization or adaptive reporting

## Excluded from the primary theorem class
- nonautonomous stage schedules where admissibility changes with stage as a protocol control
- families where lens affects admissibility
- families where packaging affects admissibility
- feedback families with unstable or state-dependent admissibility not yet reduced to a fixed finite-control object
- any family whose inclusion depends on assumptions currently tagged `unknown`
