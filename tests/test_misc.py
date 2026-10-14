from htmx_invaders.content import FRAMEWORKS, JOKES, POWERUPS
from htmx_invaders.util import lighten, pulse


def test_content_is_consistent():
    assert len({f.name for f in FRAMEWORKS}) == len(FRAMEWORKS)
    assert all(f.file.endswith(".png") for f in FRAMEWORKS)
    assert len({p.effect for p in POWERUPS}) == len(POWERUPS)
    assert all(p.weight > 0 for p in POWERUPS)
    assert JOKES


def test_lighten_bounds():
    assert lighten((10, 20, 30), 0) == (10, 20, 30)
    assert lighten((10, 20, 30), 1) == (255, 255, 255)


def test_pulse_in_unit_range():
    assert 0 <= pulse(250) <= 1
