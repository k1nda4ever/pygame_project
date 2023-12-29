import pygame
import os
import sys
import tkinter as tk
from tkinter import simpledialog
import tkinter.filedialog
from tkinter import messagebox

# the input dialog
toptk = tk.Tk()
toptk.geometry("250x250+800+300")
toptk.update_idletasks()
toptk.withdraw()
username = ""
steps = 0
menu_option = 0
# A variable to check for the status later
click = False

pygame.init()
size = width, height = 800, 800
size_all_screen = 800, 830

pygame.display.set_caption('Project_name')
FPS = 60
WIDTH = 800
HEIGHT = 830
STEP = 10
screen = pygame.display.set_mode(size_all_screen)
clock = pygame.time.Clock()
x1, y1, x2, y2 = 0, 0, 0, 0

nLevel = 0
level_map = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {'wall': load_image('wall.jpg'), 'empty': load_image('snow.png'), 'portal': load_image('portal.png')}
player_image = load_image('stay.png', -1)

tile_width = tile_height = 50


def load_map(filename):
    global level_map
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global x1, y1, x2, y2

    new_player1, new_player2, x, y = None, None, None, None
    k = 0
    for item in all_sprites:
        item.kill()
    for item in player_group:
        item.kill()
    for item in tiles_group:
        item.kill()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 'p':
                Tile('portal', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                if k == 0:
                    if menu_option != 3:
                        x1 = x
                        y1 = y
                    new_player1 = Player(x1, y1)
                    k = 1
                else:
                    if menu_option != 3:
                        x2 = x
                        y2 = y
                    new_player2 = Player(x2, y2)
    return new_player1, new_player2


def terminate():
    pygame.quit()
    sys.exit()


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def start_screen():
    global steps, nLevel, username, click, menu_option
    intro_text = ["Правила игры",
                  "Чтобы пройти игру, Вам необходимо проходить уровни,",
                  "вводя одновременно обоих персонажей в порталы,",
                  "чтобы подниматься по уровням."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    font = pygame.font.Font(None, 30)

    while True:
        screen.blit(fon, (0, 0))
        text_coord = 570
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        draw_text('Main Menu', font, (0, 0, 0), screen, 346, 150)

        mx, my = pygame.mouse.get_pos()

        # creating buttons
        button_1 = pygame.Rect(300, 200, 200, 50)
        button_2 = pygame.Rect(300, 280, 200, 50)
        button_3 = pygame.Rect(300, 360, 200, 50)

        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
        pygame.draw.rect(screen, (255, 0, 0), button_3)

        # writing text on top of button
        draw_text('NEW GAME', font, (255, 255, 255), screen, 343, 215)
        draw_text('LOAD GAME', font, (255, 255, 255), screen, 340, 295)
        draw_text('EXIT', font, (255, 255, 255), screen, 375, 375)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE]:
                terminate()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click = True

        # defining functions when a certain button is pressed
        if button_1.collidepoint((mx, my)):  # new game button
            if click:
                username = simpledialog.askstring(
                    title="New game", prompt="                 What's your Name?:               ", parent=toptk)
                if username is None:
                    continue
                steps = 0
                nLevel = 1
                game()
        if button_2.collidepoint((mx, my)):  # load game button
            if click:
                load_game()
                if menu_option == 3:
                    game()
        #        pygame.display.update()
        if button_3.collidepoint((mx, my)):  # exit button
            if click:
                terminate()

        pygame.display.flip()
        clock.tick(FPS)


def save_game():
    global steps, nLevel, username
    """Create a Tk file dialog and cleanup when finished"""
    top = tk.Tk()
    top.withdraw()
    filename = tkinter.filedialog.asksaveasfilename(parent=top)
    top.destroy()
    if filename == '':
        return
    #    filename = "data/" + file_name
    with open(filename, 'w', encoding="utf-8") as mapFile:
        mapFile.write(f'{username}\n{steps}\n{nLevel}\n{x1}\n{y1}\n{x2}\n{y2}')
    messagebox.showinfo('Game save', f'Game saved to file: {filename}.')


def load_game():
    global steps, nLevel, username, x1, x2, y1, y2, menu_option
    """Create a Tk file dialog and cleanup when finished"""
    top = tk.Tk()
    top.withdraw()
    filename = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    if filename == '':
        return
    #   filename = "data/" + file_name
    try:
        with open(filename, 'r', encoding="utf-8") as mapFile:
            read_file = [line.strip() for line in mapFile]
    except UnicodeDecodeError:
        messagebox.showinfo('Load error', f'File {filename} cannot be opened.')
        return
    try:
        steps = int(read_file[1])
        nLevel = int(read_file[2])
        username = str(read_file[0])
        x1 = int(read_file[3])
        y1 = int(read_file[4])
        x2 = int(read_file[5])
        y2 = int(read_file[6])
        menu_option = 3
    except ValueError and IndexError:
        messagebox.showinfo('Load error', f'File {filename} cannot be opened.')
        return

    messagebox.showinfo('Loaded successfully', f'File {filename} is opened.')

    return


def menu():
    global steps, nLevel, username, click, menu_option
    while True:
        font = pygame.font.Font(None, 30)
        menu_rect = pygame.Rect(260, 130, 280, 400)
        pygame.draw.rect(screen, (100, 100, 100), menu_rect)
        draw_text('Menu', font, (255, 0, 0), screen, 375, 160)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(300, 200, 200, 50)
        button_2 = pygame.Rect(300, 280, 200, 50)
        button_3 = pygame.Rect(300, 360, 200, 50)
        button_4 = pygame.Rect(300, 440, 200, 50)

        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
        pygame.draw.rect(screen, (255, 0, 0), button_3)
        pygame.draw.rect(screen, (255, 0, 0), button_4)

        # writing text on top of button
        draw_text('MAIN MENU', font, (255, 255, 255), screen, 343, 215)
        draw_text('SAVE GAME', font, (255, 255, 255), screen, 340, 295)
        draw_text('LOAD GAME', font, (255, 255, 255), screen, 340, 375)
        draw_text('EXIT', font, (255, 255, 255), screen, 375, 455)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE]:
                return
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click = True

        # defining functions when a certain button is pressed
        if button_1.collidepoint((mx, my)):  # main menu button with game ending
            if click:
                if tkinter.messagebox.askokcancel(
                        title='Info', message='Are you sure you want to finish the game and go to the main menu'):
                    menu_option = 1
                    return

        if button_2.collidepoint((mx, my)):  # save game button
            if click:
                save_game()

        if button_3.collidepoint((mx, my)):  # load game button
            if click:
                load_game()
                if menu_option == 3:
                    return
        if button_4.collidepoint((mx, my)):  # exit button
            if click:
                terminate()

        pygame.display.flip()
        clock.tick(FPS)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 8, tile_height * pos_y + 2)

    def update(self, x, y, p):
        global x1, y1, x2, y2
        if 0 <= self.rect.y + y < height and 0 <= self.rect.x + x < width and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@', 'p'):

            if p == 1:
                if x2 != x1 + x // tile_width or y2 != y1 + y // tile_height:
                    self.rect = self.rect.move(x, y)
                    x1 = x1 + x // tile_width
                    y1 = y1 + y // tile_height
            else:
                if x1 != x2 + x // tile_width or y1 != y2 + y // tile_height:
                    self.rect = self.rect.move(x, y)
                    x2 = x2 + x // tile_width
                    y2 = y2 + y // tile_height


