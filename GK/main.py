import pygame, math, random
from pygame.locals import *
from PIL import Image

# Initialise Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Game")

# Function to check overlap
def is_overlapping(new_rect, others):
    for rect in others:
        if new_rect.colliderect(rect):
            return True
    return False

class Enemy:
    def __init__(self, file, x, y, width, height, wait):
        self.wait = wait
        self.x = x
        self.y = y
        self.yspeed = 1
        self.timeout = True
        self.xspeed = 0
        self.width = width
        self.height = height
        self.image = pygame.image.load(f"{file}")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.shooting_cooldown = random.randint(175, 200) # Random delay for shooting
        self.shooting_timer = self.shooting_cooldown  # Timer to track the delay
        self.missile_fired = False  # Track if a missile is already fired

    def update(self):
        self.y += self.yspeed
        self.x += self.xspeed
        if self.y > HEIGHT:
            self.y = - self.height
            self.x = 30 + random.random() * (WIDTH - self.width)
            self.timeout = True

        # Enemy shooting mechanism
        if not self.missile_fired:
            self.shooting_timer -= 1
            if self.shooting_timer <= 0 and 0 <= self.x <= 800 and 0 <= self.y <= 800:
                # Fire a missile from the TIE fighter's position
                missile_y = self.y + self.height - 40
                enemy_missiles.append([self.x + self.width // 2, missile_y])  # Start missile just below TIE fighter
                blaster_effect2.play()  # Play the enemy shooting sound
                self.missile_fired = True
                self.shooting_timer = self.shooting_cooldown  # Reset shooting timer to random cooldown

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def check_collision(self, missile):
        missile_centre_x = missile[0] + 0.5
        missile_centre_y = missile[1] + 10

        if (self.x < missile_centre_x < self.x + self.width and
            self.y < missile_centre_y < self.y + self.height):
            
            explosions.append([self.x, self.y, 0, 0])
            # Try new position until no overlap
            while True:
                new_x = 30 + random.random() * (WIDTH - self.width - 30)
                new_rect = pygame.Rect(new_x, -200, self.width, self.height)
                others = [pygame.Rect(e.x, e.y, e.width, e.height) for e in enemy_list if e != self]
                if not is_overlapping(new_rect, others):
                    self.x = new_x
                    self.y = -200
                    break

            self.missile_fired = False
            return True
        return False


    def check_player_collision(self):
        global spaceship_invincible, flash_timer, lives
        if not spaceship_invincible:
            if (spaceship_x + 25 > self.x and
                spaceship_x + 25 < self.x + self.width and
                spaceship_y + 25 > self.y and
                spaceship_y + 25 < self.y + self.height):
                
                explosions.append([self.x, self.y, 0, 0])
                # Try new position until no overlap
                while True:
                    new_x = 30 + random.random() * (WIDTH - self.width - 30)
                    new_rect = pygame.Rect(new_x, -200, self.width, self.height)
                    others = [pygame.Rect(e.x, e.y, e.width, e.height) for e in enemy_list if e != self]
                    if not is_overlapping(new_rect, others):
                        self.x = new_x
                        self.y = -200
                        break
                
                spaceship_invincible = True
                flash_timer = 50
                lives -= 1

# Function to create enemies without overlap
enemy_rects = []

def create_enemy(file, width, height, wait):
    while True:
        x = random.uniform(0, WIDTH - width)
        y = -100
        new_rect = pygame.Rect(x, y, width, height)
        if not is_overlapping(new_rect, enemy_rects):
            enemy_rects.append(new_rect)
            return Enemy(file, x, y, width, height, wait)

# Create instances of enemies
enemy1 = create_enemy("images/tiefighter1.png", 162, 105, 200)
enemy2 = create_enemy("images/tiefighter2.png", 162, 105, 400)
enemy3 = create_enemy("images/tiefighter3.png", 126, 110, 600)

enemy_list = [enemy1, enemy2, enemy3]

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTSABER_RED = (255, 33, 46)
LIGHTSABER_GREEN = (144, 238, 144)

# Load starting images and button
title_img = pygame.image.load("images/starwarslogo.png")
title_img = pygame.transform.scale(title_img, (600, 270))

# Load spaceship image
spaceship_img = pygame.image.load("images/milleniumfalcon.png")
spaceship_img = pygame.transform.scale(spaceship_img, (100, 100))

# Load background image
background_image = pygame.image.load("images/background.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load hearts
heart_image = pygame.image.load("images/heart.png")
heart_image = pygame.transform.scale(heart_image, (50, 50))

# Load pause button image
pause_button_img = pygame.image.load("images/pausebutton.png")
pause_button_img = pygame.transform.scale(pause_button_img, (25, 25))
pause_button_rect = pause_button_img.get_rect(topleft=(743, 15))

# Load sound effects
star_wars_theme = pygame.mixer.music.load("sound/starwarstheme.mp3")
blaster_effect1 = pygame.mixer.Sound("sound/blastereffect1.mp3")
blaster_effect1.set_volume(0.3)
blaster_effect2 = pygame.mixer.Sound("sound/blastereffect2.mp3")
blaster_effect2.set_volume(0.9)
explosion_effect = pygame.mixer.Sound("sound/explosion.mp3")
explosion_effect.set_volume(0.5)
death_effect = pygame.mixer.Sound("sound/deathsound.mp3")

# Load GIFs
def load_gif_frames(gif_path):
    frames = []
    pil_gif = Image.open(gif_path)
    try:
        while True:
            frame = pil_gif.convert("RGBA")
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)
            pil_gif.seek(pil_gif.tell() + 1)
    except EOFError:
        pass
    return frames

gif_frames = load_gif_frames("images/intro.gif")

# Play starting gif
def play_starting_gif(frames):
    pygame.mixer.music.play(-1)
    for frame in frames:
        screen.fill(BLACK)
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

# Spaceship starting pos
spaceship_x, spaceship_y = WIDTH // 2, HEIGHT // 2
spaceship_speed = 7

# Missile settings
missiles = []
MISSILE_SPEED = 5
enemy_missiles = []
ENEMY_MISSILE_SPEED = 5
explosions = []

# Calculate how far to move the spaceship
def calculate_move_vector(x_mouse,y_mouse):
    xlength = spaceship_x +25 - x_mouse
    ylength = spaceship_y +25 - y_mouse
    distance = math.sqrt(xlength * xlength + ylength * ylength) / 30

    angle = math.atan2(ylength, xlength)

    xdistance = distance * math.cos(angle)
    ydistance = distance * math.sin(angle)

    return spaceship_x - xdistance, spaceship_y - ydistance

# Start Menu Code
def start_menu():
    menu_running = True
    font = pygame.font.SysFont(None, 40)
    button_rect = pygame.Rect(324, 525, 150, 50)
    pulse_timer = 0

    while menu_running:
        screen.fill(BLACK)
        screen.blit(title_img, (WIDTH - 700, HEIGHT - 550))
        pygame.draw.rect(screen, (0, 0, 0), button_rect)

        # Pulsing effect
        pulse_timer += 1
        scale = 1 + 0.1 * math.sin(pulse_timer * 0.1)
        text_surface = font.render("START", True, (255, 255, 255))
        text_width = int(text_surface.get_width() * scale)
        text_height = int(text_surface.get_height() * scale)
        scaled_text = pygame.transform.scale(text_surface, (text_width, text_height))

        # Center the text in the button
        text_x = button_rect.x + (button_rect.width - text_width) // 2
        text_y = button_rect.y + (button_rect.height - text_height) // 2
        screen.blit(scaled_text, (text_x, text_y))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    play_starting_gif(gif_frames)
                    menu_running = False

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    play_starting_gif(gif_frames)
                    menu_running = False

        pygame.display.flip()
        clock.tick(60)

# Start of game
running = True
clock = pygame.time.Clock()
start_menu()

score = 0
font = pygame.font.Font(None, 36)
spaceship_invincible = False
flash_timer = 0
paused = False
lives = 3
game_over = False
explosion_frames = load_gif_frames("images/explosion.gif")

while running:
    screen.blit(background_image, (0,0))

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Fire missiles on spacebar press or mouse click
        if event.type == KEYDOWN:
            if event.key == K_SPACE and not paused:
                missiles.append([spaceship_x + 50.25, spaceship_y])
                blaster_effect1.play()
            
        elif event.type == MOUSEBUTTONDOWN and not paused:
            missiles.append([spaceship_x + 50.25, spaceship_y])
            blaster_effect1.play()
        
        # Check if paused button is clicked
        if not game_over:
            if event.type == MOUSEBUTTONDOWN:
                if pause_button_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            
    # Get key states
    if not paused:
        keys = pygame.key.get_pressed()
        
        # Get mouse posistion
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update spaceship posistion based on mouse posistion
        spaceship_x, spaceship_y = calculate_move_vector(mouse_x, mouse_y)

        # Ensure spaceship stays within screen bounds
        if spaceship_x < 0:
            spaceship_x = 0
        elif spaceship_x > WIDTH - spaceship_img.get_width():
            spaceship_x = WIDTH - spaceship_img.get_width()

        if spaceship_y < 0:
            spaceship_y = 0
        elif spaceship_y > HEIGHT - spaceship_img.get_height():
            spaceship_y = HEIGHT - spaceship_img.get_height()

        # Update enemies
        if enemy1.timeout==False:
            enemy1.update()
        else:
            enemy1.wait -= 1
            if enemy1.wait == 0:
                enemy1.timeout = False
                enemy1.wait = random.randint(1,200)
                enemy1.yspeed = 1
        
        if enemy2.timeout==False:
            enemy2.update()
        else:
            enemy2.wait -= 1
            if enemy2.wait == 0:
                enemy2.timeout = False
                enemy2.wait = random.randint(1,200)
                enemy2.yspeed = 1

        if enemy3.timeout==False:
            enemy3.update()
        else:
            enemy3.wait -= 1
            if enemy3.wait == 0:
                enemy3.timeout = False
                enemy3.wait = random.randint(1,200)
                enemy3.yspeed = 1

        # Enemy missile behavior
        for missile in enemy_missiles:
            missile[1] += ENEMY_MISSILE_SPEED  # Move missile downwards
            pygame.draw.rect(screen, LIGHTSABER_RED, (missile[0], missile[1], 2, 20))  # Draw the missile

            # Check if the missile hits the player by checking if it intersects the player's hitbox
            missile_rect = pygame.Rect(missile[0], missile[1], 5, 15)  # Create a rectangle for the missile
            spaceship_rect = pygame.Rect(spaceship_x, spaceship_y, spaceship_img.get_width(), spaceship_img.get_height())  # Player spaceship rectangle

            if missile_rect.colliderect(spaceship_rect):  # Check if the missile collides with the spaceship
                enemy_missiles.remove(missile)  # Remove missile if it hits player
                lives -= 1
                # Reset spaceship invincibility
                spaceship_invincible = True
                flash_timer = 50

        # Update missile posistions
        for missile in missiles:
            if enemy1.check_collision(missile): # if true we have hit a missile
                explosion_effect.play()
                missiles.remove(missile) # Remove the missile
                score += 10 # Increment the score
            if enemy2.check_collision(missile):
                explosion_effect.play()
                missiles.remove(missile)
                score += 10
            if enemy3.check_collision(missile):
                explosion_effect.play()
                missiles.remove(missile)
                score += 20
            missile[1] -= MISSILE_SPEED
            pygame.draw.rect(screen, LIGHTSABER_GREEN, (missile[0], missile[1], 1.5, 18))

        # Remove missiles that leave the screen
        new_missiles = []
        for missile in missiles:
            hit = False
            for enemy in enemy_list:
                if enemy.check_collision(missile):
                    explosion_effect.play()
                    score += 10 if enemy != enemy3 else 20
                    hit = True
                    break
            if not hit:
                missile[1] -= MISSILE_SPEED
                pygame.draw.rect(screen, LIGHTSABER_GREEN, (missile[0], missile[1], 1.5, 18))
                if missile[1] > 0:
                    new_missiles.append(missile)
        missiles = new_missiles

        # Check for collisions between the player and enemies
        enemy1.check_player_collision()
        enemy2.check_player_collision()
        enemy3.check_player_collision()

        # Check if more than 3 lives are lost
        if lives <= 0:
            game_over = True

    # Handle spaceship flasing and invincibility
    if paused:
        spaceship_invincible = False

    if not game_over:
        if spaceship_invincible:
            flash_timer -= 1
            if flash_timer % 10 < 5:
                screen.blit(spaceship_img, (spaceship_x, spaceship_y))
            if flash_timer <= 0:
                spaceship_invincible = False  # End invincibility
        else:
            screen.blit(spaceship_img, (spaceship_x, spaceship_y))

    # Draw the score at the top=left corner
    score_text = font.render(f"SCORE: {score}", False, WHITE)
    screen.blit(score_text, (20, 20))

    # Draw PAUSE button
    screen.blit(pause_button_img, pause_button_rect)
    
    # Draw lives at the top of the screen
    for i in range(lives):
        screen.blit(heart_image, (340 + i * 44, 10))

    # Always draw enemies even when paused / game over
    enemy1.draw()
    enemy2.draw()
    enemy3.draw()

    # Always draw missiles when paused or game over
    for enemy_missile in enemy_missiles:
        pygame.draw.rect(screen, LIGHTSABER_RED, (enemy_missile[0], enemy_missile[1], 2, 20))
    for missile in missiles:
        pygame.draw.rect(screen, LIGHTSABER_GREEN, (missile[0], missile[1], 1.5, 18))

    # Draw explosion animations from GIF frames
    for explosion in explosions[:]:
        x, y, frame_index, frame_timer = explosion
        if frame_index < len(explosion_frames):
            frame_img = pygame.transform.scale(explosion_frames[frame_index], (100, 100))
            screen.blit(frame_img, (x + 20, y))
            explosion[3] += 1  # Increase frame timer
            if explosion[3] >= 3:  # Show each frame for 3 ticks (increase for slower speed)
                explosion[3] = 0
                explosion[2] += 1  # Advance to next frame
        else:
            explosions.remove(explosion)

    # Draw "PAUSED" label when paused
    if paused and not game_over:
        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    # Display final explosion first, then Game Over text, reset all variables
    if game_over:
        death_effect.play()
        paused = True
        pygame.mixer.music.pause()
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))    
        pygame.display.flip()
        pygame.time.delay(3500)  # Wait 3.5 seconds
        # Reset game states
        spaceship_x, spaceship_y = WIDTH // 2, HEIGHT // 2
        missiles.clear()
        enemy_missiles.clear()
        explosions.clear()
        lives = 3
        score = 0
        spaceship_invincible = False
        flash_timer = 0
        paused = False
        game_over = False
        for enemy in enemy_list:
            enemy.missile_fired = False
            enemy.timeout = True
            enemy.wait = random.randint(100, 300)
            enemy.y = -200
            enemy.x = 30 + random.random() * (WIDTH - enemy.width - 30)
        start_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()