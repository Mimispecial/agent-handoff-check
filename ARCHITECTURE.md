# Architecture

## Deployment boundary

Deploy once per task or operational workstream. The same reviewed source can be deployed again with a new title, operating rules, requirement set, and participants.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the task owner and initial holder. Only the current holder proposes a handoff; only the named receiver accepts or rejects it; only the owner closes the task.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`CONFIGURING → ACTIVE → REVIEWING_HANDOFF → AWAITING_RECEIVER → ACTIVE (repeatable) → COMPLETE`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The frozen task title, operating rules, ordered requirements, completed-work summary, evidence index, and unresolved-work statement stored in the deployment. References are treated as text indexes and are not opened.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Produce a fixed-order requirement coverage mask and a READY or NEEDS_WORK advisory for one pending handoff.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Requirement setup, holder authorization, receiver designation, acceptance or rejection, custody-chain history, and owner closure are deterministic.

Important invariants:

- Requirements freeze when the owner starts the task.
- Only the current holder can propose the next receiver, and the receiver must be a different valid address.
- Acceptance requires READY plus an all-ones coverage mask; AI cannot transfer custody.
- The owner cannot close a task until at least one receiver has accepted a handoff.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
