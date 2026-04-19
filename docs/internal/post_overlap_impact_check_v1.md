# Post-Overlap Impact Check v1

## Question
After the bounded-overlap patch and Bowen v2 enlargement, did the theorem become a bridge toward the local/non-SFT frontier, or is it still best understood as a stronger SFT-like theorem?

## What changed from Bowen v1 to v2
- Bowen v2 replaces the old disjoint-cylinder coincidence step with bounded-overlap coincidence.
- The proved class now includes `contextual_local.prefix_memory_last_digit_rule` in addition to the prior disjoint prefix-memory witness.
- The enlargement is real but still restricted to equal-scale finite-memory prefix-memory geometry.

## Newly included families
- contextual_local.prefix_memory_last_digit_rule

## Domain-gated local IFS audit
Answer: `not yet but promising`.

Reason: `contextual_local.domain_gated_two_map_local_ifs` is not obstructed by the bounded-overlap diagnostics and is marked `plausible_next` in the v2 report, but it still lies outside the proved class because the current overlap theoremlet depends on equal-scale cylinders and bounded overlap generated from finitely many stationary continuation types. The domain-gated local-IFS geometry has not yet been reduced to that setting.

## Non-SFT blocker audit
Status: `remains`.

Reason: the only newly included family is `contextual_local.prefix_memory_last_digit_rule`, which is still bounded-memory symbolic / finite-state in the paper-relevant sense. No genuinely local non-SFT family entered the proved class in Bowen v2.

## Decision
- Impact decision: `stronger_sft_like_theorem`

## Next consequence
The bounded-overlap patch is worth keeping because it strengthens the theorem honestly, but it does not by itself rescue the frontier claim. The next gate is whether to launch a dedicated non-SFT/local-domain expansion sprint aimed at bringing a genuinely local witness into the proved class.
