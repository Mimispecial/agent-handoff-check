# Agent Handoff Check

Records sequential task-custody handoffs and uses validator consensus to check whether every frozen requirement is accounted for before the named receiver decides whether to accept custody.

## Why it is an Intelligent Contract

Produce a fixed-order requirement coverage mask and a READY or NEEDS_WORK advisory for one pending handoff. GenLayer validators independently replay that semantic judgment before it becomes shared state. Requirement setup, holder authorization, receiver designation, acceptance or rejection, custody-chain history, and owner closure are deterministic.

## Reusable deployment model

Deploy once per task or operational workstream. The same reviewed source can be deployed again with a new title, operating rules, requirement set, and participants.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the task owner and initial holder. Only the current holder proposes a handoff; only the named receiver accepts or rejects it; only the owner closes the task.

State path: `CONFIGURING → ACTIVE → REVIEWING_HANDOFF → AWAITING_RECEIVER → ACTIVE (repeatable) → COMPLETE`

## Evidence boundary

The frozen task title, operating rules, ordered requirements, completed-work summary, evidence index, and unresolved-work statement stored in the deployment. References are treated as text indexes and are not opened.

## Core invariants

- Requirements freeze when the owner starts the task.
- Only the current holder can propose the next receiver, and the receiver must be a different valid address.
- Acceptance requires READY plus an all-ones coverage mask; AI cannot transfer custody.
- The owner cannot close a task until at least one receiver has accepted a handoff.

## Public interface

Write methods: `accept_handoff, add_requirement, close_task, propose_handoff, reject_handoff, review_pending_handoff, start_task`

View methods: `get_handoff, get_policy, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/agent_handoff_check.py
genvm-lint typecheck contracts/agent_handoff_check.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0x65ae055A23F6B5700dec473c1D36CD61509acC89
- Studio import: https://studio.genlayer.com/?import-contract=0x65ae055A23F6B5700dec473c1D36CD61509acC89
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0x5637d6a2671029662aadfda7522ec663e4c777c30882c3775d943e3912455428
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x817eab4ede8f6760eeede4b7bf6db03facaf0b863fb496fd8b33a1131fb94eff
- Observed committed state: `{"coverage_mask":"01","readiness":"NEEDS_WORK"}`
- Audited source SHA-256: `6fda3786bdfff22039a19f15d3b7ee2c3a5b6d04f21ac37fa603190cf2b7af51`

## Limitations

- The contract does not authenticate referenced artifacts or prove that described work happened.
- Readiness means the stored packet is sufficient to continue, not that the task is complete or correct.
- A receiver who does not respond can leave the deployment awaiting acceptance.

## Repository map

- `contracts/agent_handoff_check.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
