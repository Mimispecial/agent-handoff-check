import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_receiver_handoff_review(default_account, secondary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_handoff_check.py")
    deployed = ok(factory.deploy_contract_tx(args=["Prepare the public release candidate", "Every handoff must identify finished work, concrete evidence, and unresolved work without claiming the receiver already completed it."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    owner = factory.build_contract(address, account=default_account)
    ok(owner.add_requirement(args=["TESTS", "Record the exact test suites and their observable results."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.add_requirement(args=["RELEASE", "State whether publication occurred and list every remaining release blocker."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.start_task(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.propose_handoff(args=[secondary_account.address, "The release candidate and changelog were prepared, and all local verification commands completed successfully.", "Evidence index: commit 8d31, test log showing 42 passes, and generated package checksum.", "Publication and final reviewer approval remain unresolved for the receiver."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(owner.review_pending_handoff(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = owner.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["phase"] == "AWAITING_RECEIVER"
    assert state["pending_readiness"] in ("READY", "NEEDS_WORK")
    observed = {"coverage_mask": state["pending_coverage_mask"], "readiness": state["pending_readiness"]}
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
