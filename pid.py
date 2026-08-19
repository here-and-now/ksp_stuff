"""Discrete PID. Descended from Art Whaley's kRPC demo, with a real dt.

Original: https://github.com/krpc/krpc-library/blob/master/Art_Whaleys_KRPC_Demos/pid.py
"""

from __future__ import annotations

import time

from geometry import clamp


class PID:
    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.1,
        kd: float = 0.01,
        *,
        i_limit: float = 1.0,
        out_min: float = 0.0,
        out_max: float = 1.0,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_limit = i_limit
        self.out_min = out_min
        self.out_max = out_max
        self.setpoint = 0.0
        self._i = 0.0
        self._last_time = time.monotonic()
        self._last_measure = 0.0

    def reset(self, setpoint: float | None = None) -> None:
        if setpoint is not None:
            self.setpoint = setpoint
        self._i = 0.0
        self._last_time = time.monotonic()
        self._last_measure = 0.0

    def update(self, measure: float, now: float | None = None) -> float:
        now = time.monotonic() if now is None else now
        dt = now - self._last_time
        if dt <= 0:
            dt = 1e-6
        error = self.setpoint - measure
        self._i = clamp(self._i + error * dt, -self.i_limit, self.i_limit)
        derivative = (measure - self._last_measure) / dt
        self._last_measure = measure
        self._last_time = now
        raw = self.kp * error + self.ki * self._i - self.kd * derivative
        return clamp(raw, self.out_min, self.out_max)
