import pygame as pg

class Bird:
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
        self.image = pg.image.load("assests/birdup.png").convert_alpha()
        self.image = pg.image.load("assests/birddown.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (int(34 * self.scale_factor), int(24 * self.scale_factor)))
        self.rect = self.image.get_rect(center=(100, 300))
        self.velocity = 0
        self.update_on = False  # Initially, the bird doesn't move
        self.flap_strength = -8  # Default value, changes in setGameDifficulty()


    def update(self, dt):
        if self.update_on:  # Update only if the game has started
            self.velocity += 0.5  # gravity effect
            self.rect.y += self.velocity

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= 568:
                self.rect.bottom = 568
                self.velocity = 0  # Stop falling when hitting the ground

    def flap(self, dt):
        self.velocity = self.flap_strength  # Apply the flap strength
        self.update_on = True  # Start the bird's movement after the first flap

    def resetPosition(self):
        self.rect.center = (100, 300)
        self.velocity = 0
