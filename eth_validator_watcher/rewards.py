"""Contains functions to handle rewards calculation"""

import random
from typing import Tuple

from prometheus_client import Counter, Gauge

from eth_validator_watcher.utils import LimitedDict

from .beacon import Beacon
from .models import BeaconType, Validators

Validator = Validators.DataItem.Validator

Reward = Tuple[int, int, int]  # source, target, head
AreIdeal = Tuple[bool, bool, bool]  # source, target, head

# Network validators
# ------------------
(
    metric_net_suboptimal_sources_rate_gauge,
    metric_net_suboptimal_targets_rate_gauge,
    metric_net_suboptimal_heads_rate_gauge,
) = (
    Gauge("net_suboptimal_sources_rate", "Network suboptimal sources rate"),
    Gauge("net_suboptimal_targets_rate", "Network suboptimal targets rate"),
    Gauge("net_suboptimal_heads_rate", "Network suboptimal heads rate"),
)

(
    metric_net_ideal_sources_count,
    metric_net_ideal_targets_count,
    metric_net_ideal_heads_count,
) = (
    Counter("net_ideal_sources_count", "Network ideal sources count"),
    Counter("net_ideal_targets_count", "Network ideal targets count"),
    Counter("net_ideal_heads_count", "Network ideal heads count"),
)

(
    metric_net_actual_pos_sources_count,
    metric_net_actual_neg_sources_count,
    metric_net_actual_pos_targets_count,
    metric_net_actual_neg_targets_count,
    metric_net_actual_heads_count,
) = (
    Counter("net_actual_pos_sources_count", "Network actual positive sources count"),
    Counter("net_actual_neg_sources_count", "Network actual negative sources count"),
    Counter("net_actual_pos_targets_count", "Network actual positive targets count"),
    Counter("net_actual_neg_targets_count", "Network actual negative targets count"),
    Counter("net_actual_heads_count", "Network actual heads count"),
)

# Our validators
# --------------
(
    metric_our_suboptimal_sources_rate_gauge,
    metric_our_suboptimal_targets_rate_gauge,
    metric_our_suboptimal_heads_rate_gauge,
) = (
    Gauge("our_suboptimal_sources_rate", "Our suboptimal sources rate"),
    Gauge("our_suboptimal_targets_rate", "Our suboptimal targets rate"),
    Gauge("our_suboptimal_heads_rate", "Our suboptimal heads rate"),
)

(
    metric_our_ideal_sources_count,
    metric_our_ideal_targets_count,
    metric_our_ideal_heads_count,
) = (
    Counter("our_ideal_sources_count", "Our ideal sources count"),
    Counter("our_ideal_targets_count", "Our ideal targets count"),
    Counter("our_ideal_heads_count", "Our ideal heads count"),
)

(
    metric_our_actual_pos_sources_count,
    metric_our_actual_neg_sources_count,
    metric_our_actual_pos_targets_count,
    metric_our_actual_neg_targets_count,
    metric_our_actual_heads_count,
) = (
    Counter("our_actual_pos_sources_count", "Our actual positive sources count"),
    Counter("our_actual_neg_sources_count", "Our actual negative sources count"),
    Counter("our_actual_pos_targets_count", "Our actual positive targets count"),
    Counter("our_actual_neg_targets_count", "Our actual negative targets count"),
    Counter("our_actual_heads_count", "Our actual heads count"),
)

(
    our_ideal_sources_per_validator_count,
    our_ideal_targets_per_validator_count,
    our_ideal_heads_per_validator_count,
    our_actual_pos_sources_per_validator_count,
    our_actual_neg_sources_per_validator_count,
    our_actual_pos_targets_per_validator_count,
    our_actual_neg_targets_per_validator_count,
    our_actual_heads_per_validator_count,

    our_ideal_attestations_reward_per_validator_count,
    our_actual_pos_attestations_reward_per_validator_count,
    our_actual_neg_attestations_reward_per_validator_count,
) = (
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
)


