import logging
import os
import pygame
import sys
import random
import math
from player import Player
from enemy import RedEnemy, YellowEnemy, GreenEnemy
from game_logger_setup import game_logger

# Set up global logger
logger = game_logger("game")

# Define the path to your logs folder
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Set up a file handler for logging to a file
log_file_path = os.path.join(log_folder, "game.log")
file_handler = logging.FileHandler(log_file_path)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.info("Logger has been set up.")

# Initialize Pygame
pygame.init()

# Set up display
width, height = 300, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Enhanced Game")

# Set up colors
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# Set up player
player_size = 50
player_speed = 300
player = Player(width // 2, height - 100, player_size, player_speed, width)
logger.info(f"Player object created with attributes: {vars(player)}")

# Set up enemies
enemy_size = 50
enemies = [
    RedEnemy(random.randint(0, width - enemy_size), 0, enemy_size, width, height)
]

# Set up score
score = 0
font = pygame.font.SysFont(None, 35)

# High Score File
highscore_file = "highscore.txt"

# Load the high score
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as file:
        try:
            high_score = int(file.read())
        except ValueError:
            high_score = 0
else:
    high_score = 0

# Set up clock
clock = pygame.time.Clock()
fps = 60

# Splash Text Variables
new_high_score_achieved = False
splash_start_time = None
splash_duration = 4000  # 4 seconds in milliseconds
slow_motion_active = False
high_score_updated_this_game = False
milestone_reached = False
new_high_score_splash_shown = False  # Indicates if high score splash has been shown this session

enemy_spawn_lock = {
    'RedEnemy': False,
    'YellowEnemy': False,
    'GreenEnemy': False
}

milestones = [10, 25, 50, 100, 250, 500, 1000]

# Function to calculate distance between two positions
def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

# Anti-magnetic field: Apply separation between enemies
def apply_separation(enemies, min_distance):
    for i, enemy1 in enumerate(enemies):
        for j, enemy2 in enumerate(enemies):
            if i != j:
                dist = distance(enemy1.pos, enemy2.pos)
                if dist < min_distance:
                    dx = enemy2.pos[0] - enemy1.pos[0]
                    dy = enemy2.pos[1] - enemy1.pos[1]
                    if dx == 0 and dy == 0:
                        dx, dy = random.choice([-1, 1]), random.choice([-1, 1])
                    else:
                        norm = math.sqrt(dx ** 2 + dy ** 2)
                        dx /= norm
                        dy /= norm
                    # Adjust enemy position to maintain the distance
                    enemy2.pos[0] += dx * (min_distance - dist)
                    enemy2.pos[1] += dy * (min_distance - dist)

# Function to detect collision using masks
def detect_collision(player, enemy):
    offset_x = int(enemy.pos[0] - player.pos[0])
    offset_y = int(enemy.pos[1] - player.pos[1])
    overlap = player.mask.overlap(enemy.mask, (offset_x, offset_y))
    return overlap is not None

# Function to display text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Function to apply a simple blur effect
def apply_blur_effect(screen):
    small_surface = pygame.transform.scale(screen, (width // 2, height // 2))
    blurred_surface = pygame.transform.scale(small_surface, (width, height))
    screen.blit(blurred_surface, (0, 0))

# Game loop
running = True
game_active = False
paused = False

while running:
    try:
        if slow_motion_active:
            dt = clock.tick(fps) / 1000 * 0.25  # Slow motion at 1/4 speed
        else:
            dt = clock.tick(fps) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    logger.info("Enter key pressed - Starting game!")
                    game_active = True
                    paused = False
                    score = 0
                    player = Player(width // 2, height - 100, player_size, player_speed, width)
                    logger.info(f"Player object re-created with attributes: {vars(player)}")
                    enemies = [
                        RedEnemy(random.randint(0, width - enemy_size), 0, enemy_size, width, height)
                    ]
                    new_high_score_achieved = False
                    high_score_updated_this_game = False
                    milestone_reached = False
                    new_high_score_splash_shown = False
                    splash_start_time = None
                    slow_motion_active = False
                    # Reset enemy spawn lock
                    enemy_spawn_lock = {'RedEnemy': False, 'YellowEnemy': False, 'GreenEnemy': False}
                if event.key == pygame.K_p:
                    paused = not paused
                    logger.info(f"Paused: {paused}")

            player.handle_event(event)

        if game_active and not paused:
            # Move player
            player.move(dt)

            # Update all enemies
            for enemy in enemies:
                if enemy.move(dt):
                    score += 1
                    logger.info(f"Score updated: {score}")

                    # Trigger milestones
                    if score in milestones and not milestone_reached:
                        milestone_reached = True
                        splash_start_time = pygame.time.get_ticks()
                        slow_motion_active = True
                        logger.info(f"Milestone achieved: {score} points! Entering slow motion mode.")

            # Apply separation rule to enemies
            apply_separation(enemies, min_distance=enemy_size * 1.5)

            # Dynamically add enemies based on the new logic
            if score >= 3 and not enemy_spawn_lock['RedEnemy']:
                new_enemy = RedEnemy(random.randint(0, width - enemy_size), 0, enemy_size, width, height)
                enemies.append(new_enemy)
                enemy_spawn_lock['RedEnemy'] = True
                logger.info(f"New RedEnemy added! Total enemies: {len(enemies)}")

            if score >= 9 and not enemy_spawn_lock['YellowEnemy']:
                new_enemy = YellowEnemy(random.randint(0, width - enemy_size), 0, enemy_size, width, height)
                enemies.append(new_enemy)
                enemy_spawn_lock['YellowEnemy'] = True
                logger.info(f"New YellowEnemy added! Total enemies: {len(enemies)}")

            if score >= 18 and not enemy_spawn_lock['GreenEnemy']:
                new_enemy = GreenEnemy(random.randint(0, width - enemy_size), 0, enemy_size, width, height)
                enemies.append(new_enemy)
                enemy_spawn_lock['GreenEnemy'] = True
                logger.info(f"New GreenEnemy added! Total enemies: {len(enemies)}")

            # Check for collisions
            for enemy in enemies:
                if detect_collision(player, enemy):
                    logger.info("Collision detected - Game over!")
                    game_active = False
                    # Update high score if the current score is greater
                    if score > high_score:
                        high_score = score
                        with open(highscore_file, "w") as file:
                            file.write(str(high_score))
                        logger.info(f"New high score achieved: {high_score}")
                        high_score_updated_this_game = True

            # Trigger new high score splash effect once
            if score > high_score and not new_high_score_splash_shown and not high_score_updated_this_game:
                new_high_score_achieved = True
                new_high_score_splash_shown = True
                splash_start_time = pygame.time.get_ticks()
                slow_motion_active = True
                logger.info("New high score surpassed! Entering slow motion mode for new high score.")

            # Draw everything
            screen.fill(black)
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

            # Display the score
            text = font.render(f"Score: {score}", True, white)
            screen.blit(text, (10, 10))

            # Apply blur effect during slow motion
            if slow_motion_active:
                apply_blur_effect(screen)

            # Display splash text for new high score or milestone
            if new_high_score_achieved or milestone_reached:
                current_time = pygame.time.get_ticks()
                if current_time - splash_start_time < splash_duration:
                    if new_high_score_achieved:
                        splash_text = "New High Score!"
                    elif milestone_reached:
                        splash_text = f"{score} Points!"
                    
                    splash_rendered = font.render(splash_text, True, yellow)
                    splash_rect = splash_rendered.get_rect(center=(width // 2, height // 2))
                    screen.blit(splash_rendered, splash_rect)

                    if current_time - splash_start_time < 100:  # Log only once at the start
                        logger.info(f"Splash text '{splash_text}' is being displayed on the screen.")
                else:
                    new_high_score_achieved = False
                    milestone_reached = False
                    slow_motion_active = False
                    logger.info("Exiting slow motion mode.")

        elif not game_active:
            screen.fill(black)
            draw_text("Press Enter to Start", font, white, screen, width // 2 - 150, height // 2 - 50)
            draw_text("Press P to Pause/Resume", font, white, screen, width // 2 - 150, height // 2)
            draw_text(f"High Score: {high_score}", font, white, screen, width // 2 - 150, height // 2 + 50)

            # Display congratulatory text if a new high score was achieved
            if high_score_updated_this_game:
                draw_text("new High Score!", font, yellow, screen, width // 2 - 150, height // 2 + 100)

        elif paused:
            draw_text("Paused", font, white, screen, width // 2 - 50, height // 2 - 50)
            draw_text("Press P to Resume", font, white, screen, width // 2 - 100, height // 2)

        pygame.display.flip()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()
