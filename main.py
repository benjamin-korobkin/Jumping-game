# Jumpy! - platform game
# Music: Caketown by Matthew Pablo
#   - Somewhere in the Elevator by Peachtea@You're Perfect Studio
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        # Initialize game window, etc.
        pg.init()
        pg.mixer.init()  # Sound control
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        try:
            with open(path.join(self.dir, HS_FILE), 'r+') as f:
                self.highscore = int(f.read())
        except:
            with open(path.join(self.dir, HS_FILE), 'w'):
                self.highscore = 0

        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # load clouds
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud' + str(i) + '.png')).convert())

        # load audio
        self.sound_dir = path.join(self.dir, 'sound')
        # Keep this sound, but not for this game
        self.jump_sound = pg.mixer.Sound(path.join(self.sound_dir, 'jump3.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.sound_dir, 'boost.wav'))

    def new(self):
        # Start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.mob_timer = 0  # To track when mobs spawn
        ground = Platform(self, 0, WINDOW_HEIGHT-60)
        ground.image = pg.Surface((WINDOW_WIDTH, 60))
        ground.image.fill(GREEN)
        ground.rect = ground.image.get_rect()
        ground.rect.x = 0
        ground.rect.y = WINDOW_HEIGHT - 60
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)  # Python shortcut to 'explode' a list.
        pg.mixer.music.load(path.join(self.sound_dir, 'Caketown.ogg'))
        for i in range(10):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(700)

    def update(self):
        # Game loop - update
        self.all_sprites.update()

        # Spawn a mob?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, 0, 1000]):
            self.mob_timer = now
            Mob(self)
        # hit mob
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, True, pg.sprite.collide_mask)
        if mob_hits:
            self.playing = False
            # TODO: make plyr jump if we land on top of mob

        # Check if player hits platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                # When we touch multiple plats, try to get to the lower one
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                # Make sure the bottom of the player goes above the bottom of the plat
                if self.player.pos.x < lowest.rect.right + 10 and \
                    self.player.pos.x > lowest.rect.left - 10:
                    if self.player.rect.bottom < lowest.rect.bottom:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False
        # When plyr reaches top 1/4 of screen
        if self.player.rect.top <= WINDOW_HEIGHT / 4 and self.player.vel.y < 0:
            if random.randrange(80) < 2:
                Cloud(self)
            self.player.pos.y += abs(self.player.vel.y)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top > WINDOW_HEIGHT:
                    plat.kill()
                    self.score += 10


        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, False)
        for pow in pow_hits:
            if pow.type == 'boost' and self.player.vel.y > 0:
                self.boost_sound.play()
                self.player.vel.y -= BOOST_POWER
                self.player.jumping = False
        # DIE!
        if self.player.rect.bottom > WINDOW_HEIGHT:
            for sprite in self.all_sprites:
                # Make other platforms fall
                sprite.rect.y -= max(self.player.vel.y, 10)  # But not too quickly...
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # Spawn new platforms to keep some average number
        while (len(self.platforms)) < 6:
            width = random.randrange(52, 100)
            Platform(self, random.randrange(20, WINDOW_WIDTH - 20 - width),
                         random.randrange(-50, -35))

    def events(self):
        # Game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    self.player.jump_cut()

    def draw(self):
        # Game loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WINDOW_WIDTH / 2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()  # This means show everything to the player

    def show_start_screen(self):
        # game splash/start scrn
        pg.mixer.music.load(path.join(self.sound_dir, 'Peachtea-Elevator.ogg'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 40, WHITE, WINDOW_WIDTH/2, WINDOW_HEIGHT/4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.draw_text("Press any key to play", 22, WHITE, WINDOW_WIDTH/2, WINDOW_HEIGHT*3/4)
        self.draw_text("HIGH SCORE: " + str(self.highscore), 22, WHITE, WINDOW_WIDTH/2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(300)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.sound_dir, 'Peachtea-Elevator.ogg'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 40, WHITE, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.draw_text("Press any key to play again", 22, WHITE, WINDOW_WIDTH / 2, WINDOW_HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WINDOW_WIDTH/2, 15)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.highscore))
        else:
            self.draw_text("High score is still " + str(self.highscore), 22, WHITE, WINDOW_WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(300)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()