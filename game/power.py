"""Building power system (v0.3).

Power drains every second (normal office operation) and faster while the
CCTV is open. Doors, lights and emergency systems will add their own drain
rates in later versions -- every rate lives in settings.py, never hard-coded.
"""

from settings import POWER_MAX, POWER_BASE_DRAIN, POWER_CAMERA_DRAIN


class PowerSystem:
    def __init__(self):
        self.level = POWER_MAX

    @property
    def has_power(self):
        return self.level > 0.0

    @property
    def percent(self):
        return int(self.level)

    def update(self, dt, cameras_open):
        if self.level <= 0.0:
            return
        drain = POWER_BASE_DRAIN
        if cameras_open:
            drain += POWER_CAMERA_DRAIN
        self.level = max(0.0, self.level - drain * dt)
