"""Configuration values for Night Shift.

Everything tunable lives here so future systems (power drain, enemy speed,
event rates, ...) never need magic numbers scattered through the code.
"""

# --- Window ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Night Shift"

# --- Time system ---
# How many real seconds one in-game hour lasts (default; adjustable in Settings).
SECONDS_PER_GAME_HOUR = 75
GAME_HOUR_OPTIONS = (45, 60, 75, 90, 120)
HOURS_PER_NIGHT = 6  # 12 AM -> 6 AM

# --- Player ---
PLAYER_SPEED = 190  # pixels per second
PLAYER_SIZE = (24, 32)
PLAYER_COLOR = (175, 178, 190)
PLAYER_OUTLINE = (90, 92, 108)

# --- Interaction ---
INTERACT_RANGE = 60      # pixels between player centre and an object's edge
MESSAGE_DURATION = 5.0   # seconds an interaction message stays on screen

# --- Power system (all rates are % per second) ---
POWER_MAX = 100.0
POWER_BASE_DRAIN = 0.15    # always: normal office operation
POWER_CAMERA_DRAIN = 0.30  # extra while the CCTV is open
POWER_LOW = 25             # HUD warning colour below this

# --- Darkness overlay around the player (radius, alpha), drawn big -> small ---
DARKNESS_ALPHA = 205
LIGHT_STEPS = ((240, 170), (200, 120), (160, 60), (120, 0))
# When the power dies the office goes almost pitch black.
BLACKOUT_ALPHA = 235
BLACKOUT_LIGHT_STEPS = ((60, 150), (36, 0))

# --- Colours ---
COLOR_BG = (6, 6, 10)
COLOR_FLOOR = (21, 21, 29)
COLOR_WALL = (56, 56, 72)
COLOR_WALL_EDGE = (80, 80, 100)
COLOR_FURNITURE = (46, 40, 34)
COLOR_FURNITURE_EDGE = (66, 58, 48)
COLOR_DOOR = (52, 62, 58)
COLOR_TEXT = (198, 198, 210)
COLOR_TEXT_DIM = (118, 118, 134)
COLOR_ACCENT = (150, 170, 205)
COLOR_PANEL = (12, 12, 18)
COLOR_DANGER = (170, 60, 55)
