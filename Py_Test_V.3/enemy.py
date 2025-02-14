import pygame
import random
import os
import math
from logging import getLogger

logger = getLogger("game")

class Enemy:
    def __init__(self, x, y, size, speed, screen_width, screen_height, image_path=None):
        self.pos = [x, y]
        self.size = size
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        if image_path:
            assets_folder = os.path.join(os.path.dirname(__file__), 'assets', 'images')
            image_file_path = os.path.join(assets_folder, image_path)
            try:
                self.original_image = pygame.image.load(image_file_path).convert_alpha()
                self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
                logger.info(f"Successfully loaded enemy image {image_path} and scaled to size: {self.size}")
            except pygame.error as e:
                logger.error(f"Failed to load enemy image {image_path}: {e}")
                # Fallback to colored surface
                self.image = pygame.Surface((self.size, self.size))
                self.image.fill((255, 0, 0))  # Default to red for enemies
                logger.info(f"Using fallback enemy rectangle with size: {self.size}")
        else:
            # Fallback to colored surface if no image is provided
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill((255, 0, 0))  # Default to red for enemies

        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dt):
        self.pos[1] += self.speed * dt
        if self.pos[1] > self.screen_height:
            logger.info(f"Enemy reset to top of screen from position {self.pos}")
            self.pos[1] = 0
            self.pos[0] = random.randint(0, self.screen_width - self.size)
            return True
        return False

    def draw(self, screen):
        screen.blit(self.image, (self.pos[0], self.pos[1]))


class RedEnemy(Enemy):
    def __init__(self, x, y, size, screen_width, screen_height):
        super().__init__(x, y, size, random.randint(80, 120), screen_width, screen_height, 'RedEnemy.png')

class YellowEnemy(Enemy):
    def __init__(self, x, y, size, screen_width, screen_height):
        super().__init__(x, y, size, random.randint(150, 200), screen_width, screen_height, 'YellowEnemy.png')
        self.wave_amplitude = random.randint(30, 50)
        self.wave_frequency = random.uniform(1, 2)

    def move(self, dt):
        self.pos[1] += self.speed * dt
        self.pos[0] += math.sin(self.pos[1] / (50 * self.wave_frequency)) * self.wave_amplitude * dt
        return super().move(dt)

class GreenEnemy(Enemy):
    def __init__(self, x, y, size, screen_width, screen_height):
        super().__init__(x, y, size, 300, screen_width, screen_height, 'GreenEnemy.png')
        self.wave_amplitude = 50
        self.time = 0

    def move(self, dt):
        self.time += dt
        self.speed = 200 + math.sin(self.time * 2) * self.wave_amplitude
        self.pos[1] += self.speed * dt
        return super().move(dt)
