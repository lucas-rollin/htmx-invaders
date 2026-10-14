import pytest

from htmx_invaders.content import FRAMEWORKS
from htmx_invaders.entities import Enemy
from htmx_invaders.formation import Formation
from htmx_invaders.settings import WIDTH


def lone_enemy(x, y=100):
    e = Enemy(0, 0, FRAMEWORKS[0])
    e.base_x, e.base_y = x, y
    f = Formation()
    f.enemies = [e]
    f.dx = 100.0
    return f, e


@pytest.mark.parametrize(
    "level,expected", [(1, 3 * 6), (2, 3 * 7), (3, 4 * 8), (20, 7 * 16)]
)
def test_spawn_size_and_caps(level, expected):
    f = Formation()
    f.spawn(level)
    assert len(f) == expected


@pytest.mark.parametrize("level", range(1, 21))
def test_spawn_fits_on_screen(level):
    f = Formation()
    f.spawn(level)
    assert min(e.x for e in f) >= Formation.EDGE_MARGIN
    assert max(e.x + e.WIDTH for e in f) <= WIDTH - Formation.EDGE_MARGIN


def test_spawn_speed_scales_with_level_and_resets_drop():
    f = Formation()
    f.total_drop = 99
    f.spawn(3)
    assert f.dx == 50 + 3 * 8
    assert f.total_drop == 0


def test_marches_sideways():
    f, e = lone_enemy(500)
    f.update(0.1)
    assert e.base_x == pytest.approx(510)
    assert e.base_y == 100
    assert f.total_drop == 0


def test_bounces_and_drops_at_right_wall():
    f, e = lone_enemy(WIDTH - 20 - Enemy.WIDTH)
    x = e.base_x
    f.update(0.1)
    assert f.dx == -100.0
    assert e.base_x == x  # doesn't move sideways on the bounce frame
    assert e.base_y == 100 + Formation.DROP_STEP
    assert f.total_drop == Formation.DROP_STEP


def test_bounces_at_left_wall():
    f, _e = lone_enemy(Formation.EDGE_MARGIN)
    f.dx = -100.0
    f.update(0.1)
    assert f.dx == 100.0
    assert f.total_drop == Formation.DROP_STEP


def test_update_with_no_enemies_is_safe():
    Formation().update(0.1)


def test_push_back_requires_prior_drop():
    f, e = lone_enemy(500)
    assert f.push_back() is False
    assert e.base_y == 100


def test_push_back_one_and_two_steps():
    f, e = lone_enemy(500)
    f.total_drop = Formation.DROP_STEP
    assert f.push_back()
    assert e.base_y == 100 - Formation.DROP_STEP

    f.total_drop = Formation.DROP_STEP * 2
    assert f.push_back()
    assert e.base_y == 100 - Formation.DROP_STEP * 3


def test_remove_dead():
    f = Formation()
    f.spawn(1)
    f.enemies[0].alive = False
    f.remove_dead()
    assert len(f) == 17


def test_reached():
    f, _e = lone_enemy(500, y=300)
    assert not f.reached(600)
    assert f.reached(300 + Enemy.HEIGHT - 10)
