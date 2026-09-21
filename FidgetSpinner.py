"""Interactive fidget-spinner animation built with the turtle module."""

from __future__ import annotations

import turtle

TURN_INCREMENT = 10
FRAME_DELAY_MS = 20
COLORS = ("red", "green", "blue")


def decay_turn(turn: int) -> int:
    """Reduce the spin impulse by one frame without becoming negative."""
    return max(0, turn - 1)


def main() -> None:
    screen = turtle.Screen()
    screen.setup(width=420, height=420, startx=370, starty=0)
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.width(20)
    state = {"turn": 0}

    def draw_spinner() -> None:
        pen.clear()
        pen.right(state["turn"] / 10)
        for color in COLORS:
            pen.forward(100)
            pen.dot(120, color)
            pen.back(100)
            pen.right(120)
        screen.update()

    def animate() -> None:
        state["turn"] = decay_turn(state["turn"])
        draw_spinner()
        screen.ontimer(animate, FRAME_DELAY_MS)

    def flick() -> None:
        state["turn"] += TURN_INCREMENT

    screen.onkey(flick, "space")
    screen.listen()
    animate()
    screen.mainloop()


if __name__ == "__main__":
    main()
