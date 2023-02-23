import keyboard as kb
import mouse as m
import os
import sys
import pygame
import math
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QMainWindow


class Launcher(QMainWindow):
    global WindowWidth, WindowHeight
    WindowWidth = 1280
    WindowHeight = 720
    launching = False
    resolutions = [[1280, 720], [1920, 1080], [1440, 900]]

    def __init__(self):
        super().__init__()
        uic.loadUi('user interface.ui', self)
        self.LaunchButton.clicked.connect(self.launch)
        self.ExitButton.clicked.connect(self.exit)
        self.ComboBox.setCurrentIndex(0)
        self.ComboBox.currentIndexChanged.connect(self.combo_changed)


    def exit(self):
        exit(0)

    def combo_changed(self, i):
        global WindowWidth, WindowHeight
        WindowWidth, WindowHeight = tuple(self.resolutions[i])

    def launch(self):
        self.hide()
        def load_image(name, colorkey=None):
            fullname = os.path.join('data', name)
            image = pygame.image.load(fullname)

            if colorkey != None:
                image = image.convert()
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            else:
                image = image.convert_alpha()
            return image
        
        
        pygame.init()                              # начало кода самой игры
        pygame.display.set_caption('Hotline Maiami 3')
        size = WindowWidth, WindowHeight
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
        menu.image = load_image("main menu.png")
        menu.rect = menu.image.get_rect()
        menu.rect.center = WindowWidth / 2, WindowHeight / 2
        menu_sprites.add(menu)

        button_start = pygame.sprite.Sprite()
        button_start.image = load_image("shizofreniya.png")
        button_start.rect = button_start.image.get_rect()
        button_start.rect.center = WindowWidth / 2, WindowHeight / 2
        menu_sprites.add(button_start)



        # группа спрайтов для игрового уровня (пола, стен ...)
        level_sprites = pygame.sprite.Group()

        floor = pygame.sprite.Sprite()
        floor.image = load_image("фон.png")
        floor.rect = floor.image.get_rect()
        level_sprites.add(floor)

        walls = pygame.sprite.Sprite()
        walls.image = load_image("walls.png", -1)
        walls.rect = walls.image.get_rect()
        walls.mask = pygame.mask.from_surface(walls.image)
        level_sprites.add(walls)

        player = pygame.sprite.Sprite()
        PlayerOrigImage = load_image("смешарик.png", -1)
        player.image = load_image("смешарик.png", -1)
        player.rect = player.image.get_rect()
        player.mask = pygame.mask.from_surface(player.image)
        level_sprites.add(player)


        
        if __name__ == '__main__':
            PlayerX, PlayerY = 200, 400
            PlayerVX, PlayerVY = 0, 0
            FPS = 60
            acceleration = 0.4
            max_speed = 8
            running = True
            menu = 'main'
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEMOTION:
                        MouseX, MouseY = event.pos
                if pygame.mouse.get_focused():
                    pygame.mouse.set_visible(False)

                
                if menu == 'main':
                    if m.is_pressed() and button_start.rect.collidepoint(MouseX, MouseY):
                        menu = 'no'
                        cursor.image = cursor.image = load_image("cursor2.png", -1)
                        cursor.rect = cursor.image.get_rect()
                    menu_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    cursor.rect.center = MouseX, MouseY
                    pygame.display.flip()
                    screen.fill('BLACK')
                    pygame.time.Clock().tick(FPS)


                else:
                    if kb.is_pressed('d') and PlayerVX >= -max_speed:
                        PlayerVX -= acceleration
                    elif kb.is_pressed('a') and PlayerVX <= max_speed:
                        PlayerVX += acceleration
                    else:
                        PlayerVX = PlayerVX * 0.9
                    if kb.is_pressed('w') and PlayerVY <= max_speed:
                        PlayerVY += acceleration
                    elif kb.is_pressed('s') and PlayerVY >= -max_speed:
                        PlayerVY -= acceleration
                    else:
                        PlayerVY = PlayerVY * 0.9

                        
                    PlayerX += int(PlayerVX)
                    walls.rect.center = PlayerX, PlayerY
                    if pygame.sprite.collide_mask(player, walls):
                        PlayerX -= int(PlayerVX)
                        PlayerVX = 0

                    PlayerY += int(PlayerVY)
                    walls.rect.center = PlayerX, PlayerY
                    if pygame.sprite.collide_mask(player, walls):
                        PlayerY -= int(PlayerVY)
                        PlayerVY = 0

                    MouseRelativeX, MouseRelativeY = MouseX - (WindowWidth // 2), MouseY - (WindowHeight // 2)
                    PlayerAngle = (180 / math.pi) * -math.atan2(MouseRelativeY, MouseRelativeX)
                    player.image = pygame.transform.rotate(PlayerOrigImage, int(PlayerAngle))
                    player.mask = pygame.mask.from_surface(player.image)
                    player.rect = player.image.get_rect(center=((WindowWidth // 2), (WindowHeight // 2)))
                    


                    walls.rect.center = PlayerX, PlayerY
                    player.rect.center = WindowWidth // 2, WindowHeight // 2
                    floor.rect.center = PlayerX, PlayerY
                    cursor.rect.center = MouseX + 2, MouseY + 2
                    level_sprites.draw(screen)
                    cursor_sprite.draw(screen)
                    pygame.display.flip()
                    screen.fill('BLACK')
                    pygame.time.Clock().tick(FPS)
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    app=QApplication(sys.argv)
    window=Launcher()
    window.show()
    sys.exit(app.exec_())

