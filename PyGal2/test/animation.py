import pygame, os
from pygame.locals import * #  if dont have, then first : pip install pygame

# Center the Application
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Initialize the modules
pygame.init()

# ==========================VARIABLES===============================
y1 = 1
y2 = 0
y3 = 0
x1 = 0
speed1 = 0.3
speed2 = 0.1
speed3 = 0.1
speed4 = 0.2
bgColor = 0, 0, 0
barHeight = 75
barWidth = 25
screen_width = 800
screen_height = 600
display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rashidin's Pygame Simple Animation🦅")
progress = True
barcolor1 = (255, 0, 0)
barcolor2 = (0, 255, 0)
barcolor3 = (0, 0, 255)
barcolor4 = (255, 255, 255)

# ===========================MAIN LOOP===============================
while progress:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        progress = False
        pygame.quit()
        quit()

    display.fill((bgColor))

    for i in range(0, barHeight):
        pygame.draw.line(display, barcolor1, (0, y1 + i), (screen_width - 1, y1 + i))

    y1 += speed1

    if y1 + barHeight > screen_height - 1 or y1 < 0:
        speed1 *= -1

    for i in range(0, barHeight):
        pygame.draw.line(display, barcolor2, (0, y2 + i), (screen_width - 1, y2 + i))

    y2 += speed2

    if y2 + barHeight > screen_height - 1 or y2 < 0:
        speed2 *= -1

    for i in range(0, barHeight):
        pygame.draw.line(display, barcolor3, (0, y3 + i), (screen_width - 1, y3 + i))

    y3 += speed3

    if y3 + barHeight > screen_height - 1 or y3 < 0:
        speed3 *= -1

    for i in range(0, barWidth):
        pygame.draw.line(display, barcolor4, (x1 + i, 0), (x1 + i, screen_height - 1))

    x1 += speed4

    if x1 + barWidth > screen_width - 1 or x1 < 0:
        speed4 *= -1

    pygame.display.flip()


