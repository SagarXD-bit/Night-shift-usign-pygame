"""Security camera system (v0.2).

Six cameras covering six rooms, each drawn as a grainy surveillance feed.
Room layouts are pure data so later versions can easily add enemies, moving
props, glitches, camera failures and fake footage without touching the
rendering code.
"""

import random

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# CCTV palette -- deliberately unlike the office palette, so the interface
# feels like a different machine.
CCTV_BG = (8, 12, 9)
CCTV_FLOOR = (26, 34, 27)
CCTV_PROP = (44, 54, 45)
CCTV_PROP_EDGE = (70, 84, 70)
CCTV_TEXT = (150, 190, 150)
CCTV_TEXT_DIM = (90, 120, 90)
CCTV_FRAME = (38, 48, 39)
CCTV_REC = (200, 60, 50)

# Area of the screen the room itself is drawn in.
VIEW = pygame.Rect(60, 90, 680, 390)

SWITCH_FLASH_TIME = 0.18  # seconds of heavy static after changing camera

# Props are ("rect", (x, y, w, h), label) or ("circle", (x, y, r), label).
CAMERA_DEFS = [
    {
        "id": 1, "name": "RECEPTION",
        "props": [
            ("rect", (300, 150, 200, 50), "FRONT DESK"),
            ("circle", (250, 260, 18), "CHAIR"),
            ("circle", (330, 260, 18), "CHAIR"),
            ("rect", (520, 140, 40, 40), "PLANT"),
            ("rect", (140, 380, 160, 30), "BENCH"),
        ],
    },
    {
        "id": 2, "name": "MAIN HALL",
        "props": [
            ("rect", (90, 230, 60, 120), "VENDING"),
            ("rect", (360, 300, 140, 30), "BENCH"),
            ("rect", (640, 100, 30, 80), "DOOR N."),
            ("rect", (640, 390, 30, 80), "DOOR S."),
        ],
    },
    {
        "id": 3, "name": "STORAGE",
        "props": [
            ("rect", (120, 130, 80, 60), "BOXES"),
            ("rect", (220, 130, 80, 60), "BOXES"),
            ("rect", (120, 210, 80, 60), "BOXES"),
            ("rect", (430, 150, 100, 90), "SHELF"),
            ("rect", (430, 270, 100, 90), "SHELF"),
            ("rect", (600, 340, 70, 70), "CRATE"),
        ],
    },
    {
        "id": 4, "name": "BACK HALL EAST",
        "props": [
            ("rect", (150, 110, 300, 26), "LOCKERS"),
            ("rect", (520, 380, 70, 60), "CRATE"),
            ("rect", (90, 300, 40, 100), "DOOR W."),
        ],
    },
    {
        "id": 5, "name": "ELECTRICAL",
        "props": [
            ("rect", (300, 170, 45, 110), "GENERATOR"),
            ("rect", (120, 120, 40, 140), "PANELS"),
            ("rect", (180, 120, 40, 140), "PANELS"),
            ("rect", (560, 130, 80, 40), "DANGER"),
        ],
    },
    {
        "id": 6, "name": "BASEMENT",
        "props": [
            ("rect", (60, 96, 680, 14), "PIPES"),
            ("rect", (60, 122, 680, 10), "PIPES"),
            ("circle", (220, 300, 55), "BOILER"),
            ("rect", (520, 320, 90, 70), "BOXES"),
            ("rect", (640, 150, 60, 90), "???"),
        ],
    },
]


