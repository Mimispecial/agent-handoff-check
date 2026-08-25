from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "agent_handoff_check.py"
SDK = "v0.2.16"
PROMPT = "Review one proposed task-custody handoff"
RULES = "Every handoff must identify finished work, point to concrete evidence, and name unresolved work without claiming that the receiver already completed it."


def address(account):
    return "0x" + account.hex()


def configured(vm, direct_deploy, owner):
    vm.sender = owner
    contract = direct_deploy(str(CONTRACT), "Prepare the public release candidate", RULES, sdk_version=SDK)
    contract.add_requirement("tests", "Record the exact test suites and their observable results.")
    contract.add_requirement("release", "State whether publication occurred and list every remaining release blocker.")
    contract.start_task()
    return contract


def propose(contract, receiver):
    contract.propose_handoff(
        address(receiver),
        "The release candidate and changelog were prepared, and all local verification commands completed successfully.",
        "Evidence index: commit 8d31, test log showing 42 passes, and the generated package checksum.",
        "Publication and final reviewer approval remain unresolved for the receiver to complete.",
    )


def test_review_receiver_acceptance_and_owner_close(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = configured(direct_vm, direct_deploy, direct_alice)
    propose(contract, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "11", "readiness": "READY"}))
    contract.review_pending_handoff()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "10", "readiness": "NEEDS_WORK"}))
    assert direct_vm.run_validator(leader_result=leader) is False
    direct_vm.sender = direct_bob
    contract.accept_handoff()
    assert contract.get_handoff(1)["receiver"] == address(direct_bob).lower()
    direct_vm.sender = direct_alice
    contract.close_task("The receiver completed publication and the owner recorded the final release outcome.")
    assert contract.get_state()["phase"] == "COMPLETE"


def test_needs_work_cannot_transfer_and_receiver_can_reject(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = configured(direct_vm, direct_deploy, direct_alice)
    propose(contract, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "10", "readiness": "NEEDS_WORK"}))
    contract.review_pending_handoff()
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("handoff_needs_work"):
        contract.accept_handoff()
    contract.reject_handoff("The evidence index omits the publication checklist needed to continue safely.")
    state = contract.get_state()
    assert state["phase"] == "ACTIVE"
    assert state["accepted_handoffs"] == 0


def test_access_control_and_bad_model_mask_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = configured(direct_vm, direct_deploy, direct_alice)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_current_holder"):
        propose(contract, direct_alice)
    direct_vm.sender = direct_alice
    propose(contract, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "111", "readiness": "READY"}))
    with direct_vm.expect_revert("invalid_coverage_mask"):
        contract.review_pending_handoff()
    assert contract.get_state()["phase"] == "REVIEWING_HANDOFF"
