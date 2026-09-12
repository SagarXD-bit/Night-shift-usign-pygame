"""In-game clock: runs 12 AM -> 6 AM at a configurable speed."""


class GameClock:
    def __init__(self, seconds_per_hour, hours_per_night=6):
        self.seconds_per_hour = seconds_per_hour
        self.hours_per_night = hours_per_night
        self.elapsed = 0.0  # real seconds survived this night
        self.finished = False

    def update(self, dt):
        if not self.finished:
            self.elapsed += dt
            if self.hour_index >= self.hours_per_night:
                self.finished = True

    @property
    def hour_index(self):
        """0 == 12 AM, 1 == 1 AM, ... 6 == 6 AM."""
        return int(self.elapsed // self.seconds_per_hour)

    @property
    def display(self):
        idx = min(self.hour_index, self.hours_per_night)
        hour = 12 if idx == 0 else idx
        return f"{hour} AM"

    @property
    def progress(self):
        """0.0 at 12 AM, 1.0 at 6 AM."""
        total = self.seconds_per_hour * self.hours_per_night
        return min(self.elapsed / total, 1.0)
