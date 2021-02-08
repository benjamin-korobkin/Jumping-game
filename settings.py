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
PLAYER_JUMP = 19

# starting platforms. (First is ground)
PLATFORM_LIST = [(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40),
                 (WINDOW_WIDTH/2 - 50, WINDOW_HEIGHT * 3/4, 100, 20),
                 (125, WINDOW_HEIGHT - 300, 100, 20),
                 (350, 200, 100, 20),
                 (175, 100, 50, 15)]

# Images and colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE