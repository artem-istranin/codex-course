import pytest

from app.randomizer import pick_winner_index


class StubRandomizer:
    def __init__(self, chosen_index: int) -> None:
        self.chosen_index = chosen_index

    def randrange(self, stop: int) -> int:
        assert stop > self.chosen_index
        return self.chosen_index


def test_pick_winner_index_uses_randomizer_result() -> None:
    participants = ["Alice", "Bob", "Clara"]

    winner_index = pick_winner_index(
        participants,
        randomizer=StubRandomizer(chosen_index=1),
    )

    assert winner_index == 1


def test_pick_winner_index_requires_participants() -> None:
    with pytest.raises(ValueError, match="participants must contain at least one item"):
        pick_winner_index([])
