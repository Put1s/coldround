import os
import sys
import pygame
import math
import random

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

        # coin = pygame.sprite.Sprite()
        # coin.image = load_image("coin/0.png", -1)
        # coin.rect = coin.image.get_rect()
        # coin.mask = pygame.mask.from_surface(coin.image)
        # coin.rect.center = 123123, 123123
        # level_sprites.add(coin)

        font = pygame.font.Font(None, 72)
        score = 0
        text = font.render("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", True, (255, 0, 0))
        place = text.get_rect(
            center=(200, 150))
        screen.blit(text, place)

        class Entity:
            def __init__(self, x_, y_):
                self.entity = pygame.sprite.Sprite()
                self.entity.image = load_image("cat.png", -1)
                self.entity.rect = self.entity.image.get_rect()
                self.entity.rect.center = x_, y_
                self.x = x_
                self.y = y_

            def set_image(self, image_):
                self.entity.image = load_image(image_, -1)
                # self.entity.rect = self.entity.image.get_rect()
                # self.entity.mask = pygame.mask.from_surface(self.entity.image)

            def update_pos(self, PlayerX_, PlayerY_):
                # self.entity.rect.center = self.x, self.y
                self.entity.rect.center = self.x + PlayerX_, self.y + PlayerY_

        class Coin(Entity):
            def __init__(self, x_, y_):
                super().__init__(x_, y_)
                self.exists = True
                self.state = 0
                self.states = 6
                self.animate()

            def pick_up(self):
                self.entity.kill()

            def animate(self):
                self.state += 1
                if self.state == self.states:
                    self.state = 0
                self.set_image("coin/" + str(self.state) + ".png")

        class Spikes(Entity):
            def __init__(self, x, y):
                super().__init__(x, y)
                self.set_image("spikes.png")

        class Level:
            def __init__(self, level_name_, left_up_, right_down_, coins_, spikes_, floor_image_):
                self.name = level_name_
                self.left_up = left_up_
                self.right_down = right_down_
                self.coins = coins_
                self.spikes = spikes_
                self.floor = pygame.sprite.Sprite()
                self.floor.image = load_image(floor_image_, -1)
                self.floor.rect = floor.image.get_rect()
                self.floor.mask = pygame.mask.from_surface(floor.image)
                self.sprites_group = pygame.sprite.Group()
                for coin_ in coins_:
                    self.sprites_group.add(coin_.entity)
                for spikes_ in self.spikes:
                    self.sprites_group.add(spikes_.entity)

            def set_coins(self, coins_):
                for coin_ in self.coins:
                    self.sprites_group.remove(coin_.entity)
                self.coins = coins_
                for coin_ in self.coins:
                    self.sprites_group.add(coin_.entity)

            def set_spikes(self, spikes_):
                for spike_ in self.spikes:
                    self.sprites_group.remove(spike_.entity)
                self.spikes = spikes_
                for spike_ in self.spikes:
                    self.sprites_group.add(spike_.entity)

            def reset(self, coins_, spikes_):
                self.coins = coins_
                self.spikes = spikes_
                self.sprites_group = pygame.sprite.Group()
                for coin_ in coins_:
                    self.sprites_group.add(coin_.entity)
                for spikes_ in self.spikes:
                    self.sprites_group.add(spikes_.entity)

            def update(self, PlayerX_, PlayerY_):
                for coin_ in self.coins:
                    coin_.update_pos(PlayerX_, PlayerY_)
                    coin_.animate()
                for spikes_ in self.spikes:
                    spikes_.update_pos(PlayerX_, PlayerY_)

            def collide(self, player_): # -> pair: score(int), death(True/False)
                score_ = 0
                for coin_ in self.coins:
                    if pygame.sprite.collide_mask(player_, coin_.entity) and coin_.exists:
                        coin_.pick_up()
                        coin_.exists = False
                        score_ += 1
                for spikes_ in self.spikes:
                    if pygame.sprite.collide_mask(player_, spikes_.entity):
                        return score_, True
                return score_, False

            def draw(self, screen_):
                self.sprites_group.draw(screen_)

        class Levels:
            def __init__(self, start_level_, floors_images_):
                self.score = 0
                self.level = start_level_ - 1
                self.configure = [
                    # имя, левый верхний угол и правый нижний угол спавна энтити, кол-во монет, кол-во шипов
                    # TODO: подобрать координаты спавна энтити чтобы на двух этажах норм спавнилось
                    ("First floor", (0, 0), (500, 800), 20, 10),
                    ("Second floor", (-2000, -100), (2000, 2000), 100, 30)  # (4254, 2646)
                ]
                self.levels = [Level("void", 0, 0, [], [], floors_images_[i]) for i in range(len(floors_images_))]
                self.reset()
                # for level_ in self.configure:
                #     self.levels.append(
                #         Level(level_[0], level_[1], level_[2],
                #               [Coin(random.randint(level_[1][0], level_[2][0]),
                #                     random.randint(level_[1][1], level_[2][1]))
                #                for i in range(level_[3]) if],
                #               [Spikes(random.randint(level_[1][0], level_[2][0]),
                #                       random.randint(level_[1][1], level_[2][1]))
                #                for i in range(level_[4])]
                #               )
                #     )

            def get_score(self):
                return str(self.score)

            def next(self):
                self.level += 1

            def previous(self):
                self.level -= 1

            def set_level(self, level_):
                self.level = level_ - 1

            def reset(self):
                for i, level_ in enumerate(self.levels):
                    coins_ = list()
                    for j in range(self.configure[i][3]):
                        x_, y_ = random.randint(self.configure[i][1][0], self.configure[i][2][0]), \
                            random.randint(self.configure[i][1][1], self.configure[i][2][1])
                        coin_ = Coin(x_, y_)
                        if not pygame.sprite.collide_mask(coin_.entity, level_.floor):
                            coins_.append(coin_)
                        # coins_.append(coin_)
                    level_.set_coins(coins_)
                    spikes_ = list()
                    for j in range(self.configure[i][4]):
                        x_, y_ = random.randint(self.configure[i][1][0], self.configure[i][2][0]), \
                            random.randint(self.configure[i][1][1], self.configure[i][2][1])
                        spike_ = Spikes(x_, y_)
                        if not pygame.sprite.collide_mask(spike_.entity, level_.floor):
                            spikes_.append(spike_)
                        # spikes_.append(spike_)
                    level_.set_spikes(spikes_)
                    # level_.reset(
                    #     [Coin(random.randint(0, self.configure[i][1][0]), random.randint(0, self.configure[i][1][1]))
                    #      for j in range(self.configure[i][2])],
                    #     [Spikes(random.randint(0, self.configure[i][1][0]), random.randint(0, self.configure[i][1][1]))
                    #      for j in range(self.configure[i][3])]
                    # )

            def update(self, player_, PlayerX_, PlayerY_):
                self.levels[self.level].update(PlayerX_, PlayerY_)
                t_ = self.levels[self.level].collide(player_)
                self.score += t_[0]
                return t_[1]

            def draw(self, screen_):
                self.levels[self.level].draw(screen_)

        floors = Levels(1, ["floor.png", "floor2.png"])

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
                        pygame.mixer.music.unload()
                        pygame.mixer.music.load(ambient)
                        pygame.mixer.music.play(-1)

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
                            pygame.mixer.music.unload()
                            pygame.mixer.music.load(final_menu_music)
                            pygame.mixer.music.play(-1)
                        floors.next()

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
                    # coin.rect.center = PlayerX, PlayerY
                    if floors.update(player, PlayerX, PlayerY):
                        walls.image = load_image("walls.png", -1)
                        walls.rect = walls.image.get_rect()
                        walls.mask = pygame.mask.from_surface(walls.image)

                        door.image = load_image("door.png", -1)
                        door.rect = door.image.get_rect()
                        door.mask = pygame.mask.from_surface(door.image)

                        floor.image = load_image("floor.png", -1)
                        floor.rect = floor.image.get_rect()
                        floors.set_level(1)
                        floors.reset()
                        PlayerX, PlayerY = 850, 550
                        state[1] = 1
                        floors.score = 0
                    level_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    floors.draw(screen)
                    text = font.render(floors.get_score(), True, (255, 0, 0))
                    screen.blit(text, (100, 100))
                    pygame.display.flip()
                    screen.fill("BLACK")
                    pygame.time.Clock().tick(FPS)

                elif state[0] == "final_menu":
                    final_menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.image = load_image("cursor.png", -1)
                    cursor.rect.center = MouseX, MouseY
                    text = font.render(floors.get_score(), True, (255, 0, 0))
                    screen.blit(text, (100, 100))
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
