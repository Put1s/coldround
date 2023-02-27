import os
import sys
import pygame
import math
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QMainWindow


class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)
        self.LaunchButton.clicked.connect(self.launch)
        self.ExitButton.clicked.connect(self.exit)
        self.ComboBox.setCurrentIndex(0)

    def exit(self):
        exit(0)

    def launch(self):
        self.hide()

        windowWidth, windowHeight = [(1280, 720), (1920, 1080), (1440, 900)][self.ComboBox.currentIndex()]

        def load_image(name, colorKey=None):
            fullname = os.path.join('data', name)
            image = pygame.image.load(fullname)

            if colorKey is not None:
                image = image.convert()
                if colorKey == -1:
                    colorKey = image.get_at((0, 0))
                image.set_colorkey(colorKey)
            else:
                image = image.convert_alpha()
            return image

        pygame.init()  # начало кода самой игры
        pygame.display.set_caption('Sussy Baki')
        size = windowWidth, windowHeight
        screen = pygame.display.set_mode(size)

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

        final_menu_sprites = pygame.sprite.Group()  # для финального меню

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

        if __name__ == '__main__':
            PlayerX, PlayerY = 850, 550
            PlayerVX, PlayerVY = 0, 0
            MouseX, MouseY = 0, 0
            FPS = 60
            acceleration = 0.4
            max_speed = 8
            running = True
            menu = 'main'
            level = 1
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEMOTION:
                        MouseX, MouseY = event.pos
                    elif menu == 'main' and event.type == pygame.MOUSEBUTTONDOWN and \
                            button_start.rect.collidepoint(MouseX, MouseY):
                        menu = 'no'
                        cursor.image = cursor.image = load_image("cursor2.png", -1)
                        cursor.rect = cursor.image.get_rect()

                if pygame.mouse.get_focused():
                    pygame.mouse.set_visible(False)

                keys = pygame.key.get_pressed()

                if menu == 'main':
                    menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.rect.center = MouseX, MouseY
                    pygame.display.flip()
                    screen.fill('BLACK')
                    pygame.time.Clock().tick(FPS)

                elif menu == 'no':
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
                        if level == 1:
                            level = 2
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
                            menu = 'final'

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
                    level_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    pygame.display.flip()
                    screen.fill('BLACK')
                    pygame.time.Clock().tick(FPS)

                if menu == 'final':
                    final_menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.rect.center = MouseX, MouseY
                    pygame.display.flip()
                    screen.fill('BLACK')
                    pygame.time.Clock().tick(FPS)
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Launcher()
    window.show()
    sys.exit(app.exec_())
