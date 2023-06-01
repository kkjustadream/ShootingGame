import pygame
import math

pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font("assets/font/myFont.ttf", 32)  # freesansbold.ttf內建的
big_font = pygame.font.Font("assets/font/myFont.ttf", 60)
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

backgrounds = []
banners = []
guns = []
target_images = [[], [], []]
# target numbers for each level
targets = {1: [10, 5, 3],
           2: [12, 8, 5],
           3: [15, 12, 8, 3]}
level = 0  # menu is at level 0
points = 0
shot = False
total_shot = 0
# 0: freeplay, 1: accuracy, 2: time
mode = 0
ammo = 0
time_passed = 0
time_remaining = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_time = 0
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
# initialize enemy coordinates, according to the number of targets
one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]

# load images: put each level image into list
menu_img = pygame.image.load("assets/menus/mainMenu.png")
game_over_img = pygame.image.load("assets/menus/gameOver.png")
pause_img = pygame.image.load("assets/menus/pause.png")
for i in range(1, 4):
    # load image in game: pygame.image.load
    backgrounds.append(pygame.image.load(f"assets/backgrounds/{i}.png"))
    banners.append(pygame.image.load(f"assets/banners/{i}.png"))
    # scale gun from 500 to 100
    guns.append(pygame.transform.scale(pygame.image.load(f"assets/guns/{i}.png"), (100, 100)))
    # level 1, 2 have 3 size of targets, level 3 has 4
    if i < 3:
        for j in range(1, 4):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))
    else:
        for j in range(1, 5):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))

# read high scores from file
file = open("high_scores.txt", "r")
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_time = int(read_file[2])

# load sound effects
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/bg_music.mp3")
# Lower the background music volume
pygame.mixer.music.set_volume(0.15)
plate_sound = pygame.mixer.Sound("assets/sounds/Broken plates.wav")
plate_sound.set_volume(0.2)
bird_sound = pygame.mixer.Sound("assets/sounds/Drill Gear.mp3")
bird_sound.set_volume(0.2)
laser_sound = pygame.mixer.Sound("assets/sounds/Laser Gun.wav")
laser_sound.set_volume(0.2)
# play
pygame.mixer.music.play()

def draw_score(points):
    points_tex = font.render(f"Points: {points}", True, "black")
    screen.blit(points_tex, (320, 660))
    shots_text = font.render(f"Total Shots: {total_shot}", True, "black")
    screen.blit(shots_text, (320, 687))
    time_text = font.render(f"Time Elapsed: {time_passed}", True, "black")
    screen.blit(time_text, (320, 714))
    if mode == 0:
        mode_text = font.render(f"Freeplay", True, "black")
    elif mode == 1:
        mode_text = font.render(f"Ammo Remaining: {ammo}", True, "black")
    else:
        mode_text = font.render(f"Time Remaining: {time_remaining}", True, "black")
    screen.blit(mode_text, (320, 741))


