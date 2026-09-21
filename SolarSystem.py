"""A simple Newtonian solar-system simulation rendered with pygame."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import ClassVar

WIDTH = 800
HEIGHT = 800
MAX_ORBIT_POINTS = 5_000

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)


@dataclass
class Planet:
    """Position, velocity, and physical properties of one simulated body."""

    AU: ClassVar[float] = 149.6e6 * 1_000
    G: ClassVar[float] = 6.67428e-11
    SCALE: ClassVar[float] = 250 / AU  # 1 AU = 250 pixels
    TIMESTEP: ClassVar[float] = 3_600 * 24  # 1 day

    x: float
    y: float
    radius: int
    color: tuple[int, int, int]
    mass: float
    is_sun: bool = False
    distance_to_sun: float = 0
    x_velocity: float = 0
    y_velocity: float = 0
    orbit: deque[tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=MAX_ORBIT_POINTS)
    )

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("mass must be positive")
        if self.radius <= 0:
            raise ValueError("radius must be positive")
        if not all(math.isfinite(value) for value in (self.x, self.y, self.mass)):
            raise ValueError("position and mass must be finite")

    def attraction(self, other: Planet) -> tuple[float, float]:
        """Return the gravitational force exerted on this planet by another."""
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance_squared = distance_x**2 + distance_y**2
        if distance_squared == 0:
            raise ValueError("different planets cannot occupy the same position")

        distance = math.sqrt(distance_squared)
        if other.is_sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance_squared
        return force * distance_x / distance, force * distance_y / distance

    def acceleration(self, planets: list[Planet]) -> tuple[float, float]:
        """Calculate acceleration from a shared, unchanged system state."""
        total_force_x = 0.0
        total_force_y = 0.0
        for planet in planets:
            if self is planet:
                continue
            force_x, force_y = self.attraction(planet)
            total_force_x += force_x
            total_force_y += force_y
        return total_force_x / self.mass, total_force_y / self.mass

    def advance(self, acceleration: tuple[float, float]) -> None:
        """Advance velocity and position by one simulation timestep."""
        acceleration_x, acceleration_y = acceleration
        self.x_velocity += acceleration_x * self.TIMESTEP
        self.y_velocity += acceleration_y * self.TIMESTEP
        self.x += self.x_velocity * self.TIMESTEP
        self.y += self.y_velocity * self.TIMESTEP
        self.orbit.append((self.x, self.y))

    def draw(self, window: object, font: object, pygame_module: object) -> None:
        """Draw the orbit, body, and current solar distance."""
        screen_x = self.x * self.SCALE + WIDTH / 2
        screen_y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            points = [
                (
                    round(x * self.SCALE + WIDTH / 2),
                    round(y * self.SCALE + HEIGHT / 2),
                )
                for x, y in self.orbit
            ]
            pygame_module.draw.lines(window, self.color, False, points, 2)

        center = (round(screen_x), round(screen_y))
        pygame_module.draw.circle(window, self.color, center, self.radius)

        if not self.is_sun:
            distance_text = font.render(f"{round(self.distance_to_sun / 1_000, 1)} km", True, WHITE)
            window.blit(
                distance_text,
                (
                    screen_x - distance_text.get_width() / 2,
                    screen_y - distance_text.get_height() / 2,
                ),
            )


def step(planets: list[Planet]) -> None:
    """Advance every body simultaneously so list order cannot bias physics."""
    accelerations = [planet.acceleration(planets) for planet in planets]
    for planet, acceleration in zip(planets, accelerations, strict=True):
        planet.advance(acceleration)


def create_planets() -> list[Planet]:
    sun = Planet(0, 0, 30, YELLOW, 1.98892e30, is_sun=True)
    earth = Planet(-Planet.AU, 0, 16, BLUE, 5.9742e24, y_velocity=29.783e3)
    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39e23, y_velocity=24.077e3)
    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30e23, y_velocity=-47.4e3)
    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 4.8685e24, y_velocity=-35.02e3)
    return [sun, earth, mars, mercury, venus]


def main() -> None:
    import pygame

    pygame.init()
    try:
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Planet Simulation")
        font = pygame.font.SysFont("comicsans", 16)
        clock = pygame.time.Clock()
        planets = create_planets()
        running = True

        while running:
            clock.tick(40)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            step(planets)
            window.fill((0, 0, 0))
            for planet in planets:
                planet.draw(window, font, pygame)
            pygame.display.update()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