def init_rewards_per_validator_counters(our_labels: dict[str, dict[str, str]]) -> None:
    global our_ideal_sources_per_validator_count
    global our_ideal_targets_per_validator_count
    global our_ideal_heads_per_validator_count
    global our_actual_pos_sources_per_validator_count
    global our_actual_neg_sources_per_validator_count
    global our_actual_pos_targets_per_validator_count
    global our_actual_neg_targets_per_validator_count
    global our_actual_heads_per_validator_count
    global our_ideal_attestations_reward_per_validator_count
    global our_actual_pos_attestations_reward_per_validator_count
    global our_actual_neg_attestations_reward_per_validator_count

    if len(our_labels) == 0 or our_ideal_targets_per_validator_count is not None:
        return

    labels = list(random.choice(list(our_labels.values())).keys())
    our_ideal_sources_per_validator_count = Counter("our_ideal_sources_per_validator_count",
                                                    "Our ideal sources count per validator",
                                                    labels)
    our_ideal_targets_per_validator_count = Counter("our_ideal_targets_per_validator_count",
                                                    "Our ideal targets count per validator",
                                                    labels)
    our_ideal_heads_per_validator_count = Counter("our_ideal_heads_per_validator_count",
                                                  "Our ideal heads count per validator",
                                                  labels)
    our_actual_pos_sources_per_validator_count = Counter("our_actual_pos_sources_per_validator_count",
                                                         "Our actual positive sources count per validator",
                                                         labels)
    our_actual_neg_sources_per_validator_count = Counter("our_actual_neg_sources_per_validator_count",
                                                         "Our actual negative sources count per validator",
                                                         labels)
    our_actual_pos_targets_per_validator_count = Counter("our_actual_pos_targets_per_validator_count",
                                                         "Our actual positive targets count per validator",
                                                         labels)
    our_actual_neg_targets_per_validator_count = Counter("our_actual_neg_targets_per_validator_count",
                                                         "Our actual negative targets count per validator",
                                                         labels)
    our_actual_heads_per_validator_count = Counter("our_actual_heads_per_validator_count",
                                                   "Our actual heads count per validator",
                                                   labels)
    our_ideal_attestations_reward_per_validator_count = Counter("our_ideal_attestations_reward_per_validator_count",
                                                                "Our ideal attestations per validator",
                                                                labels)
    our_actual_pos_attestations_reward_per_validator_count = Counter(
        "our_actual_pos_attestations_reward_per_validator_count",
        "Our actual positive attestations per validator",
        labels)
    our_actual_neg_attestations_reward_per_validator_count = Counter(
        "our_actual_neg_attestations_reward_per_validator_count",
        "Our actual negative attestations per validator",
        labels)
    for labels_dict in our_labels.values():
        our_ideal_sources_per_validator_count.labels(**labels_dict)
        our_ideal_targets_per_validator_count.labels(**labels_dict)
        our_ideal_heads_per_validator_count.labels(**labels_dict)
        our_actual_pos_sources_per_validator_count.labels(**labels_dict)
        our_actual_neg_sources_per_validator_count.labels(**labels_dict)
        our_actual_pos_targets_per_validator_count.labels(**labels_dict)
        our_actual_neg_targets_per_validator_count.labels(**labels_dict)
        our_actual_heads_per_validator_count.labels(**labels_dict)
        our_ideal_attestations_reward_per_validator_count.labels(**labels_dict)
        our_actual_pos_attestations_reward_per_validator_count.labels(**labels_dict)
        our_actual_neg_attestations_reward_per_validator_count.labels(**labels_dict)


def _validator_counters_update(counter_pos: Counter | None, counter_neg: Counter | None, pub_keys: Tuple[str],
                               values: set[int], labels_dict: dict[str, dict[str, str]]
                               ) -> None:
    if counter_pos is None or len(labels_dict) == 0:
        return
    for (pubkey, value) in zip(pub_keys, values):
        labels = labels_dict[pubkey]
        (
            counter_pos
            if value >= 0
            else counter_neg
        ).labels(**labels).inc(abs(value))


def _validator_summary_counters_update(counter_pos: Counter | None, counter_neg: Counter | None, pub_keys: Tuple[str],
                                       sources: set[int], targets: set[int], heads: set[int],
                                       labels_dict: dict[str, dict[str, str]]
                                       ) -> None:
    if counter_pos is None or len(labels_dict) == 0:
        return
    for (pubkey, source, target, head) in zip(pub_keys, sources, targets, heads):
        labels = labels_dict[pubkey]
        value = source + target + head
        (
            counter_pos
            if value >= 0
            else counter_neg
        ).labels(**labels).inc(abs(value))


def _log(
        pubkeys: Tuple[str],
        are_ideal: Tuple[bool],
        suboptimal_rate: float,
        epoch: int,
        picto: str,
        label: str,
) -> None:
    not_perfect_pubkeys = {
        pubkey for (pubkey, perfect) in zip(pubkeys, are_ideal) if not perfect
    }

    if len(not_perfect_pubkeys) > 0:
        first_not_perfect_pubkeys = sorted(not_perfect_pubkeys)[:5]

        short_first_not_perfect_pubkeys = [
            pubkey[:10] for pubkey in first_not_perfect_pubkeys
        ]

        short_first_not_perfect_pubkeys_str = ", ".join(short_first_not_perfect_pubkeys)

        diff = len(not_perfect_pubkeys) - len(first_not_perfect_pubkeys)

        print(
            f"{picto} Our validator {short_first_not_perfect_pubkeys_str} and {diff} "
            f"more had not ideal rewards on {label} at epoch {epoch - 2} "
            f"({suboptimal_rate:.2%})"
        )


