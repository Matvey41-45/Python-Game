import pygame
import json

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

width = 800
height = 800
clock = pygame.time.Clock()
fps = 60
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('Platformer')
bg_image = pygame.image.load('images/bg.png')
bg_rect = bg_image.get_rect()

tile_size = 40
game_over = 0
main_menu = True

level = 1
max_level = 3
score = 0
lives = 3

with open(f'levels/level{level}.json', 'r') as file:
    world_data = json.load(file)

sound_jump = pygame.mixer.Sound('music/jump.wav')
sound_game_over = pygame.mixer.Sound('music/game_over.wav')
sound_coin = pygame.mixer.Sound('music/coin.wav')


def draw_text(text, color, size, x, y):
    font = pygame.font.SysFont('Arial', size)
    img = font.render(text, True, color)
    display.blit(img, (x, y))


class Button:
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display.blit(self.image, self.rect)
        return action


class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        self.image = pygame.image.load('images/player2.png')
        self.image = pygame.transform.scale(self.image, (35, 35))
        self.ghost_image = pygame.image.load('images/ghost.png')
        self.ghost_image = pygame.transform.scale(self.ghost_image, (35, 35))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.jumped = False
        self.index = 0
        self.counter = 0
        self.direction = 1
        self.images_right = [self.image, pygame.transform.flip(self.image, True, False)]
        self.images_left = [pygame.transform.flip(self.image, True, False), self.image]

    def update(self, tile_list):
        global game_over
        x = 0
        y = 0
        walk_speed = 10

        if game_over == 0:
            key = pygame.key.get_pressed()

            if key[pygame.K_SPACE] and self.jumped == False:
                self.gravity = -15
                self.jumped = True
                sound_jump.play()

            if key[pygame.K_SPACE] == False:
                self.jumped = False

            if key[pygame.K_LEFT]:
                x -= 5
                self.direction = -1
                self.counter += 1
            if key[pygame.K_RIGHT]:
                x += 5
                self.direction = 1
                self.counter += 1

            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity

            for tile in tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.rect.width, self.rect.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.rect.width, self.rect.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                self.image = self.ghost_image
                sound_game_over.play()

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            self.rect.x += x
            self.rect.y += y

            if self.rect.bottom > height:
                self.rect.bottom = height
                self.gravity = 0

        elif game_over == -1:
            if self.rect.y > 0:
                self.rect.y -= 5

        display.blit(self.image, self.rect)


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/tile3.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/door.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class World:
    def __init__(self, data):
        dirt_img = pygame.image.load('images/tile2.png')
        grass_img = pygame.image.load('images/tile1.png')

        self.tile_list = []
        self.start_x = 100
        self.start_y = height - 130

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1: dirt_img, 2: grass_img}
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tile_list.append((img, img_rect))
                elif tile == 3:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                elif tile == 4:
                    self.start_x = col_count * tile_size
                    self.start_y = row_count * tile_size
                elif tile == 5:
                    exit_node = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit_node)
                elif tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            display.blit(tile[0], tile[1])


def reset_level():
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()

    with open(f'levels/level{level}.json', 'r') as file:
        world_data = json.load(file)
    world = World(world_data)
    return world


lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

world = World(world_data)
player = Player(world.start_x, world.start_y)

restart_button = Button(width // 2, height // 2, 'images/restart_btn 2.png')
start_button = Button(width // 2 - 150, height // 2, 'images/start_btn 2.png')
exit_button = Button(width // 2 + 150, height // 2, 'images/exit_btn 2.png')

run = True
while run:
    clock.tick(fps)
    display.blit(bg_image, bg_rect)

    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
            level = 1
            score = 0
            lives = 3
            world = reset_level()
            player.reset(world.start_x, world.start_y)
    else:
        world.draw()

        lava_group.draw(display)
        exit_group.draw(display)
        coin_group.draw(display)

        draw_text(str(score), (255, 255, 255), 30, 10, 10)

        player.update(world.tile_list)

        if pygame.sprite.spritecollide(player, coin_group, True):
            score += 1
            sound_coin.play()
            print(score)

        if game_over == -1:
            if restart_button.draw():
                lives -= 1
                if lives == 0:
                    main_menu = True
                    lives = 3
                score = 0
                world = reset_level()
                player.reset(world.start_x, world.start_y)
                game_over = 0

        elif game_over == 1:
            game_over = 0
            if level < max_level:
                level += 1
                world = reset_level()
                player.reset(world.start_x, world.start_y)
            else:
                print('win')
                main_menu = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()