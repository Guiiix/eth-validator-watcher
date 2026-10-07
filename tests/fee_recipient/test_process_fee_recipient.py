import json
from pathlib import Path

from pytest import fixture

from eth_validator_watcher.fee_recipient import (
    process_fee_recipients,
    metric_wrong_fee_recipient_proposed_block_count,
)
from eth_validator_watcher.models import Block, ExecutionBlock, Validators, ExecutionTransactionTraces
from tests.fee_recipient import assets

Validator = Validators.DataItem.Validator


class Slack:
    def __init__(self):
        self.counter = 0

    def send_message(self, _: str) -> None:
        self.counter += 1


class Execution:
    def eth_get_block_by_hash(self, hash: str) -> ExecutionBlock:
        assert (
            hash == "0x9fc5b74ae5b8a0f7495314c7e6608e524c2ffe8581eca704208066cd922a1fee"
        )

        execution_block_path = Path(assets.__file__).parent / "execution_block.json"

        with execution_block_path.open() as file_descriptor:
            return ExecutionBlock(**json.load(file_descriptor))

    def eth_trace_transaction(self, hash: str):
        return None


class ExecutionEmptyBlock:
    def eth_get_block_by_hash(self, hash: str) -> ExecutionBlock:
        assert (
            hash == "0x9fc5b74ae5b8a0f7495314c7e6608e524c2ffe8581eca704208066cd922a1fee"
        )

        execution_block_path = (
            Path(assets.__file__).parent / "empty_execution_block.json"
        )

        with execution_block_path.open() as file_descriptor:
            return ExecutionBlock(**json.load(file_descriptor))

    def eth_trace_transaction(self, hash: str):
        return None


class ExecutionMEV:
    def eth_get_block_by_hash(self, hash: str) -> ExecutionBlock:
        assert (
            hash == "0x7f20d9f1dbd5d66371bcd0c5517ce75aaf2d436dc90b2a41f2472aef0e2584d9"
        )

        execution_block_path = (
            Path(assets.__file__).parent / "execution_block_0xa0226f5a.json"
        )

        with execution_block_path.open() as file_descriptor:
            return ExecutionBlock(**json.load(file_descriptor))

    def eth_trace_transaction(self, hash: str):
        assert (
            hash == "0xf71ddb5bf44774adfbc538e51a07811c6a6cd340a7bb761e06bf9bb4cfb97d91"
        )

        transaction_trace_path = (
                Path(assets.__file__).parent / "transaction_0xf71ddb5b.json"
        )

        with transaction_trace_path.open() as file_descriptor:
            return ExecutionTransactionTraces(**json.load(file_descriptor))


class ExecutionMEVPaidFromOtherAddress:
    """Builder pays the proposer from an address other than the block fee recipient."""

    def eth_get_block_by_hash(self, hash: str) -> ExecutionBlock:
        assert (
            hash == "0xa529a5146fd0fc6fec93687a8d227d71a86f9d0d0d885a8c2aee673b27f70db0"
        )

        execution_block_path = (
            Path(assets.__file__).parent / "execution_block_0xa529a514.json"
        )

        with execution_block_path.open() as file_descriptor:
            return ExecutionBlock(**json.load(file_descriptor))

    def eth_trace_transaction(self, hash: str):
        assert (
            hash == "0x96b8491a9496667a51836b7bcaf04bf63c25b010f3eb540d54a1662ff6acafc0"
        )

        transaction_trace_path = (
                Path(assets.__file__).parent / "transaction_0x96b8491a.json"
        )

        with transaction_trace_path.open() as file_descriptor:
            return ExecutionTransactionTraces(**json.load(file_descriptor))


@fixture
def block() -> Block:
    block_file = Path(assets.__file__).parent / "block.json"
    with block_file.open() as file_descriptor:
        return Block(**json.load(file_descriptor))

