from random import Random, SystemRandom


_randomizer = SystemRandom()


def pick_winner_index(
    participants: list[str],
    randomizer: Random | SystemRandom | None = None,
) -> int:
    if not participants:
        raise ValueError(
            "participants must contain at least one item"
        )

    rng = randomizer or _randomizer
    return rng.randrange(len(participants))
