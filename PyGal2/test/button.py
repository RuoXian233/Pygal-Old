import sys

import pygame
from pygame import SRCALPHA


class Button(object):
    ##As a Button,these properties are necessary:
    ##A RECT:Contains the pos and size
    ##THE label:A micro text
    ##THE Image:decide the LOOK of the button
    def __init__(self, pos, size, image, font, clickEvent = None,label='', onHover = None,bgcolor=None, fontSize=24):
        self.pos = pos
        self.size = size
        self.surface = pygame.Surface(size, SRCALPHA)
        self.hoverImage = onHover

        self.fontColor = (0xFF, 0xFF, 0xFF)

        ##To make sure the function is'n too long
        ##I split the code to three functions
        self.image = self.__LoadImage(image, bgcolor, resize=True)
        self._image = self.__LoadImage(onHover, bgcolor, resize = True)
        self.font = self.__LoadFont(font, fontSize)
        self.label = label
        self.click = clickEvent
        self.onChange = False

        self.__Combination(self.image)

    def __LoadImage(self, image, bgcolor, resize: bool = True):
        ## Use the pure color
        if bgcolor != None:
            try:
                self.surface.fill(bgcolor)
            except pygame.error:
                print('Cannot use the color')
                raise SystemExit
            return self.surface
        ## Use a image
        else:
            try:
                Image = pygame.image.load(image).convert_alpha()
            except pygame.error:
                print('Could not load the image')
                raise SystemExit
            if resize:
                Image = pygame.transform.scale(Image, self.size)
            return Image

    ##Maybe I should consider reuse the code
    ##Now It is stupid
    def __LoadFont(self, font, fontSize):
        try:
            font = pygame.font.Font(font, fontSize)
        except pygame.error as message:
            print('Cannot load font:', font)
            raise SystemExit(message)
        return font

    def __Combination(self, img):
        Image = img
        labelSurface = self.font.render(self.label, True, self.fontColor)
        xPos = (Image.get_width() - labelSurface.get_width()) / 2
        yPos = (Image.get_height() - labelSurface.get_height()) / 2
        Image.blit(labelSurface, (xPos, yPos))
        self.surface.blit(Image, (0, 0))

    def render(self, surface, event):
        if self._onHover() and self.hoverImage:
            self.__Combination(self._image)
        else:
            self.__Combination(self.image)

        x, y = self.pos
        w, h = self.surface.get_size()
        x -= w / 2
        y -= h / 2
        surface.blit(self.surface, (x, y))
        self._onClick(event, self.click)

    ## check one point is in THIS BUTTON
    ## Orz,repeat codes....I'm lazy...
    def is_over(self, point):
        x, y = self.pos
        w, h = self.surface.get_size()
        x -= w / 2
        y -= h / 2
        rect = pygame.Rect((x, y), self.size)
        return rect.collidepoint(point)

    def get_pos(self):
        return self.pos

    def get_surface(self):
        return self.surface

    def get_rect(self):
        return self.surface.get_rect()

    def _onClick(self, event, click):
        if self.is_over(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            click()

    def _onHover(self):
        return self.is_over(pygame.mouse.get_pos())

pygame.init()
screen = pygame.display.set_mode([600, 450], pygame.RESIZABLE)

btn = Button([180, 108], [100, 45], './assets/Img/Button/Button_1.png', onHover='./assets/Img/Button/Button_2.png', font = './assets/Font/default.ttf', label='Hello', clickEvent=lambda: print('Hello'))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        btn.render(screen, event)

    pygame.display.update()
