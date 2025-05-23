"""Contains the logic to check if the validators missed attestations."""

import functools
import random

from prometheus_client import Counter, Gauge

from eth_validator_watcher.models import BeaconType

from .beacon import Beacon
from .models import Validators
from .utils import LimitedDict, Slack

print = functools.partial(print, flush=True)

metric_missed_attestations_count = Gauge(
    "missed_attestations_count",
    "Missed attestations count",
)

metric_double_missed_attestations_count = Gauge(
    "double_missed_attestations_count",
    "Double missed attestations count",
)

missed_attestations_per_validator_count: Counter | None = None
double_missed_attestations_per_validator_count: Counter | None = None


def init_missed_attestations_per_validator_counters(our_labels: dict[str, dict[str, str]]) -> None:
    global missed_attestations_per_validator_count
    global double_missed_attestations_per_validator_count

    if len(our_labels) == 0 or missed_attestations_per_validator_count is not None:
        return

    labels = list(random.choice(list(our_labels.values())).keys())
    missed_attestations_per_validator_count = Counter(
        "missed_attestations_per_validator_count",
        "Missed attestations per validator",
        labels)
    double_missed_attestations_per_validator_count = Counter(
        "double_missed_attestations_per_validator_count",
        "Double missed attestations per validator (finalized)",
        labels)
    for labels_dict in our_labels.values():
        missed_attestations_per_validator_count.labels(**labels_dict)
        double_missed_attestations_per_validator_count.labels(**labels_dict)


def process_missed_attestations(
        beacon: Beacon,
        beacon_type: BeaconType,
        epoch_to_index_to_validator_index: LimitedDict,
        epoch: int,
        our_labels: dict[str, dict[str, str]],
) -> set[int]:
    """Process missed attestations.

    Parameters:
    beacon                       : Beacon instance
    beacon_type                  : Beacon type
    epoch_to_index_to_validator : Limited dictionary with:
        outer key             : epoch
        outer value, inner key: validator indexes
        inner value           : validators
    epoch                        : Epoch where the missed attestations are checked
    our_labels                   : Pubkey to labels dictionary
    """
    if epoch < 1:
        return set()

    index_to_validator: dict[int, Validators.DataItem.Validator] = (
        epoch_to_index_to_validator_index[epoch - 1]
        if epoch - 1 in epoch_to_index_to_validator_index
        else epoch_to_index_to_validator_index[epoch]
    )

    validators_index = set(index_to_validator)
    validators_liveness = beacon.get_validators_liveness(
        beacon_type, epoch - 1, validators_index
    )

    dead_indexes = {
        index for index, liveness in validators_liveness.items() if not liveness
    }

    metric_missed_attestations_count.set(len(dead_indexes))

    if len(dead_indexes) == 0:
        return set()

    pubkeys = list(
        index_to_validator[index].pubkey for index in dead_indexes
    )

    first_pubkeys = pubkeys[:5]

    short_first_pubkeys = [pubkey[:10] for pubkey in first_pubkeys]
    short_first_pubkeys_str = ", ".join(short_first_pubkeys)

    print(
        f"🙁 Our validator {short_first_pubkeys_str} and "
        f"{len(dead_indexes) - len(short_first_pubkeys)} more "
        f"missed attestation at epoch {epoch - 1}"
    )

    if missed_attestations_per_validator_count is not None and len(our_labels) > 0:
        for pubkey in pubkeys:
            labels = our_labels[pubkey]
            missed_attestations_per_validator_count.labels(**labels).inc()

    return dead_indexes


def process_double_missed_attestations(
        dead_indexes: set[int],
        previous_dead_indexes: set[int],
        epoch_to_index_to_validator_index: LimitedDict,
        epoch: int,
        slack: Slack | None,
        our_labels: dict[str, dict[str, str]],
) -> set[int]:
    """Process double missed attestations.

    Parameters:
    dead_indexes                 : Set of indexes of the validators that missed
                                   attestations
    previous_dead_indexes        : Set of indexes of the validators that missed
                                   attestations in the previous epoch

    epoch_to_index_to_validator  : Limited dictionary with:
        outer key             : epoch
        outer value, inner key: validator indexes
        inner value           : validators

    epoch                        : Epoch where the missed attestations are checked
    slack                        : Slack instance
    our_labels                   : Pubkey to labels dictionary
    """
    if epoch < 2:
        return set()

    double_dead_indexes = dead_indexes & previous_dead_indexes
    metric_double_missed_attestations_count.set(len(double_dead_indexes))

    if len(double_dead_indexes) == 0:
        return set()

    index_to_validator = epoch_to_index_to_validator_index[epoch - 1]

    pubkeys = list(
        index_to_validator[index].pubkey for index in double_dead_indexes
    )

    first_pubkeys = pubkeys[:5]

    short_first_pubkeys = [pubkey[:10] for pubkey in first_pubkeys]
    short_first_pubkeys_str = ", ".join(short_first_pubkeys)

    message_console = (
        f"😱 Our validator {short_first_pubkeys_str} and "
        f"{len(double_dead_indexes) - len(short_first_pubkeys)} more "
        f"missed 2 attestations in a row from epoch {epoch - 2}"
    )

    print(message_console)

    if slack is not None:
        message_slack = (
            f"😱 Our validator `{short_first_pubkeys_str}` and "
            f"`{len(double_dead_indexes) - len(short_first_pubkeys)}` more "
            f"missed 2 attestations in a row from epoch `{epoch - 2}`"
        )

        slack.send_message(message_slack)

    if double_missed_attestations_per_validator_count is not None and len(our_labels) > 0:
        for pubkey in pubkeys:
            labels = our_labels[pubkey]
            double_missed_attestations_per_validator_count.labels(**labels).inc()

    return double_dead_indexes
