import pygame
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import tkinter.filedialog

# the input dialog
toptk = tk.Tk()
toptk.geometry("250x250+800+300")
toptk.update_idletasks()
toptk.withdraw()
username = ""
steps = 0
menu_option = 0
start_move = 0
# A variable to check for the status later
click = False

pygame.init()
size = width, height = 800, 800
size_all_screen = 800, 830

pygame.display.set_caption('За двоих')
FPS = 60
WIDTH = 800
HEIGHT = 830
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


tile_images = {'wall': load_image('wall.jpg'), 'portal': load_image('portal.png'), 'sand': load_image('sand.jpg'),
               'grass': load_image('grass.jpg'), 'snow': load_image('snow.png')}
player_images = [load_image('sp.png', -1),
                 load_image('spl.png', -1),
                 load_image('spr.png', -1),
                 load_image('spup.png', -1),
                 load_image('spdown.png', -1), ]

tile_width = tile_height = 50


def load_map(filename):
    global level_map
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global x1, y1, x2, y2, nLevel
    if nLevel == 1:
        ground = 'grass'
    if nLevel == 2:
        ground = 'sand'
    if nLevel == 3:
        ground = 'snow'
    if nLevel == 4:
        ground = 'grass'
    if nLevel == 5:
        ground = 'snow'
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
                Tile(ground, x, y)
            elif level[y][x] == 'p':
                Tile('portal', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile(ground, x, y)
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
    intro_text = ["Правила игры «За двоих»:",
                  "Для прохождения игры, необходимо пройти 5 уровней.",
                  "Чтобы пройти уровень, необходимо одновременно",
                  "ввести обоих персонажей в порталы.",
                  "Управление:",
                  "Движение осуществляется на стрелочки на клавиатуре;",
                  "Для вызова меню необходимо нажать кнопку 'ESCAPE'."]

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
                f = 1
                username = ''
                while f == 1:
                    username = simpledialog.askstring(initialvalue=username,
                                                      title="Новая игра", prompt="Введите желаемое имя пользователя:",
                                                      parent=toptk)
                    if username is None:
                        f = 2
                        continue
                    if len(username) > 25:
                        messagebox.showinfo('Ошибка имени пользователся',
                                            'Имя пользователя должно содержать 25 и меньше символов')
                    else:
                        f = 0
                if f != 2:
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
    try:
        with open(filename, 'r', encoding="utf-8") as mapFile:
            read_file = [line.strip() for line in mapFile]
    except UnicodeDecodeError:
        messagebox.showinfo('Load error', f'File {filename} cannot be opened.')
        return
    if len(read_file) != 7:
        messagebox.showinfo('Load error', f'File {filename} cannot be opened.')
        return
    is_file_correct = [read_file[1].isdigit(), read_file[2].isdigit(), isinstance(read_file[0], str),
                       read_file[3].isdigit(), read_file[4].isdigit(), read_file[5].isdigit(), read_file[6].isdigit()]
    if all(is_file_correct) == 0:
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
                menu_option = 0
                return
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click = True

        # defining functions when a certain button is pressed
        if button_1.collidepoint((mx, my)):  # main menu button with game ending
            if click:
                if tkinter.messagebox.askokcancel(
                        title='Information',
                        message='Are you sure you want to finish the game and go to the main menu'):
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
        self.image = player_images[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 5, tile_height * pos_y + 5)
        self.start_move_player = 0
        self.target_x = 0
        self.target_y = 0

    def update(self, x, y, p):
        global x1, y1, x2, y2, start_move
        if 0 <= self.rect.y + y < height and 0 <= self.rect.x + x < width and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@', 'p'):

            if p == 1:
                if x2 != x1 + x // tile_width or y2 != y1 + y // tile_height:
                    x1 = x1 + x // tile_width
                    y1 = y1 + y // tile_height
                    self.target_x = x
                    self.target_y = y
                    self.rect = self.rect.move(x // 2, y // 2)
                    if x > 0:
                        self.image = player_images[2]  # move right
                    elif x < 0:
                        self.image = player_images[1]  # move left
                    elif y < 0:
                        self.image = player_images[3]  # move up
                    elif y > 0:
                        self.image = player_images[4]  # move down
                    self.start_move_player = 1
                    start_move = 1
            else:
                if x1 != x2 + x // tile_width or y1 != y2 + y // tile_height:
                    x2 = x2 + x // tile_width
                    y2 = y2 + y // tile_height
                    self.target_x = x
                    self.target_y = y
                    self.rect = self.rect.move(x // 2, y // 2)
                    if x > 0:
                        self.image = player_images[2]  # move right
                    elif x < 0:
                        self.image = player_images[1]  # move left
                    elif y < 0:
                        self.image = player_images[3]  # move up
                    elif y > 0:
                        self.image = player_images[4]  # move down
                    self.start_move_player = 1
                    start_move = 1

    def update_end(self):
        if self.start_move_player == 1:
            self.rect = self.rect.move(self.target_x // 2, self.target_y // 2)
            self.image = player_images[0]
            self.start_move_player = 0


def game():
    global username, steps, nLevel, menu_option, start_move
    player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))

    run = True
    while run:
        if start_move == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                key = pygame.key.get_pressed()
                if key[pygame.K_DOWN]:
                    if y1 > y2:
                        player1.update(0, tile_height, 1)
                        player2.update(0, tile_height, 2)
                    else:
                        player2.update(0, tile_height, 2)
                        player1.update(0, tile_height, 1)
                    break
                elif key[pygame.K_UP]:
                    if y1 > y2:
                        player2.update(0, -tile_height, 2)
                        player1.update(0, -tile_height, 1)
                    else:
                        player1.update(0, -tile_height, 1)
                        player2.update(0, -tile_height, 2)
                    break
                elif key[pygame.K_LEFT]:
                    if x1 > x2:
                        player2.update(-tile_width, 0, 2)
                        player1.update(-tile_width, 0, 1)
                    else:
                        player1.update(-tile_width, 0, 1)
                        player2.update(-tile_width, 0, 2)
                    break
                elif key[pygame.K_RIGHT]:
                    if x1 < x2:
                        player2.update(tile_width, 0, 2)
                        player1.update(tile_width, 0, 1)
                    else:
                        player1.update(tile_width, 0, 1)
                        player2.update(tile_width, 0, 2)
                    break
                elif key[pygame.K_ESCAPE]:
                    menu()
                    if menu_option == 3:
                        player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))
                        menu_option = 0
                    elif menu_option == 1:
                        menu_option = 0
                        return

        else:
            pygame.time.wait(100)
            start_move = 0
            player1.update_end()
            player2.update_end()
            steps += 1
            if level_map[y1][x1] == 'p' and level_map[y2][x2] == 'p':
                menu_option = 1
                nLevel += 1
                tiles_group.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
                pygame.time.wait(500)
                if nLevel <= 5:
                    player1, player2 = generate_level(load_map(f'map{nLevel}.txt'))
                else:
                    end_screen()
                    if menu_option == 2:
                        return
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


