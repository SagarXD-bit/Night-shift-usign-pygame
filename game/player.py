import math

import pygame

from settings import PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLOR, PLAYER_OUTLINE


class Player:
    """The night guard. WASD / arrow keys to move, axis-separated collision."""

    def __init__(self, x, y):
        self.rect = pygame.Rect((0, 0), PLAYER_SIZE)
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED
        self.facing = (0, 1)  # last move direction, used for the eye indicator

    def update(self, dt, keys, walls):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        if dx and dy:  # normalise diagonal movement
            inv = 1.0 / math.sqrt(2.0)
            dx *= inv
            dy *= inv
        if dx or dy:
            self.facing = (dx, dy)
        self._move(dx * self.speed * dt, dy * self.speed * dt, walls)

    def _move(self, mx, my, walls):
        # Move one axis at a time so sliding along walls feels right.
        self.rect.x += round(mx)
        self._resolve(walls, mx, 0)
        self.rect.y += round(my)
        self._resolve(walls, 0, my)

    def _resolve(self, walls, mx, my):
        for wall in walls:
            if not self.rect.colliderect(wall):
                continue
            if mx > 0:
                self.rect.right = wall.left
            elif mx < 0:
                self.rect.left = wall.right
            if my > 0:
                self.rect.bottom = wall.top
            elif my < 0:
                self.rect.top = wall.bottom

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
        pygame.draw.rect(surface, PLAYER_OUTLINE, self.rect, 2)
        # Two eyes that shift toward the facing direction.
        fx, fy = self.facing
        ex = self.rect.centerx + fx * 4
        ey = self.rect.centery - 4 + fy * 4
        pygame.draw.circle(surface, PLAYER_OUTLINE, (int(ex - 4), int(ey)), 3)
        pygame.draw.circle(surface, PLAYER_OUTLINE, (int(ex + 4), int(ey)), 3)
