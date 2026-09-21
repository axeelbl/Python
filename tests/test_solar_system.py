from collections import deque

import pytest

from SolarSystem import MAX_ORBIT_POINTS, Planet, create_planets, step


def make_pair() -> list[Planet]:
    return [
        Planet(-1.0e8, 0, 10, (255, 255, 0), 2.0e20, is_sun=True),
        Planet(1.0e8, 0, 5, (0, 0, 255), 1.0e20),
    ]


def test_gravity_is_equal_and_opposite() -> None:
    first, second = make_pair()
    first_force = first.attraction(second)
    second_force = second.attraction(first)
    assert first_force[0] == pytest.approx(-second_force[0])
    assert first_force[1] == pytest.approx(-second_force[1])


def test_step_is_independent_of_planet_list_order() -> None:
    forward = make_pair()
    reverse = make_pair()[::-1]

    step(forward)
    step(reverse)

    forward_by_mass = {planet.mass: planet for planet in forward}
    reverse_by_mass = {planet.mass: planet for planet in reverse}
    for mass in forward_by_mass:
        assert forward_by_mass[mass].x == pytest.approx(reverse_by_mass[mass].x)
        assert forward_by_mass[mass].x_velocity == pytest.approx(reverse_by_mass[mass].x_velocity)


def test_planet_validation_and_collision_guard() -> None:
    with pytest.raises(ValueError, match="mass"):
        Planet(0, 0, 1, (0, 0, 0), 0)

    first = Planet(0, 0, 1, (0, 0, 0), 1)
    second = Planet(0, 0, 1, (0, 0, 0), 1)
    with pytest.raises(ValueError, match="same position"):
        first.attraction(second)


def test_orbit_history_is_bounded() -> None:
    planet = make_pair()[0]
    assert isinstance(planet.orbit, deque)
    for _ in range(MAX_ORBIT_POINTS + 5):
        planet.advance((0, 0))
    assert len(planet.orbit) == MAX_ORBIT_POINTS


def test_one_frame_renders_with_headless_video_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pygame

    pygame.init()
    try:
        window = pygame.display.set_mode((800, 800))
        font = pygame.font.Font(None, 16)
        planets = create_planets()
        step(planets)
        for planet in planets:
            planet.draw(window, font, pygame)
        pygame.display.flip()
    finally:
        pygame.quit()
