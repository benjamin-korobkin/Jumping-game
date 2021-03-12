# Pygame Settings
TITLE = "JUMPY!"
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "Highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player Properties
PLAYER_ACC = 0.5  # Acceleration
# Ground friction. For ice or sand, you would decrease/increase it
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.6
PLAYER_JUMP = 18

# Powerup settings
BOOST_POWER = 60
POW_SPAWN_PCT = 7
# Mob settings
MOB_FREQ = 5000
# Layers
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0
# starting platforms (aside from ground)
PLATFORM_LIST = [(WINDOW_WIDTH/2 - 50, WINDOW_HEIGHT * 3/4),
                 (125, WINDOW_HEIGHT - 300),
                 (350, 200), (175, 100)]

# Images and colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHTBLUE = (98, 180, 207)
BROWN = (139, 69, 19)
BGCOLOR = LIGHTBLUE