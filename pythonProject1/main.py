import pygame
import sys
from random import choice, randint


class Player(pygame.sprite.Sprite):
    def __init__(self):

        super().__init__()
        # Player surface imports and initialization
        player_1 = pygame.image.load('Assets/player_walk_1.png').convert_alpha()
        player_2 = pygame.image.load('Assets/player_walk_2.png').convert_alpha()
        # Used a list to store both surfaces so we can easily switch between them to animate
        self.player_walk = [player_1, player_2]
        self.player_jump = pygame.image.load('Assets/jump.png').convert_alpha()
        self.player_index = 0

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

        # Jump Sound Initialization
        self.jump_sound = pygame.mixer.Sound('Assets/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        # Jump if on the ground and space is pressed
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    # Introduce gravity into the game by using it to adjust player y position
    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        # Notice that self.rect plays the same role as player_rect in our old code
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        # If player is not on the ground, display jump animation
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        # Here we run the gravity and player input to actually make sure we behave like a player
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, types):
        super().__init__()

        # We also need to consider the type of obstacle, i.e. fly or snail
        if types == 'fly':
            fly_1 = pygame.image.load('Assets/fly.png').convert_alpha()
            fly_2 = pygame.image.load('Assets/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 200
        else:
            snail_1 = pygame.image.load('Assets/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('Assets/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]

        # Two Different paths for images but displayed at the same rectangle regardless
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        # By casting int we can essentially oscillate between 0 and 1 to animate enemies
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    # Destroy the obstacles that go too far to the left
    def destroy(self):
        if self.rect.right <= 0:
            self.kill()

    def update(self):
        self.animation_state()
        # Entity movement towards player
        self.rect.x -= 5
        self.destroy()


def display_score():
    # Ticks need to be divided by 1k to give reasonable score value and needs to be reset each iter
    current_time = (pygame.time.get_ticks() // 1000) - start_time
    score_surf = test_font.render(str(current_time), False, '#b84d69')
    score_rect = score_surf.get_rect(center=(700, 50))
    SCREEN.blit(score_surf, score_rect)
    return current_time


def sprite_collision():
    # Detect collisions between player and enemies
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        # Clears all enemies when game ends
        obstacle_group.empty()
        return False
    else:
        return True


pygame.init()

WIDTH = 800
HEIGHT = 400
TITLE = "Silly Little Game"
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
test_font = pygame.font.Font('Fonts/GUMDROP.ttf', 50)
clock = pygame.time.Clock()

# Groups
# Create single group for us to interact w/ sprites (this is perfect for just 1 player)
player = pygame.sprite.GroupSingle()
# Add instance of player class
player.add(Player())

obstacle_group = pygame.sprite.Group()

# initial Positioning
# Create surfaces which are to be displayed
sky_surface = pygame.image.load('Assets/Sky.png').convert()
ground_surface = pygame.image.load('Assets/ground.png').convert()

title_surface = test_font.render("Runner", False, '#b84d69').convert()
title_rect = title_surface.get_rect(center=(400, 50))

obstacle_rect_list = []

player_title = pygame.image.load('Assets/player_stand.png').convert_alpha()
# Rotate 0 deg and make 2x bigger
player_title = pygame.transform.rotozoom(player_title, 0, 2)
player_title_rect = player_title.get_rect(center=(400, 200))

instruction_surf = test_font.render("Press Space to Start", False, '#b84d69').convert()
instructions_rect = instruction_surf.get_rect(center=(400, 350))

start_time = 0
player_gravity = 0
run = False
score = 0
game_music = pygame.mixer.Sound('Assets/gamemusic.mp3')
# Loop music and play it forever
game_music.play(loops=-1)
# Timer to trigger events to make game more challenging
obstacle_timer = pygame.USEREVENT + 1
# Trigger Obstacle Timer every specified duration
pygame.time.set_timer(obstacle_timer, 1500)

snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer, 500)

fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)

while True:
    # Continuously runs and updates game to make it interactive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if run:
            pass
        else:
            # Reset game when player loses by pressing space again and reset score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                run = True
                start_time = pygame.time.get_ticks() // 1000

        if run:
            if event.type == obstacle_timer:
                # Input types of enemies, more can be added if we add to class
                obstacle_group.add(Obstacle(choice(["fly", "fly", "snail", "snail"])))
        else:
            pass
    # Call upon and display preinitalized surfaces
    if run:
        SCREEN.blit(sky_surface, (0, 0))
        SCREEN.blit(ground_surface, (0, 300))
        score = display_score()

        # Using the sprite group, we can easily create our players + obs by drawing it on SCREEN
        player.draw(SCREEN)
        player.update()

        obstacle_group.draw(SCREEN)
        obstacle_group.update()

        run = sprite_collision()

    else:
        # Losing Screen
        SCREEN.fill((94, 129, 162))
        # Remember move the rectangle to where you want to spawn the surface
        SCREEN.blit(title_surface, title_rect)
        SCREEN.blit(player_title, player_title_rect)
        score_message = test_font.render(f'Your score was {score}', False, '#b84d69')
        score_message_rect = score_message.get_rect(center=(400, 350))

        # When player first loads up game they'll have a score of 0 and thus instructions shown
        if score == 0:
            SCREEN.blit(instruction_surf, instructions_rect)
        else:
            SCREEN.blit(score_message, score_message_rect)
    # Updates Screen
    pygame.display.update()
    # Keeps this loop running a specified # of times / second
    clock.tick(60)
