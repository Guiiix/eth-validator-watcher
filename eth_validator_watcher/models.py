"""Contains the models for the validator watcher."""

from enum import StrEnum

from pydantic import BaseModel


class Validators(BaseModel):
    class DataItem(BaseModel):
        class StatusEnum(StrEnum):
            pendingInitialized = "pending_initialized"
            pendingQueued = "pending_queued"
            activeOngoing = "active_ongoing"
            activeExiting = "active_exiting"
            activeSlashed = "active_slashed"
            exitedUnslashed = "exited_unslashed"
            exitedSlashed = "exited_slashed"
            withdrawalPossible = "withdrawal_possible"
            withdrawalDone = "withdrawal_done"

        class Validator(BaseModel):
            pubkey: str
            effective_balance: int
            slashed: bool

        index: int
        status: StatusEnum

        validator: Validator

    data: list[DataItem]


class Genesis(BaseModel):
    class Data(BaseModel):
        genesis_time: int

    data: Data


class Header(BaseModel):
    class Data(BaseModel):
        class Header(BaseModel):
            class Message(BaseModel):
                slot: int

            message: Message

        header: Header

    data: Data


class Block(BaseModel):
    class Data(BaseModel):
        class Message(BaseModel):
            class Body(BaseModel):
                class Attestation(BaseModel):
                    class Data(BaseModel):
                        slot: int
                        index: int

                    aggregation_bits: str
                    data: Data

                class ExecutionPayload(BaseModel):
                    fee_recipient: str
                    block_hash: str

                attestations: list[Attestation]
                execution_payload: ExecutionPayload

            slot: int
            proposer_index: int
            body: Body

        message: Message

    data: Data


class Committees(BaseModel):
    class Data(BaseModel):
        index: int
        slot: int
        validators: list[int]

    data: list[Data]


class ProposerDuties(BaseModel):
    class Data(BaseModel):
        pubkey: str
        validator_index: int
        slot: int

    dependent_root: str
    data: list[Data]


class ValidatorsLivenessRequestLighthouse(BaseModel):
    indices: list[int]
    epoch: int


class ValidatorsLivenessRequestTeku(BaseModel):
    indices: list[int]


class ValidatorsLivenessResponse(BaseModel):
    class Data(BaseModel):
        index: int
        is_live: bool

    data: list[Data]


class SlotWithStatus(BaseModel):
    number: int
    missed: bool


class CoinbaseTrade(BaseModel):
    time: str
    trade_id: int
    price: float
    size: float
    side: str


class BeaconType(StrEnum):
    LIGHTHOUSE = "lighthouse"
    NIMBUS = "nimbus"
    OLD_PRYSM = "old-prysm"
    OLD_TEKU = "old-teku"
    OTHER = "other"


class BlockIdentierType(StrEnum):
    HEAD = "head"
    GENESIS = "genesis"
    FINALIZED = "finalized"


class EthGetBlockByHashRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str = "eth_getBlockByHash"
    params: list
    id: str = "1"


class ExecutionBlock(BaseModel):
    class Result(BaseModel):
        class Transaction(BaseModel):
            to: str | None

        transactions: list[Transaction]

    jsonrpc: str
    id: int
    result: Result


class Rewards(BaseModel):
    class Data(BaseModel):
        class IdealReward(BaseModel):
            effective_balance: int
            source: int
            target: int
            head: int

        class TotalReward(BaseModel):
            validator_index: int
            source: int
            target: int
            head: int

        ideal_rewards: list[IdealReward]
        total_rewards: list[TotalReward]

    data: Data


class BlockReward(BaseModel):
    class Data(BaseModel):
        proposer_index: int
        total: int

    data: Data


class SyncCommitteeReward(BaseModel):
    class Data(BaseModel):
        validator_index: int
        reward: int

    data: list[Data]


class ProposerPayloadDelivered(BaseModel):
    slot: int
    value: int
    proposer_pubkey: str


class RelayBuilderValidator(BaseModel):
    class Entry(BaseModel):
        class Message(BaseModel):
            pubkey: str

        message: Message

    slot: int
    validator_index: int
    entry: Entry


class SyncCommittee(BaseModel):
    class Data(BaseModel):
        validators: list[int]

    data: Data
