# arXiv Submission Notes --- Cantor

Copy/paste-ready metadata for the arXiv upload form.

---

## Title

Strict Theory Extension on a Lawful Continuous Cantor Shell

## Abstract

We study a twenty-state stochastic substrate in which six coupled mechanisms (operator rewrite, admissibility gating, timescale adaptation, lens selection, packaging, and a budget ledger) rewrite a Markov kernel at every step. We describe it at two levels: a growth theory, which records how selector-weighted products of the evolving kernels grow, and a completion theory, which records the unique fixed point of an evolve-forget-reinstate map built from the current kernel and lens. We prove four results. First, the unmodified update law admits a nonempty forward-invariant controlled shell. Its admissible futures are indexed by a Cantor space of kernel parameters, and each of the six mechanisms changes the dynamics somewhere on it. Second, on this shell the multiplicative growth pressure exists for every parameter s >= 0, is Lipschitz and strictly decreasing, equals log 20 at s = 0, and has a unique zero in (1/3, 1). Third, two explicit shell states agree on every specified growth observation (every horizon, every parameter, both selector observables) and yet have different completion objects, so the completion theory is a strict extension of the growth theory. Fourth, the same pair shows that growth is blind to this extra structure: from the second step on, the two states have identical history matrices. Hence strict extension does not force a conditional pressure gap. On the same shell, one admissible reference law gives an identically zero gap, while another gives a certified positive gap. Lean 4 checks the twenty-state witness, the matrix identities and the abstract pressure lemmas. The all-time shell inequalities are certified by exact rational interval arithmetic. The correspondence with the implemented update formulas and the construction of the reference laws are analytic.

## Keywords

- Cantor dynamics
- Products of nonnegative matrices
- Matrix pressure
- Thermodynamic formalism
- Theory extension
- Non-factorization
- Formal verification
- Six Birds Theory

## Author

- **Ioannis Tsiokos**
  - Affiliation: Automorph Inc., Wilmington, DE, USA
  - Email: ioannis@automorph.io
  - ORCID: 0009-0009-7659-5964

## Suggested arXiv categories

**Primary:**
- `math.DS` --- Dynamical Systems

**Cross-list:**
- `math-ph` --- Mathematical Physics

**MSC 2020 classes:**
- 37D35 (Thermodynamic formalism)
- 37A35 (Entropy and other invariants)
- 37H15 (Random dynamical systems: multiplicative ergodic theory, Lyapunov exponents)
- 28A80 (Fractals)
- 60J10 (Markov chains, discrete time)

## Version

- **v3** --- the title page lists v1 (31 March 2026), v2 (19 April 2026) and v3 (3 October 2026). Appendix B records the version history. The first-page footer carries the Zenodo v3 DOI 10.5281/zenodo.23126110 (concept record 19189352; v1 DOI 10.5281/zenodo.19189353).
- arXiv comments field suggestion: "v3: substantive mathematical revision; 28 pages, 4 figures; Lean 4 and exact-arithmetic certificates at https://github.com/ioannist/six-birds-cantor"

## Links

- **GitHub repository:** https://github.com/ioannist/six-birds-cantor
- **SBT Foundations reference:** https://doi.org/10.5281/zenodo.18365949

## License

**Recommended: CC BY 4.0** (matches the license stated in the paper footer).

## Submission package

| Item | Path |
|---|---|
| Source zip (arXiv upload) | `paper/build/arxiv_source_upload.zip` |
| Staging tree | `paper/build/arxiv_source_staging/` |
| Manifest (sha256) | `paper/submission/arxiv_source_manifest.txt` |
| Highlights (<= 5 lines, <= 85 chars each) | `paper/submission/highlights.txt` |
| Keywords | `paper/submission/keywords.txt` |
| AI disclosure | `paper/submission/ai_disclosure.txt` |
| Dry-run checklist | `paper/submission/checklist.md` |
| Compiled PDF (reference) | `paper/build/main.pdf` |

## Rebuild command

```bash
cd paper && latexmk -pdf -g -interaction=nonstopmode -halt-on-error main.tex
bash scripts/package_arxiv.sh
```
