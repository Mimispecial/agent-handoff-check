# Security

## Scope

This repository contains one bounded Intelligent Contract, direct tests, a five-validator GLSim test, and an opt-in StudioNet smoke test. It has no frontend, backend, database, token, payout, proxy upgrade, or repository secret.

## Trust model

Untrusted evidence is delimited as data, model outputs use closed schemas, and validator replay must agree before semantic state is stored.

The deployer is the task owner and initial holder. Only the current holder proposes a handoff; only the named receiver accepts or rejects it; only the owner closes the task.

## Implemented controls

- Concrete immutable GenVM runner hash; no floating runner dependency.
- Address normalization, explicit role separation, collection caps, one-time actions, and lifecycle locks.
- Bounded text plus strict `[EXPECTED]` and `[LLM_ERROR]` failure classes.
- Sorted, delimited evidence packets and independent validator replay.
- Storage is copied before nondeterministic callbacks; static audit requires zero callback reads from `self`.
- No cross-contract calls, fund custody, transfer, automated purchase, external deletion, or webhook.
- `.env`, caches, artifacts, wallet files, and local secrets are ignored. Live wallets are encrypted outside the workspace.

## Contract-specific safety properties

- Requirements freeze when the owner starts the task.
- Only the current holder can propose the next receiver, and the receiver must be a different valid address.
- Acceptance requires READY plus an all-ones coverage mask; AI cannot transfer custody.
- The owner cannot close a task until at least one receiver has accepted a handoff.

## Residual risks

- The contract does not authenticate referenced artifacts or prove that described work happened.
- Readiness means the stored packet is sufficient to continue, not that the task is complete or correct.
- A receiver who does not respond can leave the deployment awaiting acceptance.

Do not use this contract to make legal, medical, financial, employment, admission, credit, or physical-safety decisions beyond the explicit low-risk policy in its source. A new use case requires a fresh deployment and independent domain review.

## Reporting

Report vulnerabilities privately to the repository owner with the contract name, affected method, reproduction, expected invariant, and impact. Never include private keys, wallet passwords, or personal data.