def game():
    global username, steps, nLevel, menu_option
    player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                steps += 1
                if y1 > y2:
                    player1.update(0, tile_height, 1)
                    player2.update(0, tile_height, 2)
                else:
                    player2.update(0, tile_height, 2)
                    player1.update(0, tile_height, 1)
            elif key[pygame.K_UP]:
                steps += 1
                if y1 > y2:
                    player2.update(0, -tile_height, 2)
                    player1.update(0, -tile_height, 1)
                else:
                    player1.update(0, -tile_height, 1)
                    player2.update(0, -tile_height, 2)
            elif key[pygame.K_LEFT]:
                steps += 1
                if x1 > x2:
                    player2.update(-tile_width, 0, 2)
                    player1.update(-tile_width, 0, 1)
                else:
                    player1.update(-tile_width, 0, 1)
                    player2.update(-tile_width, 0, 2)
            elif key[pygame.K_RIGHT]:
                steps += 1
                if x1 < x2:
                    player2.update(tile_width, 0, 2)
                    player1.update(tile_width, 0, 1)
                else:
                    player1.update(tile_width, 0, 1)
                    player2.update(tile_width, 0, 2)
            elif key[pygame.K_ESCAPE]:
                menu()
                if menu_option == 3:
                    player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))
                    menu_option = 0
                elif menu_option == 1:
                    return
        if level_map[y1][x1] == 'p' and level_map[y2][x2] == 'p':
            menu_option = 1
            nLevel += 1

            tiles_group.draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
            pygame.time.wait(1000)
            player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        font = pygame.font.Font(None, 30)
        draw_text('Игрок: ' + username, font, (255, 255, 255), screen, 10, 805)
        draw_text('Уровень ' + str(nLevel), font, (255, 255, 255), screen, 400, 805)

        if steps < 1000000:
            draw_text('Сделано шагов: ' + str(steps), font, (255, 255, 255), screen, 550, 805)
        else:
            draw_text('Сделано очень много шагов', font, (255, 0, 0), screen, 515, 805)

        pygame.display.flip()


# Основной цикл программы
start_screen()
