import pygame
import math

pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font("assets/font/myFont.ttf", 32)  # freesansbold.ttf內建的
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

backgrounds = []
banners = []
guns = []
level = 1      # menu is at level 0

# put each level image into list
for i in range(1, 4):
    # load image in game: pygame.image.load
    backgrounds.append(pygame.image.load(f"assets/backgrounds/{i}.png"))
    banners.append(pygame.image.load(f"assets/banners/{i}.png"))
    # scale gun from 500 to 100
    guns.append(pygame.transform.scale(pygame.image.load(f"assets/guns/{i}.png"), (100, 100)))

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



run = True
while run:
    # if no tick, the game will run as fast as possible
    timer.tick(fps)

    screen.fill("black")
    screen.blit(backgrounds[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, HEIGHT - 200))
    if level > 0:
        draw_gun()

    # check quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    # flip is update the entire display surface at once
    pygame.display.flip()

pygame.quit()