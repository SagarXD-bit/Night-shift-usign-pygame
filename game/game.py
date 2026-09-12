import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    SECONDS_PER_GAME_HOUR, GAME_HOUR_OPTIONS,
    INTERACT_RANGE, MESSAGE_DURATION,
    POWER_MAX, POWER_LOW,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    COLOR_PANEL, COLOR_DANGER,
    DARKNESS_ALPHA, LIGHT_STEPS, BLACKOUT_ALPHA, BLACKOUT_LIGHT_STEPS,
)
from game.cameras import CameraSystem
from game.clock import GameClock
from game.office import Office
from game.player import Player
from game.power import PowerSystem


class Game:
    """Owns the window, the main loop, and the game-state machine."""

    STATE_MENU = "menu"
    STATE_SETTINGS = "settings"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_NIGHT_COMPLETE = "night_complete"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.Font(None, 76)
        self.font_lg = pygame.font.Font(None, 44)
        self.font_md = pygame.font.Font(None, 28)
        self.font_sm = pygame.font.Font(None, 22)

        self.running = True
        self.state = self.STATE_MENU
        self.previous_state = self.STATE_MENU  # where the Settings screen returns to

        self.night = 1
        self.seconds_per_hour = SECONDS_PER_GAME_HOUR

        self.office = Office()
        self.cameras = CameraSystem()
        self.power = PowerSystem()
        self.player = None
        self.game_clock = None

        self.message = ""
        self.message_timer = 0.0
        self.death_cause = ""

        self.menu_index = 0
        self.settings_index = 0
        self.pause_index = 0

    # ------------------------------------------------------------------ loop

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _update(self, dt):
        if self.state != self.STATE_PLAYING:
            return
        if self.cameras.is_open:
            # Time keeps passing while the player watches the monitors.
            self.cameras.update(dt)
        else:
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.office.walls)
        self.game_clock.update(dt)
        had_power = self.power.has_power
        self.power.update(dt, self.cameras.is_open)
        if had_power and not self.power.has_power:
            self._on_blackout()
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        if self.game_clock.finished:
            self.state = self.STATE_NIGHT_COMPLETE

    # ---------------------------------------------------------------- input

    def _handle_key(self, key):
        handler = {
            self.STATE_MENU: self._key_menu,
            self.STATE_SETTINGS: self._key_settings,
            self.STATE_PLAYING: self._key_playing,
            self.STATE_PAUSED: self._key_paused,
            self.STATE_NIGHT_COMPLETE: self._key_night_complete,
            self.STATE_GAME_OVER: self._key_game_over,
        }[self.state]
        handler(key)

    def _key_menu(self, key):
        items = self._menu_items()
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_index = self._step_menu(items, self.menu_index, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = self._step_menu(items, self.menu_index, +1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            label, enabled = items[self.menu_index]
            if enabled:
                self._activate_menu_item(label)

    @staticmethod
    def _step_menu(items, index, step):
        """Move the cursor, skipping disabled entries."""
        for _ in range(len(items)):
            index = (index + step) % len(items)
            if items[index][1]:
                break
        return index

    def _activate_menu_item(self, label):
        if label == "PLAY":
            self.night = 1
            self.start_night()
        elif label == "SETTINGS":
            self.previous_state = self.STATE_MENU
            self.state = self.STATE_SETTINGS
        elif label == "QUIT":
            self.running = False

    def _key_settings(self, key):
        if key == pygame.K_ESCAPE:
            self.state = self.previous_state
        elif key in (pygame.K_UP, pygame.K_w):
            self.settings_index = (self.settings_index - 1) % 2
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.settings_index = (self.settings_index + 1) % 2
        elif key in (pygame.K_LEFT, pygame.K_a) and self.settings_index == 0:
            self._cycle_speed(forward=False)
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.settings_index == 0:
            self._cycle_speed(forward=True)
        elif key in (pygame.K_RETURN, pygame.K_SPACE) and self.settings_index == 1:
            self.state = self.previous_state

    def _key_playing(self, key):
        if self.cameras.is_open:
            self.cameras.handle_key(key)  # ESC/E closes the CCTV first
            return
        if key == pygame.K_ESCAPE:
            self.state = self.STATE_PAUSED
        elif key == pygame.K_e:
            self._interact()
        elif key == pygame.K_F9:
            # Temporary debug key so the death screen can be previewed
            # before enemies exist. Will be removed once real threats land.
            self._game_over("You never heard it come in. (debug)")

    def _key_paused(self, key):
        items = ["RESUME", "SETTINGS", "QUIT TO MENU"]
        if key == pygame.K_ESCAPE:
            self.state = self.STATE_PLAYING
        elif key in (pygame.K_UP, pygame.K_w):
            self.pause_index = (self.pause_index - 1) % len(items)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.pause_index = (self.pause_index + 1) % len(items)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = items[self.pause_index]
            if choice == "RESUME":
                self.state = self.STATE_PLAYING
            elif choice == "SETTINGS":
                self.previous_state = self.STATE_PAUSED
                self.state = self.STATE_SETTINGS
            elif choice == "QUIT TO MENU":
                self.state = self.STATE_MENU

    def _key_night_complete(self, key):
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.night += 1
            self.start_night()
        elif key == pygame.K_ESCAPE:
            self.state = self.STATE_MENU

    def _key_game_over(self, key):
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_night()  # retry the same night
        elif key == pygame.K_ESCAPE:
            self.state = self.STATE_MENU

    def _cycle_speed(self, forward):
        options = list(GAME_HOUR_OPTIONS)
        i = options.index(self.seconds_per_hour)
        i = max(0, min(len(options) - 1, i + (1 if forward else -1)))
        self.seconds_per_hour = options[i]

    # ------------------------------------------------------------ game flow

    def start_night(self):
        self.player = Player(400, 330)
        self.game_clock = GameClock(self.seconds_per_hour)
        self.power = PowerSystem()
        self.cameras.close()
        self.message = ""
        self.message_timer = 0.0
        self.pause_index = 0
        self._show_message(f"Night {self.night}. Stay in the office until 6 AM.")
        self.state = self.STATE_PLAYING

    def _game_over(self, cause):
        self.death_cause = cause
        self.state = self.STATE_GAME_OVER

    def _on_blackout(self):
        self.cameras.close()
        self._show_message(
            "The power dies. Somewhere in the walls, the building groans."
        )

    def _show_message(self, text):
        self.message = text
        self.message_timer = MESSAGE_DURATION

    def _interact(self):
        near = self._nearest_interactable()
        if near is None:
            return
        if near.name == "Computer":
            if self.power.has_power:
                self.cameras.open()
            else:
                self._show_message("The computer is dead. The building has no power.")
        elif near.name == "Wall Clock":
            self._show_message(
                f"The clock reads {self.game_clock.display}. Sunrise at 6 AM. "
                "The second hand ticks a little too loudly."
            )
        else:
            self._show_message(near.description)

    def _nearest_interactable(self):
        if self.player is None:
            return None
        px, py = self.player.rect.center
        best, best_dist = None, INTERACT_RANGE
        for item in self.office.interactables:
            cx = max(item.rect.left, min(px, item.rect.right))
            cy = max(item.rect.top, min(py, item.rect.bottom))
            dist = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
            if dist < best_dist:
                best, best_dist = item, dist
        return best

    # ----------------------------------------------------------------- draw

    def _draw(self):
        self.screen.fill(COLOR_BG)
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_SETTINGS:
            self._draw_settings()
        else:
            self._draw_world()
            if self.state == self.STATE_PAUSED:
                self._draw_pause()
            elif self.state == self.STATE_NIGHT_COMPLETE:
                self._draw_night_complete()
            elif self.state == self.STATE_GAME_OVER:
                self._draw_game_over()
        pygame.display.flip()

    def _draw_world(self):
        near = self._nearest_interactable() if self.state == self.STATE_PLAYING else None
        self.office.draw(self.screen, self.font_sm, near)
        self.player.draw(self.screen)
        self._draw_darkness()
        self._draw_hud()
        if self.cameras.is_open:
            # The CCTV feed covers the whole screen: a different machine.
            self.cameras.draw(self.screen, self.font_sm, self.font_md,
                              self.game_clock.display)

    def _draw_darkness(self):
        """Soft pool of light around the player; the rest of the office is dim.

        With no power the pool shrinks to almost nothing.
        """
        if self.power.has_power:
            alpha, steps = DARKNESS_ALPHA, LIGHT_STEPS
        else:
            alpha, steps = BLACKOUT_ALPHA, BLACKOUT_LIGHT_STEPS
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        px, py = self.player.rect.center
        for radius, alpha in steps:
            pygame.draw.circle(overlay, (0, 0, 0, alpha), (px, py), radius)
        self.screen.blit(overlay, (0, 0))

    def _draw_hud(self):
        night = self.font_sm.render(f"NIGHT {self.night}", True, COLOR_TEXT_DIM)
        self.screen.blit(night, (26, 26))
        clock_label = self.font_lg.render(self.game_clock.display, True, COLOR_TEXT)
        self.screen.blit(clock_label, (SCREEN_WIDTH - clock_label.get_width() - 26, 22))

        # Power readout + bar; red when running low.
        low = self.power.percent < POWER_LOW
        power_color = COLOR_DANGER if low else COLOR_TEXT
        power_label = self.font_sm.render(f"POWER: {self.power.percent}%", True, power_color)
        self.screen.blit(power_label, (26, 46))
        bar = pygame.Rect(26, 66, 80, 5)
        pygame.draw.rect(self.screen, (50, 50, 64), bar)
        fill = round(bar.width * self.power.level / POWER_MAX)
        if fill > 0:
            pygame.draw.rect(self.screen, power_color, (bar.x, bar.y, fill, bar.height))

        if self.message:
            self._draw_message_box(self.message, COLOR_TEXT)
        else:
            near = self._nearest_interactable()
            if near:
                self._draw_message_box(f"[E]  {near.prompt}", COLOR_ACCENT)

    def _draw_message_box(self, text, color):
        lines = self._wrap(text, self.font_sm, SCREEN_WIDTH - 220)
        line_h = self.font_sm.get_linesize()
        w = max(self.font_sm.size(line)[0] for line in lines) + 32
        h = line_h * len(lines) + 16
        x = (SCREEN_WIDTH - w) // 2
        y = SCREEN_HEIGHT - h - 20
        panel = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel)
        pygame.draw.rect(self.screen, (62, 62, 78), panel, 1)
        for i, line in enumerate(lines):
            label = self.font_sm.render(line, True, color)
            self.screen.blit(label, (x + 16, y + 8 + i * line_h))

    @staticmethod
    def _wrap(text, font, max_width):
        lines, line = [], ""
        for word in text.split():
            test = f"{line} {word}".strip()
            if font.size(test)[0] <= max_width or not line:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    # ------------------------------------------------------------ full menus

    @staticmethod
    def _menu_items():
        # CONTINUE stays disabled until the save system arrives.
        return [("PLAY", True), ("CONTINUE", False), ("SETTINGS", True), ("QUIT", True)]

    def _draw_menu(self):
        self._centered("NIGHT SHIFT", 150, self.font_xl, COLOR_TEXT)
        self._centered("the building is not empty", 226, self.font_sm, COLOR_TEXT_DIM)
        for i, (label, enabled) in enumerate(self._menu_items()):
            if not enabled:
                color = COLOR_TEXT_DIM
            else:
                color = COLOR_ACCENT if i == self.menu_index else COLOR_TEXT
            prefix = "> " if i == self.menu_index and enabled else "   "
            self._centered(prefix + label, 300 + i * 40, self.font_md, color)
        self._centered("v0.3", SCREEN_HEIGHT - 36, self.font_sm, COLOR_TEXT_DIM)

    def _draw_settings(self):
        self._centered("SETTINGS", 140, self.font_lg, COLOR_TEXT)
        rows = [f"GAME SPEED   < {self.seconds_per_hour}s per hour >", "BACK"]
        for i, row in enumerate(rows):
            color = COLOR_ACCENT if i == self.settings_index else COLOR_TEXT
            prefix = "> " if i == self.settings_index else "   "
            self._centered(prefix + row, 260 + i * 44, self.font_md, color)
        self._centered("How many real seconds one in-game hour lasts.",
                       380, self.font_sm, COLOR_TEXT_DIM)
        self._centered("Applies when a new night starts.",
                       404, self.font_sm, COLOR_TEXT_DIM)

    def _draw_pause(self):
        self._dim_screen()
        self._centered("PAUSED", 180, self.font_lg, COLOR_TEXT)
        for i, label in enumerate(["RESUME", "SETTINGS", "QUIT TO MENU"]):
            color = COLOR_ACCENT if i == self.pause_index else COLOR_TEXT
            prefix = "> " if i == self.pause_index else "   "
            self._centered(prefix + label, 290 + i * 42, self.font_md, color)

    def _draw_night_complete(self):
        self._dim_screen(200)
        self._centered("6:00 AM", 190, self.font_xl, COLOR_TEXT)
        self._centered(f"NIGHT {self.night} COMPLETE", 272, self.font_lg, COLOR_ACCENT)
        self._centered("ENTER - clock in tomorrow", 362, self.font_md, COLOR_TEXT)
        self._centered("ESC - main menu", 398, self.font_md, COLOR_TEXT_DIM)

    def _draw_game_over(self):
        self._dim_screen(215)
        self._centered("YOU DIDN'T MAKE IT", 190, self.font_lg, COLOR_DANGER)
        self._centered(self.death_cause, 252, self.font_md, COLOR_TEXT)
        self._centered("ENTER - try the night again", 352, self.font_md, COLOR_TEXT)
        self._centered("ESC - main menu", 388, self.font_md, COLOR_TEXT_DIM)

    def _dim_screen(self, alpha=170):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _centered(self, text, y, font, color=COLOR_TEXT):
        label = font.render(text, True, color)
        self.screen.blit(label, ((SCREEN_WIDTH - label.get_width()) // 2, y))