def process_rewards(
        beacon: Beacon,
        beacon_type: BeaconType,
        epoch: int,
        net_epoch_to_index_to_validator: LimitedDict,
        our_epoch_to_index_to_validator: LimitedDict,
        our_labels: dict[str, dict[str, str]],
) -> None:
    """Process rewards for given epoch and validators

    Parameters:
        beacon (Beacon): Beacon object
        beacon_type (BeaconType): Beacon type
        epoch (int): Epoch number

        net_epoch_to_index_to_validator : Limited dictionary with:
            outer key             : epoch
            outer value, inner key: validator indexes
            inner value           : validators

        our_epoch_to_index_to_validator : Limited dictionary with:
            outer key             : epoch
            outer value, inner key: validator indexes
            inner value           : validators
        our_labels : Pubkey to labels dictionary
    """

    if epoch < 2:
        return

    # Network validators
    # ------------------
    net_index_to_validator = (
        net_epoch_to_index_to_validator[epoch - 2]
        if epoch - 2 in net_epoch_to_index_to_validator
        else (
            net_epoch_to_index_to_validator[epoch - 1]
            if epoch - 1 in net_epoch_to_index_to_validator
            else net_epoch_to_index_to_validator[epoch]
        )
    )

    if len(net_index_to_validator) == 0:
        return

    data = beacon.get_rewards(beacon_type, epoch - 2).data

    effective_balance_to_ideal_reward: dict[int, Reward] = {
        reward.effective_balance: (reward.source, reward.target, reward.head)
        for reward in data.ideal_rewards
    }

    index_to_actual_reward: dict[int, Reward] = {
        reward.validator_index: (reward.source, reward.target, reward.head)
        for reward in data.total_rewards
    }

    items = [
        _process_validator(
            validator.pubkey,
            effective_balance_to_ideal_reward[validator.effective_balance],
            index_to_actual_reward[index],
        )
        for index, validator in net_index_to_validator.items()
        if index in index_to_actual_reward
        and validator.effective_balance in effective_balance_to_ideal_reward
    ]

    unzipped: Tuple[
        Tuple[str], Tuple[Reward], Tuple[Reward], Tuple[AreIdeal]
    ] = zip(  # type:ignore
        *items
    )

    _, ideal_rewards, actual_rewards, ideals = unzipped

    ideal_sources, ideal_targets, ideal_heads = zip(*ideal_rewards)
    actual_sources, actual_targets, actual_heads = zip(*actual_rewards)
    are_sources_ideal, are_targets_ideal, are_heads_ideal = zip(*ideals)

    total_ideal_sources = sum(ideal_sources)
    total_ideal_targets = sum(ideal_targets)
    total_ideal_heads = sum(ideal_heads)

    metric_net_ideal_sources_count.inc(total_ideal_sources)
    metric_net_ideal_targets_count.inc(total_ideal_targets)
    metric_net_ideal_heads_count.inc(total_ideal_heads)

    total_actual_sources = sum(actual_sources)
    total_actual_targets = sum(actual_targets)
    total_actual_heads = sum(actual_heads)

    (
        metric_net_actual_pos_sources_count
        if total_actual_sources >= 0
        else metric_net_actual_neg_sources_count
    ).inc(abs(total_actual_sources))

    (
        metric_net_actual_pos_targets_count
        if total_actual_targets >= 0
        else metric_net_actual_neg_targets_count
    ).inc(abs(total_actual_targets))

    metric_net_actual_heads_count.inc(total_actual_heads)

    suboptimal_sources_rate = 1 - sum(are_sources_ideal) / len(are_sources_ideal)
    suboptimal_targets_rate = 1 - sum(are_targets_ideal) / len(are_targets_ideal)
    suboptimal_heads_rate = 1 - sum(are_heads_ideal) / len(are_heads_ideal)

    metric_net_suboptimal_sources_rate_gauge.set(suboptimal_sources_rate)
    metric_net_suboptimal_targets_rate_gauge.set(suboptimal_targets_rate)
    metric_net_suboptimal_heads_rate_gauge.set(suboptimal_heads_rate)

    # Our validators
    # --------------
    our_index_to_validator = (
        our_epoch_to_index_to_validator[epoch - 2]
        if epoch - 2 in our_epoch_to_index_to_validator
        else (
            our_epoch_to_index_to_validator[epoch - 1]
            if epoch - 1 in our_epoch_to_index_to_validator
            else our_epoch_to_index_to_validator[epoch]
        )
    )

    our_indexes = set(our_index_to_validator)

    if len(our_indexes) == 0:
        return

    data = beacon.get_rewards(beacon_type, epoch - 2, our_indexes).data

    effective_balance_to_ideal_reward = {
        reward.effective_balance: (reward.source, reward.target, reward.head)
        for reward in data.ideal_rewards
    }

    index_to_actual_reward = {
        reward.validator_index: (reward.source, reward.target, reward.head)
        for reward in data.total_rewards
    }

    items = [
        _process_validator(
            validator.pubkey,
            effective_balance_to_ideal_reward[validator.effective_balance],
            index_to_actual_reward[index],
        )
        for index, validator in our_index_to_validator.items()
    ]

    unzipped = zip(*items)  # type: ignore

    pubkeys, ideal_rewards, actual_rewards, ideals = unzipped

    ideal_sources, ideal_targets, ideal_heads = zip(*ideal_rewards)
    actual_sources, actual_targets, actual_heads = zip(*actual_rewards)
    are_sources_ideal, are_targets_ideal, are_heads_ideal = zip(*ideals)

    total_ideal_sources = sum(ideal_sources)
    total_ideal_targets = sum(ideal_targets)
    total_ideal_heads = sum(ideal_heads)

    metric_our_ideal_sources_count.inc(total_ideal_sources)
    metric_our_ideal_targets_count.inc(total_ideal_targets)
    metric_our_ideal_heads_count.inc(total_ideal_heads)

    total_actual_sources = sum(actual_sources)
    total_actual_targets = sum(actual_targets)
    total_actual_heads = sum(actual_heads)

    (
        metric_our_actual_pos_sources_count
        if total_actual_sources >= 0
        else metric_our_actual_neg_sources_count
    ).inc(abs(total_actual_sources))

    (
        metric_our_actual_pos_targets_count
        if total_actual_targets >= 0
        else metric_our_actual_neg_targets_count
    ).inc(abs(total_actual_targets))

    metric_our_actual_heads_count.inc(total_actual_heads)

    suboptimal_sources_rate = 1 - sum(are_sources_ideal) / len(are_sources_ideal)
    suboptimal_targets_rate = 1 - sum(are_targets_ideal) / len(are_targets_ideal)
    suboptimal_heads_rate = 1 - sum(are_heads_ideal) / len(are_heads_ideal)

    metric_our_suboptimal_sources_rate_gauge.set(suboptimal_sources_rate)
    metric_our_suboptimal_targets_rate_gauge.set(suboptimal_targets_rate)
    metric_our_suboptimal_heads_rate_gauge.set(suboptimal_heads_rate)

    _validator_counters_update(our_ideal_sources_per_validator_count, None, pubkeys, ideal_sources, our_labels)
    _validator_counters_update(our_ideal_targets_per_validator_count, None, pubkeys, ideal_targets, our_labels)
    _validator_counters_update(our_ideal_heads_per_validator_count, None, pubkeys, ideal_heads, our_labels)
    _validator_counters_update(our_actual_pos_sources_per_validator_count, our_actual_neg_sources_per_validator_count,
                               pubkeys, actual_sources, our_labels)
    _validator_counters_update(our_actual_pos_targets_per_validator_count, our_actual_neg_targets_per_validator_count,
                               pubkeys, actual_targets, our_labels)
    _validator_counters_update(our_actual_heads_per_validator_count, None, pubkeys, actual_heads, our_labels)
    _validator_summary_counters_update(our_ideal_attestations_reward_per_validator_count, None, pubkeys, ideal_sources,
                                       ideal_targets, ideal_heads, our_labels)
    _validator_summary_counters_update(our_actual_pos_attestations_reward_per_validator_count,
                                       our_actual_neg_attestations_reward_per_validator_count, pubkeys, actual_sources,
                                       actual_targets, actual_heads, our_labels)

    _log(pubkeys, are_sources_ideal, suboptimal_sources_rate, epoch, "🚰", "source")
    _log(pubkeys, are_targets_ideal, suboptimal_targets_rate, epoch, "🎯", "target")
    _log(pubkeys, are_heads_ideal, suboptimal_heads_rate, epoch, "👤", "head ")


def _process_validator(
        pubkey: str,
        ideal_reward: Reward,
        actual_reward: Reward,
) -> Tuple[str, Reward, Reward, AreIdeal]:
    (ideal_source_reward, ideal_target_reward, ideal_head_reward) = ideal_reward
    (actual_source_reward, actual_target_reward, actual_head_reward) = actual_reward

    are_ideal = (
        actual_source_reward == ideal_source_reward,
        actual_target_reward == ideal_target_reward,
        actual_head_reward == ideal_head_reward,
    )

    return pubkey, ideal_reward, actual_reward, are_ideal