def add_result():
    global steps, username
    con = sqlite3.connect('RESULTS.sqlite')
    cur = con.cursor()
    if cur.execute(f'SELECT * FROM result WHERE Name="{username}"').fetchall():
        if cur.execute(f'SELECT * FROM result WHERE Name="{username}"').fetchall()[0][0]:
            cur.execute(f"UPDATE result SET Steps={steps} WHERE Name='{username}'")
    else:
        cur.execute("INSERT INTO result VALUES(?, ?);", (username, steps))
    cur.execute("SELECT * FROM result ORDER BY Steps ASC")
    a = cur.fetchall()
    cur.execute('DELETE FROM result')
    s = []
    place = 0
    k = 0
    for i in a:
        k += 1
        if i[0] == username:
            place = k
        cur.execute("INSERT INTO result VALUES(?, ?);", i)
        s.append(i)
    con.commit()
    con.close()
    s = s[:10]
    m = []
    if steps % 10 == 0:
        m.append(f'Ваш результат: {place} место - {steps} шагов!')
    elif 20 > steps % 100 > 4:
        m.append(f'Ваш результат: {place} место - {steps} шагов!')
    elif steps % 10 == 1:
        m.append(f'Ваш результат: {place} место - {steps} шаг!')
    elif steps % 10 < 5:
        m.append(f'Ваш результат: {place} место - {steps} шага!')
    else:
        m.append(f'Ваш результат: {place} место - {steps} шагов!')
    if place <= 10:
        m.append("Теперь, список самых быстрых прохождений выглядит так:")
    else:
        m.append('Самые быстрые прохождения:')
    k = 0
    for i in s:
        k += 1
        if k != 10:
            if i[1] % 10 == 0:
                m.append(f'{k}. {i[0]}: {i[1]} шагов')
            elif 20 > i[1] % 100 > 4:
                m.append(f'{k}. {i[0]}: {i[1]} шагов')
            elif i[1] % 10 == 1:
                m.append(f'{k}. {i[0]}: {i[1]} шаг')
            elif i[1] % 10 < 5:
                m.append(f'{k}. {i[0]}: {i[1]} шага')
            else:
                m.append(f'{k}. {i[0]}: {i[1]} шагов')
        else:
            if i[1] % 10 == 0:
                m.append(f'{k}.{i[0]}: {i[1]} шагов')
            elif 20 > i[1] % 100 > 4:
                m.append(f'{k}.{i[0]}: {i[1]} шагов')
            elif i[1] % 10 == 1:
                m.append(f'{k}.{i[0]}: {i[1]} шаг')
            elif i[1] % 10 < 5:
                m.append(f'{k}.{i[0]}: {i[1]} шага')
            else:
                m.append(f'{k}.{i[0]}: {i[1]} шагов')
    return m[0], m[1:]


def end_screen():
    global steps, nLevel, username, click, menu_option
    your_result, end_text = add_result()
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    font = pygame.font.Font(None, 30)
    font_head = pygame.font.Font(None, 50)
    while True:
        screen.blit(fon, (0, 0))
        draw_text('Поздравляем! Вы прошли игру!', font_head, (255, 0, 255), screen, 127, 50)
        draw_text(your_result, font, (0, 0, 0), screen, 197, 112)
        text_coord = 150
        for line in end_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        mx, my = pygame.mouse.get_pos()
        # creating buttons
        button_1 = pygame.Rect(300, 600, 200, 50)
        button_3 = pygame.Rect(300, 680, 200, 50)

        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_3)

        # writing text on top of button
        draw_text('MAIN MENU', font, (255, 255, 255), screen, 343, 615)
        draw_text('EXIT', font, (255, 255, 255), screen, 375, 695)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click = True

        # defining functions when a certain button is pressed
        if button_1.collidepoint((mx, my)):  # main menu button in end_screen
            if click:
                menu_option = 2
                nLevel = 0
                username = ''
                steps = 0
                return

        if button_3.collidepoint((mx, my)):  # exit button
            if click:
                terminate()

        pygame.display.flip()
        clock.tick(FPS)


# Запуск программы
start_screen()
