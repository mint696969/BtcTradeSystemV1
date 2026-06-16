# path: ./btcts_next/src/btcts/replay/replay_clock.py
# desc: Replay clock for controlling playback state and speed.

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReplayClock:
    speed: float = 1.0
    paused: bool = False

    def set_speed(self, speed: float) -> None:
        if speed <= 0:
            raise ValueError("speed must be > 0")
        self.speed = float(speed)

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def toggle(self) -> None:
        self.paused = not self.paused