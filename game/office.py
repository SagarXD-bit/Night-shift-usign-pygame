import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_FLOOR, COLOR_WALL, COLOR_WALL_EDGE,
    COLOR_FURNITURE, COLOR_FURNITURE_EDGE, COLOR_DOOR,
    COLOR_TEXT_DIM, COLOR_ACCENT,
)


class Interactable:
    """Something the player can inspect with E. Does not block movement."""

    def __init__(self, name, rect, description, color, prompt=None):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.description = description
        self.color = color
        self.prompt = prompt or f"Inspect {name}"

    def draw(self, surface, font, highlighted=False):
        pygame.draw.rect(surface, self.color, self.rect)
        edge = COLOR_ACCENT if highlighted else COLOR_WALL_EDGE
        pygame.draw.rect(surface, edge, self.rect, 2 if highlighted else 1)
        label = font.render(self.name, True, COLOR_TEXT_DIM)
        x = self.rect.centerx - label.get_width() // 2
        x = max(4, min(x, SCREEN_WIDTH - label.get_width() - 4))  # keep on screen
        surface.blit(label, (x, self.rect.bottom + 3))


class Office:
    """The security office: walls (collision), furniture, and interactables."""

    WALL_T = 20

    def __init__(self):
        t = self.WALL_T
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        self.outer_walls = [
            pygame.Rect(0, 0, w, t),      # top
            pygame.Rect(0, h - t, w, t),  # bottom
            pygame.Rect(0, 0, t, h),      # left
            pygame.Rect(w - t, 0, t, h),  # right
        ]
        self.furniture = [
            pygame.Rect(290, 96, 220, 46),   # front desk
            pygame.Rect(620, 380, 92, 60),   # radio table
            pygame.Rect(70, 470, 150, 42),   # supply shelf
        ]
        # Everything the player can collide with.
        self.walls = self.outer_walls + self.furniture

        self.door_visuals = [
            pygame.Rect(0, 250, t, 110),        # left door
            pygame.Rect(w - t, 320, t, 110),    # right door
        ]

        self.interactables = [
            Interactable(
                "Computer", (372, 100, 56, 36),
                "The security computer hums quietly.",  # unused: E opens the CCTV
                (62, 76, 92),
                prompt="Use Computer (security cameras)",
            ),
            Interactable(
                "Wall Clock", (470, 22, 34, 30),
                "",  # filled in dynamically by Game
                (150, 150, 160),
            ),
            Interactable(
                "Radio", (640, 388, 50, 36),
                "An old shortwave radio. It's switched off, but the power "
                "light glows faintly.",
                (86, 68, 52),
            ),
            Interactable(
                "Electrical Panel", (w - 24, 140, 22, 68),
                "Breakers for the whole building. Everything reads normal, "
                "except the meter is running a little fast.",
                (96, 90, 60),
            ),
            Interactable(
                "Left Door", (0, 250, 26, 110),
                "A heavy fire door. The lock motor clicks when you touch the "
                "handle, but the controls aren't wired up yet.",
                COLOR_DOOR,
            ),
            Interactable(
                "Right Door", (w - 22, 320, 22, 110),
                "Same heavy door as the left. Through the little window you "
                "only see darkness.",
                COLOR_DOOR,
            ),
            Interactable(
                "Supply Shelf", (70, 470, 150, 42),
                "Boxes of old employee files. One is labelled '1983 - DO NOT "
                "SHRED'. You decide not to open it tonight.",
                (70, 60, 46),
            ),
        ]

    def draw(self, surface, font, highlighted=None):
        t = self.WALL_T
        pygame.draw.rect(surface, COLOR_FLOOR,
                         (t, t, SCREEN_WIDTH - 2 * t, SCREEN_HEIGHT - 2 * t))
        for wall in self.outer_walls:
            pygame.draw.rect(surface, COLOR_WALL, wall)
            pygame.draw.rect(surface, COLOR_WALL_EDGE, wall, 1)
        for door in self.door_visuals:
            pygame.draw.rect(surface, COLOR_DOOR, door)
            pygame.draw.rect(surface, COLOR_WALL_EDGE, door, 1)
        for block in self.furniture:
            pygame.draw.rect(surface, COLOR_FURNITURE, block)
            pygame.draw.rect(surface, COLOR_FURNITURE_EDGE, block, 1)
        for item in self.interactables:
            item.draw(surface, font, item is highlighted)
