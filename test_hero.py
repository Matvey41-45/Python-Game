import pygame
pygame.init()

width, height = 800, 800
clock = pygame.time.Clock()

display = pygame.display.set_mode((width, height))

class Hero:
    def __init__(self):
        self.image = pygame.image.load('img/player1.png')
        self.rect = self.image.get_rect()
        self.direction = 1

    def update(self):
        self.rect.x += self.direction
        if self.rect.right > width or self.rect.left < 0:
            self.direction *= -1
        display.blit(self.image, self.rect)

hero = Hero()
run = True
while run:
    clock.tick(60)
    display.fill('white')
    hero.update()
    pygame.display.update()
pygame.quit()