from FidgetSpinner import decay_turn


def test_turn_decay_stops_at_zero() -> None:
    assert decay_turn(10) == 9
    assert decay_turn(1) == 0
    assert decay_turn(0) == 0
