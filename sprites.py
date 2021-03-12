#  Sprite classes for platformer
# TODO: jumping animation
from settings import *
from random import choice, randrange
import pygame as pg
vec = pg.math.Vector2  # 2d vector

class Spritesheet:
    # Utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.set_colorkey(BLACK)
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width//2, height//2))  # // --> force to int
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        # self.image = pg.Surface((30, 40))
        self.image = self.standing_frames[0]  # Start image
        # self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH / 5, WINDOW_HEIGHT - 25)
        self.pos = vec(WINDOW_WIDTH/5, WINDOW_HEIGHT - 25)  # Position vector
        self.vel = vec(0, 0)  # Velocity vector
        self.acc = vec(0, 0)  # Acceleration vector

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)  # determines fall vel
        keys = pg.key.get_pressed()
        # Manage acceleration
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # The faster you go, the more friction slows you down
        # Friction should be adjusted based on env. See settings.
        # Only friction for x direction to avoid 'steady' falling
        # Equations for motion
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        # Instead of changing the vel, I'll just stop
        # the walking animation after a certain point
        # if abs(self.vel.x) < 0.5:
        #     self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # Wrap around sides of screen
        if self.pos.x > WINDOW_WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WINDOW_WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if abs(self.vel.x) > 1.1:
            self.walking = True
        else:
            self.walking = False
        if self.jumping:
            self.image = self.jump_frame
        # Show walk animation
        elif self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # Set up idle animation
        else:
            if now - self.last_update > 300:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                # Adjust bottom to compensate for new image
                bottom = self.rect.bottom  # Current bottom
                self.image = self.standing_frames[self.current_frame]  # Update img
                self.rect = self.image.get_rect()  # Update plyr rect
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -8:
                self.vel.y = -8

    def jump(self):
        # Jump only if standing on platform
        # Check 1px below
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if hits and not self.jumping:
            self.jumping = True
            self.game.jump_sound.play()
            self.vel.y = -PLAYER_JUMP

class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        scale = randrange(50, 101) / 100
        self.rect = self.image.get_rect()
        self.rect.x = randrange(0, WINDOW_WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))



    def update(self):
        if self.rect.top > WINDOW_HEIGHT * 2:
            self.kill()

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = choice(images)
        # self.image = pg.Surface((w, h))
        # self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Powerup(self.game, self)

class Powerup(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(420, 1558, 145, 77)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx  # Center powerup at platform's center
        self.rect.bottom = self.plat.rect.top # make powerup appear on platform

    def update(self):
        if not self.game.platforms.has(self.plat):
            self.kill()
        else:
            self.rect.bottom = self.plat.rect.top - 5

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WINDOW_WIDTH + 100])  # from left or right side
        self.vx = randrange(1, 4)  # randomize speed
        if self.rect.centerx > WINDOW_WIDTH:
            self.vx *= -1
        self.rect.y = randrange(WINDOW_HEIGHT/2)
        self.vy = 0
        self.dy = 0.5  # for smooth up/down motion

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > (WINDOW_WIDTH + 100) or self.rect.right < -100:
            self.kill()
