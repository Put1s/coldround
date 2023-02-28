import os
import sys
import pygame
import math

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QMainWindow


def load_image(name, colorKey=None):
    fullname = os.path.join("data", name)
    image = pygame.image.load(fullname)

    if colorKey is not None:
        image = image.convert()
        if colorKey == -1:
            colorKey = image.get_at((0, 0))
        image.set_colorkey(colorKey)
    else:
        image = image.convert_alpha()
    return image


class Entity:
    def __init__(self, x, y):
        self.entity = pygame.sprite.Sprite()
        self.entity.rect.center = x, y
        self.x = x
        self.y = y

    def set_image(self, image, path=None):
        self.entity.image = load_image(os.path.join(path, image), -1)
        self.entity.rect = self.entity.image.get_rect()
        self.entity.mask = pygame.mask.from_surface(self.entity.image)

    def update_pos(self, PlayerX, PlayerY):
        self.entity.rect.center = self.x + PlayerX, self.y + PlayerY


class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = 0
        self.states = 6

    def pick_up(self):
        self.kill()

    def animate(self):
        self.state += 1
        if self.state == self.states:
            self.state = 0
        self.set_image(str(self.state) + ".png", "coin")


class Spikes(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.set_image("spikes.png")


class Level:
    def __init__(self, level_id, coins, spikes):
        self.id = level_id
        self.coins = coins
        self.spikes = spikes
        self.sprites_group = pygame.sprite.Group()
        for coin in coins:
            self.sprites_group.add(coin.entity)
        for spikes in self.spikes:
            self.sprites_group.add(spikes.entity)

    def update(self, PlayerX, PlayerY):
        for coin in self.coins:
            coin.update_pos(PlayerX, PlayerY)
            coin.animate()
        for spikes in self.spikes:
            spikes.update_pos(PlayerX, PlayerY)

    def collide(self, player):
        for coin in self.coins:
            if pygame.sprite.collide_mask(player, coin):
                coin.pick_up()
        for spikes in self.spikes:
            if pygame.sprite.collide_mask(player, spikes):
                return True
        return False

    def show(self, screen):
        self.sprites_group.show(screen)


class Levels:
    def __init__(self, start_level):
        self.level = start_level
        self.levels = [
            Level(
                1,
                [Coin(228, 1337), Coin(1337, 228)],
                [Spikes(100, 2000), Spikes(-225, 1000)]
            ),
            Level(
                2,
                [Coin(1000, 1000), Coin(0, 0), Coin(50, 0), Coin(100, 0)],
                [Spikes(-500, 2000), Spikes(2000, 2000), Spikes(2000, 2050), Spikes(2000, 2100)]
            ),
        ]

    def next(self):
        self.level += 1

    def previous(self):
        self.level -= 1

    def set_level(self, level):
        self.level = level

    def update(self, player, PlayerX, PlayerY):
        self.levels[self.level].update(PlayerX, PlayerY)
        return self.levels[self.level].collide(player)

    def draw(self, screen):
        self.levels[self.level].draw(screen)


class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI.ui", self)
        self.LaunchButton.clicked.connect(self.launch)
        self.ExitButton.clicked.connect(self.exit)
        self.ComboBox.setCurrentIndex(0)

    @staticmethod
    def exit():
        exit(0)

    def launch(self):
        self.hide()

        levels = Levels(1)

        windowWidth, windowHeight = [(1280, 720), (1920, 1080), (1440, 900)][self.ComboBox.currentIndex()]

        pygame.init()
        pygame.display.set_caption("Sussy Baki")
        size = windowWidth, windowHeight
        screen = pygame.display.set_mode(size)

        main_menu_music = os.path.join("data", "sussy_baka.mp3")
        ambient = os.path.join("data", "ambient.mp3")
        final_menu_music = os.path.join("data", "social_credits.mp3")

        pygame.mixer.init()
        pygame.mixer.music.load(main_menu_music)
        pygame.mixer.music.play(-1)
        # pygame.mixer.music.unload()

        all_sprites = pygame.sprite.Group()

        # просто курсор
        cursor_sprite = pygame.sprite.Group()

        cursor = pygame.sprite.Sprite()
        cursor.image = load_image("cursor.png", -1)
        cursor.rect = cursor.image.get_rect()
        cursor_sprite.add(cursor)

        # менюшные спрайты
        menu_sprites = pygame.sprite.Group()

        menu = pygame.sprite.Sprite()
        menu.image = load_image("main_menu.png")
        menu.rect = menu.image.get_rect()
        menu.rect.center = windowWidth / 2, windowHeight / 2
        menu_sprites.add(menu)

        button_start = pygame.sprite.Sprite()
        button_start.image = load_image("ButtonStartGame.png")
        button_start.rect = button_start.image.get_rect()
        button_start.rect.center = windowWidth / 2, windowHeight / 2 - 200
        menu_sprites.add(button_start)
        button_start.remove()

        # для финального меню
        final_menu_sprites = pygame.sprite.Group()

        final_menu = pygame.sprite.Sprite()
        final_menu.image = load_image("final menu.png")
        final_menu.rect = final_menu.image.get_rect()
        final_menu.rect.center = windowWidth / 2, windowHeight / 2
        final_menu_sprites.add(final_menu)

        # группа спрайтов для игрового уровня (пола, стен ...)
        level_sprites = pygame.sprite.Group()

        floor = pygame.sprite.Sprite()
        floor.image = load_image("floor.png", -1)
        floor.rect = floor.image.get_rect()
        level_sprites.add(floor)

        walls = pygame.sprite.Sprite()
        walls.image = load_image("walls.png", -1)
        walls.rect = walls.image.get_rect()
        walls.mask = pygame.mask.from_surface(walls.image)
        level_sprites.add(walls)

        door = pygame.sprite.Sprite()
        door.image = load_image("door.png", -1)
        door.rect = door.image.get_rect()
        door.mask = pygame.mask.from_surface(door.image)
        level_sprites.add(door)

        player = pygame.sprite.Sprite()
        PlayerOrigImage = load_image("player.png", -1)
        player.image = load_image("player.png", -1)
        player.rect = player.image.get_rect()
        player.mask = pygame.mask.from_surface(player.image)
        level_sprites.add(player)

        coin = pygame.sprite.Sprite()
        coin.image = load_image("coin/0.png", -1)
        coin.rect = coin.image.get_rect()
        coin.mask = pygame.mask.from_surface(coin.image)
        coin.rect.center = 123123, 123123
        level_sprites.add(coin)

        if __name__ == "__main__":
            PlayerX, PlayerY = 850, 550
            PlayerVX, PlayerVY = 0, 0
            MouseX, MouseY = 0, 0
            FPS = 60
            acceleration = 0.4
            max_speed = 8
            running = True
            state = ["main_menu", 1]  # ["main_menu"/"game"/"final_menu", level]

            while running:
                pygame.mixer.music.play(loops=-1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEMOTION:
                        MouseX, MouseY = event.pos
                    elif state[0] == "main_menu" and event.type == pygame.MOUSEBUTTONDOWN and \
                            button_start.rect.collidepoint(MouseX, MouseY):
                        state[0] = "game"
                        cursor.image = cursor.image = load_image("cursor2.png", -1)
                        cursor.rect = cursor.image.get_rect()

                if pygame.mouse.get_focused():
                    pygame.mouse.set_visible(False)

                keys = pygame.key.get_pressed()

                if state[0] == "main_menu":
                    menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.rect.center = MouseX, MouseY
                    pygame.display.flip()
                    screen.fill("BLACK")
                    pygame.time.Clock().tick(FPS)

                elif state[0] == "game":
                    if keys[pygame.K_d] and PlayerVX >= -max_speed:
                        PlayerVX -= acceleration
                    elif keys[pygame.K_a] and PlayerVX <= max_speed:
                        PlayerVX += acceleration
                    else:
                        PlayerVX = PlayerVX * 0.9
                    if keys[pygame.K_w] and PlayerVY <= max_speed:
                        PlayerVY += acceleration
                    elif keys[pygame.K_s] and PlayerVY >= -max_speed:
                        PlayerVY -= acceleration
                    else:
                        PlayerVY = PlayerVY * 0.9
                    PlayerX += int(PlayerVX)  # проверка столкновений со стенами
                    walls.rect.center = PlayerX, PlayerY
                    if pygame.sprite.collide_mask(player, walls):
                        PlayerX -= int(PlayerVX)
                        PlayerVX = 0

                    PlayerY += int(PlayerVY)
                    walls.rect.center = PlayerX, PlayerY
                    if pygame.sprite.collide_mask(player, walls):
                        PlayerY -= int(PlayerVY)
                        PlayerVY = 0

                    # проверка коллизии с переходом на следующий уроваень
                    if pygame.sprite.collide_mask(player, door):
                        if state[1] == 1:
                            state[1] = 2
                            PlayerX, PlayerY = 2600, 1500
                            floor.image = load_image("floor2.png", -1)
                            floor.rect = floor.image.get_rect()

                            walls.image = load_image("walls2.png", -1)
                            walls.rect = walls.image.get_rect()
                            walls.mask = pygame.mask.from_surface(walls.image)

                            door.image = load_image("door2.png", -1)
                            door.rect = door.image.get_rect()
                            door.mask = pygame.mask.from_surface(door.image)
                        else:
                            state[0] = "final_menu"

                    MouseRelativeX, MouseRelativeY = MouseX - (windowWidth // 2), MouseY - (
                            windowHeight // 2)  # код поворота игрока
                    PlayerAngle = (180 / math.pi) * -math.atan2(MouseRelativeY, MouseRelativeX)
                    player.image = pygame.transform.rotate(PlayerOrigImage, int(PlayerAngle))
                    player.mask = pygame.mask.from_surface(player.image)
                    player.rect = player.image.get_rect(center=((windowWidth // 2), (windowHeight // 2)))

                    walls.rect.center = PlayerX, PlayerY
                    player.rect.center = windowWidth // 2, windowHeight // 2
                    floor.rect.center = PlayerX, PlayerY
                    door.rect.center = PlayerX, PlayerY
                    cursor.rect.center = MouseX + 2, MouseY + 2
                    coin.rect.center = PlayerX, PlayerY
                    Levels.update(player, PlayerX, PlayerY)
                    level_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    Levels.draw(screen)
                    pygame.display.flip()
                    screen.fill("BLACK")
                    pygame.time.Clock().tick(FPS)

                elif state[0] == "final_menu":
                    final_menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.image = load_image("cursor.png", -1)
                    cursor.rect.center = MouseX, MouseY
                    pygame.display.flip()
                    screen.fill("BLACK")
                    pygame.time.Clock().tick(FPS)
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Game()
    window.show()
    sys.exit(app.exec_())