class CameraSystem:
    """The CCTV interface opened from the office computer."""

    def __init__(self):
        self.is_open = False
        self.index = 0
        self.flash = 0.0   # burst of heavy static right after switching
        self._blink = 0.0  # drives the blinking REC dot
        self._scanlines = None  # built once, reused every frame

    # ---------------------------------------------------------------- state

    def open(self):
        self.is_open = True
        self.flash = SWITCH_FLASH_TIME

    def close(self):
        self.is_open = False

    @property
    def current(self):
        return CAMERA_DEFS[self.index]

    def handle_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_e, pygame.K_TAB):
            self.close()
            return
        new_index = self.index
        if pygame.K_1 <= key <= pygame.K_6:
            new_index = key - pygame.K_1
        elif key in (pygame.K_LEFT, pygame.K_a):
            new_index = (self.index - 1) % len(CAMERA_DEFS)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            new_index = (self.index + 1) % len(CAMERA_DEFS)
        if new_index != self.index:
            self.index = new_index
            self.flash = SWITCH_FLASH_TIME

    def update(self, dt):
        if self.flash > 0:
            self.flash -= dt
        self._blink += dt

    # ------------------------------------------------------------------ draw

    def draw(self, surface, font_sm, font_md, time_text):
        surface.fill(CCTV_BG)
        cam = self.current
        self._draw_room(surface, cam, font_sm)
        self._draw_noise(surface)
        self._draw_scanlines(surface)
        self._draw_frame(surface, cam, font_sm, font_md, time_text)

    def _draw_room(self, surface, cam, font):
        pygame.draw.rect(surface, CCTV_FLOOR, VIEW)
        for shape, data, label in cam["props"]:
            if shape == "rect":
                rect = pygame.Rect(data)
                pygame.draw.rect(surface, CCTV_PROP, rect)
                pygame.draw.rect(surface, CCTV_PROP_EDGE, rect, 1)
                lx, ly = rect.centerx, rect.bottom + 4
            else:
                pygame.draw.circle(surface, CCTV_PROP, data[:2], data[2])
                pygame.draw.circle(surface, CCTV_PROP_EDGE, data[:2], data[2], 1)
                lx, ly = data[0], data[1] + data[2] + 4
            text = font.render(label, True, CCTV_TEXT_DIM)
            surface.blit(text, (lx - text.get_width() // 2, ly))

    def _draw_noise(self, surface):
        density = 900 if self.flash > 0 else 250
        for _ in range(density):
            x = random.randint(VIEW.left, VIEW.right - 1)
            y = random.randint(VIEW.top, VIEW.bottom - 1)
            shade = random.randint(40, 140)
            surface.set_at((x, y), (shade, shade + 10, shade))

    def _draw_scanlines(self, surface):
        if self._scanlines is None:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for y in range(0, SCREEN_HEIGHT, 3):
                pygame.draw.line(s, (0, 0, 0, 60), (0, y), (SCREEN_WIDTH, y))
            self._scanlines = s
        surface.blit(self._scanlines, (0, 0))

    def _draw_frame(self, surface, cam, font_sm, font_md, time_text):
        # Header: camera id/name, current game time, blinking REC dot.
        title = font_md.render(f"CAM {cam['id']:02d} // {cam['name']}", True, CCTV_TEXT)
        surface.blit(title, (VIEW.left, 40))
        clock = font_md.render(time_text, True, CCTV_TEXT)
        surface.blit(clock, (VIEW.right - clock.get_width(), 40))
        if self._blink % 1.0 < 0.6:
            pygame.draw.circle(surface, CCTV_REC, (VIEW.left + 8, 70), 5)
            rec = font_sm.render("REC", True, CCTV_REC)
            surface.blit(rec, (VIEW.left + 20, 62))

        pygame.draw.rect(surface, CCTV_FRAME, VIEW, 2)

        # Footer: camera selector buttons + controls help.
        y = 510
        x = VIEW.left
        for i, c in enumerate(CAMERA_DEFS):
            text = font_sm.render(f" {c['id']} ", True,
                                  CCTV_BG if i == self.index else CCTV_TEXT)
            box = pygame.Rect(x, y, text.get_width() + 10, 26)
            pygame.draw.rect(surface, CCTV_TEXT if i == self.index else CCTV_FRAME, box)
            pygame.draw.rect(surface, CCTV_FRAME, box, 1)
            surface.blit(text, (x + 5, y + 5))
            x += box.width + 8
        help_text = font_sm.render("1-6 select    <-/-> cycle    E / ESC close",
                                   True, CCTV_TEXT_DIM)
        surface.blit(help_text, (VIEW.right - help_text.get_width(), y + 4))
