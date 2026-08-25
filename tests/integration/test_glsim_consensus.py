from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Review one proposed task-custody handoff"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"coverage_mask": "11", "readiness": "READY"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_receiver_accepted_handoff():
    owner_account, receiver_account = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_handoff_check.py")
    deployed = factory.deploy_contract_tx(args=["Prepare the public release candidate", "Every handoff must identify finished work, concrete evidence, and unresolved work without claiming the receiver already completed it."], account=owner_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    owner = factory.build_contract(address, account=owner_account)
    receiver = factory.build_contract(address, account=receiver_account)
    ok(owner.add_requirement(args=["TESTS", "Record the exact test suites and their observable results."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.add_requirement(args=["RELEASE", "State whether publication occurred and list every remaining release blocker."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.start_task(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.propose_handoff(args=[receiver_account.address, "The release candidate and changelog were prepared, and all local verification commands completed successfully.", "Evidence index: commit 8d31, test log showing 42 passes, and generated package checksum.", "Publication and final reviewer approval remain unresolved for the receiver."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.review_pending_handoff(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(receiver.accept_handoff(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.close_task(args=["The receiver completed publication and the owner recorded the final release outcome."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert owner.get_state(args=[]).call()["phase"] == "COMPLETE"
