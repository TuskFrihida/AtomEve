"""Curated science & space facts powering the ``/fact`` command.

A small static dataset keeps the function fast and dependency-free — no
external API call (and no extra latency or rate limits) on every request.
"""

from __future__ import annotations

import random

FACTS: list[str] = [
    "A single teaspoon of a neutron star would weigh about 6 billion tons on Earth.",
    "There are more atoms in a single glass of water than glasses of water in all the oceans.",
    "Light from the Sun takes roughly 8 minutes and 20 seconds to reach Earth.",
    "Hydrogen and helium make up about 98% of all ordinary matter in the universe.",
    "A day on Venus is longer than its year — it rotates slower than it orbits the Sun.",
    "If you could fold a piece of paper 42 times, it would reach the Moon.",
    "The observable universe contains an estimated two trillion galaxies.",
    "Atoms are 99.9999999% empty space — solid matter is mostly nothing at all.",
    "Saturn's density is so low that it would float in a (sufficiently large) bathtub.",
    "Your body contains about 7 octillion atoms, forged inside ancient stars.",
    "The footprints left by Apollo astronauts on the Moon could last millions of years.",
    "One million Earths could fit inside the Sun, yet it is an average-sized star.",
]


def random_fact() -> str:
    """Return a random fact from the curated list."""
    return random.choice(FACTS)