@fixture
def block_15055756() -> Block:
    block_file = Path(assets.__file__).parent / "block_15055756.json"
    with block_file.open() as file_descriptor:
        return Block(**json.load(file_descriptor))

@fixture
def block_15380539() -> Block:
    block_file = Path(assets.__file__).parent / "block_15380539.json"
    with block_file.open() as file_descriptor:
        return Block(**json.load(file_descriptor))


def test_execution_is_none():
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block="A block",  # type: ignore
        index_to_validator={},
        execution=None,
        expected_fee_recipients=["0x1234"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before

    assert slack.counter == 0


def test_fee_recipient_is_none():
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block="A block",  # type: ignore
        index_to_validator={},
        execution="execution",  # type: ignore
        expected_fee_recipients=None,
        slack=slack,  # type: ignore
    )

    assert slack.counter == 0


def test_not_our_validator(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={},
        execution="execution",  # type: ignore
        expected_fee_recipients=["0x1234"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before

    assert slack.counter == 0


def test_our_validator_allright(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution="execution",  # type: ignore
        expected_fee_recipients=["0xebec795c9c8bbd61ffc14a6662944748f299cacf"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before

    assert slack.counter == 0


def test_our_validator_ok_in_last_tx(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution=Execution(),  # type: ignore
        expected_fee_recipients=["0x760a6314a1d207377271917075f88e520141d55f"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before

    assert slack.counter == 0


def test_our_validator_not_ok_empty_block(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution=ExecutionEmptyBlock(),  # type: ignore
        expected_fee_recipients=["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before + 1

    assert slack.counter == 1


def test_our_validator_not_ok(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution=Execution(),  # type: ignore
        expected_fee_recipients=["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before + 1

    assert slack.counter == 1


def test_our_validator_allright_multiple_fee_recipients(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution="execution",  # type: ignore
        expected_fee_recipients=["0xabcdef1234", "0xebec795c9c8bbd61ffc14a6662944748f299cacf"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before

    assert slack.counter == 0


def test_our_validator_not_ok_multiple_fee_recipients(block: Block):
    slack = Slack()
    counter_before = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            365100: Validator(
                pubkey="0xabcd", effective_balance=32000000000, slashed=False
            )
        },
        execution=Execution(),  # type: ignore
        expected_fee_recipients=["0xabcdfe", "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
        slack=slack,  # type: ignore
    )

    counter_after = metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[0].value  # type: ignore
    assert counter_after == counter_before + 1

    assert slack.counter == 1

def test_our_validator_ok_with_mev_with_smart_contract(block_15055756: Block):
    block = block_15055756
    slack = Slack()
    counter_before = \
    metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[
        0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            915501: Validator(
                pubkey="0xa5ab9d", effective_balance=32000000000, slashed=False
            )
        },
        execution=ExecutionMEV(),  # type: ignore
        expected_fee_recipients=["0x4297cc867b85b63297c34af4268ced9cafc66f5a"],
        slack=slack,  # type: ignore
    )

    counter_after = \
    metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[
        0].value  # type: ignore

    assert counter_after == counter_before
    assert slack.counter == 0

def test_our_validator_ok_with_mev_with_smart_contract_paid_from_other_address(
    block_15380539: Block,
):
    block = block_15380539
    slack = Slack()
    counter_before = \
    metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[
        0].value  # type: ignore

    process_fee_recipients(
        block=block,
        index_to_validator={
            1565873: Validator(
                pubkey="0xa5ab9d", effective_balance=32000000000, slashed=False
            )
        },
        execution=ExecutionMEVPaidFromOtherAddress(),  # type: ignore
        expected_fee_recipients=["0x4297cc867b85b63297c34af4268ced9cafc66f5a"],
        slack=slack,  # type: ignore
    )

    counter_after = \
    metric_wrong_fee_recipient_proposed_block_count.collect()[0].samples[
        0].value  # type: ignore

    assert counter_after == counter_before
    assert slack.counter == 0
