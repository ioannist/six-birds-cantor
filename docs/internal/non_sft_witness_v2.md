# Non-SFT Witness Audit v2

## Question being tested
Does the closed delayed-return theorem branch yield a genuinely frontier local-domain witness, or is it still only a stronger finite-state renewal-like result?

## Closed theorem class
- `bounded_return_full_core_delayed_gate_subclass`

## Control setup being ruled out
For this audit, the excluded control setup is a stationary finite-state symbolic or finite-state renewal-like control model with finitely many continuation/return types sufficient to generate the induced cylinders and geometry relevant to the closed theorem.

The question is not only whether the class is non-SFT in the narrow symbolic sense. It is also whether it escapes finite-state renewal-like control in the theorem-relevant sense.

## Candidate families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- `frontier.fw_delayed_return_gate_a2`
- `contextual_local.prefix_memory_last_digit_rule`
- `contextual_local.prefix_memory_no_22_base3`
- `contextual_local.domain_gated_two_map_local_ifs`

## Selected witness or blocker
- Selected family: `frontier.fw_delayed_return_gate_a3`
- Decision: `finite_state_renewal_like_only`

## Reason the selected family is in-class
- It is one of the frozen witnesses for the closed theorem package.
- It satisfies the delayed-return assumptions and remains inside the closed full-core delayed-gate subclass.

## Reason it is or is not beyond finite-state renewal-like control
- It is not beyond finite-state renewal-like control on the evidence currently in the repo.
- The closed class is built from bounded return, a finite induced return alphabet on the supported witnesses, and a return-premeasure transfer that closes after narrowing to full-core control.
- That is enough for a theorem, but not enough to certify a genuinely new non-SFT local-domain phenomenon.

## Impact consequence
- The delayed-return branch is mathematically real and closed, but the current audit does not justify a non-SFT claim.
- The result is a stronger finite-state renewal-like theorem package, not yet the frontier witness the project ultimately wants.
