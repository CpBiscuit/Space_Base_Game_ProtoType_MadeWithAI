import pygame
from logging import getLogger
import os

logger = getLogger("game")

class Player:
    def __init__(self, x, y, size, speed, screen_width):
        # Initialize player position, size, and movement speed
        self.pos = [x, y]
        self.size = size  # Correctly set self.size based on the initialization value
        self.speed = speed
        self.screen_width = screen_width

        # Load the spaceship image
        assets_folder = os.path.join(os.path.dirname(__file__), 'assets', 'images')
        spaceship_path = os.path.join(assets_folder, 'spaceship.png')

        try:
            self.original_image = pygame.image.load(spaceship_path).convert_alpha()  # Load image with alpha transparency
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))  # Scale image to fit the player size
            logger.info("Successfully loaded and scaled spaceship image to size: {}".format(self.size))
        except pygame.error as e:
            logger.error(f"Failed to load spaceship image: {e}")
            self.image = pygame.Surface((self.size, self.size))  # Fallback to a colored surface (a filled rectangle)
            self.image.fill((255, 255, 255))  # Fill the fallback image with white color
            logger.info("Using a fallback player rectangle with size: {}".format(self.size))

        # Create a mask for precise collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Initialize movement control attributes
        self.moving_left = False
        self.moving_right = False
        self.last_key_pressed = None

    def handle_event(self, event):
        # Handle key press events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if not self.moving_left:
                    logger.info("Started moving left")
                self.moving_left = True
                self.last_key_pressed = pygame.K_LEFT
            if event.key == pygame.K_RIGHT:
                if not self.moving_right:
                    logger.info("Started moving right")
                self.moving_right = True
                self.last_key_pressed = pygame.K_RIGHT

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.moving_left = False
                logger.info("Stopped moving left")
                if self.moving_right:
                    self.last_key_pressed = pygame.K_RIGHT
                    logger.info("Switching to moving right")
            if event.key == pygame.K_RIGHT:
                self.moving_right = False
                logger.info("Stopped moving right")
                if self.moving_left:
                    self.last_key_pressed = pygame.K_LEFT
                    logger.info("Switching to moving left")

    def move(self, dt):
        # Apply movement based on the last key pressed
        if self.last_key_pressed == pygame.K_LEFT and self.moving_left:
            self.pos[0] -= self.speed * dt
            if self.pos[0] < 0:
                self.pos[0] = 0
        elif self.last_key_pressed == pygame.K_RIGHT and self.moving_right:
            self.pos[0] += self.speed * dt
            if self.pos[0] > self.screen_width - self.size:
                self.pos[0] = self.screen_width - self.size

    def draw(self, screen):
        # Draw the spaceship image
        logger.debug(f"Drawing player at position {self.pos} with size {self.size}")
        screen.blit(self.image, (self.pos[0], self.pos[1]))

    def get_mask(self):
        # Return the collision mask for the player
        return self.mask