def draw_gun():
    """
    draw the gun that will point to the mouse
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    gun_point = (WIDTH / 2, HEIGHT - 200)
    lasers = ["red", "purple", "green"]
    # index 0 1 2 -> (left, middle, right), if pressed change to 1
    clicks = pygame.mouse.get_pressed()
    if mouse_x != gun_point[0]:
        # get the slop of the mouse and the gun
        slop = (mouse_y - gun_point[1]) / (mouse_x - gun_point[0])
    else:
        slop = float("-inf")
    # get the angle(radius) of the mouse and the gun
    angle = math.atan(slop)
    rotation = math.degrees(angle)
    # if mouse is at left side，want gun pic to flip
    if mouse_x < gun_point[0]:
        # flip in x axis(True), not y axis(False)
        gun = pygame.transform.flip(guns[level - 1], True, False)
        # handle when pointing at banner(y > 600)，200 is banner height
        if mouse_y < HEIGHT - 200:
            # draw gun when in shooting area
            screen.blit(pygame.transform.rotate(gun, 90 - rotation),
                        (WIDTH / 2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], (mouse_x, mouse_y), 5)
    # don't need to flip
    else:
        gun = guns[level - 1]
        if mouse_y < HEIGHT - 200:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation),
                        (WIDTH / 2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], (mouse_x, mouse_y), 5)


def draw_level(coords):
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    else:
        target_rects = [[], [], [], []]
    # i size of target， 1,2 is 3 size, 3 is 4 size
    for i in range(len(coords)):
        # loop over all targets in same size
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),
                                                    (60 - i * 12, 60 - i * 12)))
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects


def move_level(coords):
    if level == 1 or level == 2:
        max_val = 3
    else:
        max_val = 4
    for i in range(max_val):
        for j in range(len(coords[i])):
            cur_coord = coords[i][j]
            # biggest size out of screen
            if cur_coord[0] < -150:
                coords[i][j] = (WIDTH, cur_coord[1])
            else:
                coords[i][j] = (cur_coord[0] - 2 ** i, cur_coord[1])
    return coords


def check_shot(targets, coords, points):
    # get the mouse position
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10 * (i ** 2)
                # add sounds ofr enemy hit
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    plate_sound.play()
                else:
                    laser_sound.play()
    return coords, points


def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, time_remaining, \
        points, total_shot, ammo, best_freeplay, best_ammo, best_time, write_values, clicked, new_coords
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    # draw invisible rect
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    screen.blit(font.render(f"{best_freeplay}", True, "black"), (340, 580))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f"{best_ammo}", True, "black"), (650, 580))
    time_button = pygame.rect.Rect((170, 661), (260, 100))
    screen.blit(font.render(f"{best_time}", True, "black"), (350, 710))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))
    # if we click on freeplay
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shot = 0
        points = 0
        clicked = True
        new_coords = True
    # if we click on ammo
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shot = 0
        points = 0
        clicked = True
        new_coords = True
    # if we click on time
    if time_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remaining = 40
        time_passed = 0
        total_shot = 0
        points = 0
        clicked = True
        new_coords = True
    # if we click reset
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_time = 0
        write_values = True
        clicked = True


def draw_gameover():
    global clicked, game_over, menu, points, time_passed, mode, pause, level,\
        total_shot, time_remaining
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    screen.blit(big_font.render(f"{display_score}", True, "black"), (650, 570))
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 0
        game_over = False
        clicked = True
        pause = False
        menu = True
        points = 0
        total_shot = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False


def draw_pause():
    global level, pause, menu, points, total_shot, time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 0
        pause = False
        menu = True
        points = 0
        total_shot = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True
        pygame.mixer.music.play()


run = True
while run:
    # if no tick, the game will run as fast as possible
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1

    if new_coords:
        # initialize enemy coordinates, according to the number of targets
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        new_coords = False

    screen.fill("black")
    screen.blit(backgrounds[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, HEIGHT - 200))

    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_gameover()
    if pause:
        level = 0
        draw_pause()

    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords, points = check_shot(target_boxes, one_coords, points)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords, points = check_shot(target_boxes, two_coords, points)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords, points = check_shot(target_boxes, three_coords, points)
            shot = False

    if level > 0:
        draw_gun()
        draw_score(points)

    # check quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # if the mouse is clicked, and the left button is pressed, don't want drag
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shot += 1
                if mode == 1:
                    ammo -= 1
            # click on pause button
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):
                resume_level = level
                pause = True
                clicked = True
            # click on reset button
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                menu = True
                pygame.mixer.music.play()
                clicked = True
                new_coords = True  # set to true everytime we go to menu

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1
    # game over condition
    if level == 3 and target_boxes == [[], [], [], []] or (mode == 1 and ammo == 0) \
            or (mode == 2 and time_remaining == 0):
        new_coords = True
        pygame.mixer.music.play()
        # check if it's high score
        if mode == 0:
            if time_passed < best_freeplay or best_freeplay == 0:
                best_freeplay = time_passed
                write_values = True
        if mode == 1:
            if points > best_ammo:
                best_ammo = points
                write_values = True
        if mode == 2:
            if points > best_time:
                best_time = points
                write_values = True

        game_over = True

    if write_values:
        file = open("high_scores.txt", "w")
        file.write(f"{best_freeplay}\n{best_ammo}\n{best_time}")
        file.close()
        write_values = False

    # flip is update the entire display surface at once
    pygame.display.flip()

pygame.quit()
