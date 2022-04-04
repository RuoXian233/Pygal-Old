import os
import sys
import time
import pygame
import threading
import traceback
import pygame_menu

from abc import ABCMeta
from abc import abstractmethod


class GameBase(metaclass=ABCMeta):
    @abstractmethod
    def start(self) -> int: ...

    @abstractmethod
    def update(self) -> None: ...


class Controls(metaclass=ABCMeta):
    @abstractmethod  
    def render(self) -> None: ...

    @abstractmethod
    def size(self) -> tuple[int, int]: ...

    @abstractmethod
    def pos(self) -> tuple[int, int]: ...

    @abstractmethod
    def centre(self) -> tuple[int, int]: ...


class SpriteBase(Controls):
    @abstractmethod
    def _next_action(self): ...


class Window(Controls):
    def __init__(
            self,
            size: tuple[int, int] = ...,
            title: str = ...,
            icon: str = None,
            flags: int = 0
        ) -> None:
        try:
            self.elements: list[Controls] = []
            self.title = 'Game' if title == Ellipsis else title
            self.icon = None if icon == Ellipsis else icon
            self.current_window_size = (640, 480) if size == Ellipsis else size
            self.surface = pygame.display.set_mode(self.current_window_size, flags)
            self.window_event: pygame.event.Event = None
        except Exception as e:
            traceback.print_exc()

        if self.icon:
            pygame.display.set_caption(self.title, self.icon)
        else:
             pygame.display.set_caption(self.title)

    def render(self):
        if self.elements:
            for e in self.elements:
                e.render()

        pygame.display.flip()

    def pos(self):
        return self.surface.get_rect()[0:2]

    def size(self):
        return self.current_window_size

    def centre(self):
        return (
            self.pos()[0] + self.size()[0] // 2,
            self.pos()[1] + self.size()[1] // 2
        )

    def add(self, element: Controls):
        self.elements.append(element)


class Image(Controls):
    def __init__(
            self, 
            parent: Window,
            src: str, 
            lt_pos: tuple[int, int],
            size: object = None
       ) -> None:
        self.parent = parent
        self.src = src
        self._pos = lt_pos
        self.size = size
        self.load()

    def load(self):
        try:
            self.surface = pygame.image.load(self.src)
        except Exception as e:
            traceback.print_exc()

    def render(self):
        try:
            if not self.size:
                pygame.transform.scale(self.surface, self.parent.size())
            self.parent.surface.blit(self.surface, self._pos)
        except Exception as e:
            traceback.print_exc()

    def pos(self):
        return self._pos

    def size(self):
        self.surface.get_size()

    def centre(self):
        return (
            self.pos()[0] + self.size()[0] // 2,
            self.pos()[1] + self.size()[1] // 2
        )


class Sprite(SpriteBase):
    def __init__(self):
        self.current_action: Image = None
        self.action_duration = 0
        self.action_count = 0
        self.actions: dict[str, list[Image]] = {}
        self.state = None

    def render(self):
        pass

    def _next_action(self):
        pass

    def size(self):
        pass

    def pos(self):
        pass

    def centre(self):
        pass


class Game(GameBase):
    def __init__(
            self, 
            main_window: Window,
            avg_fps: int = 30
        ) -> None:
        self.window = main_window
        self.event = None
        self.deltatime = 30 / 1000
        self.clock = 0

    def start(self) -> int:
        ret = pygame.init()
        return ret

    def update(self):
        for e in pygame.event.get():
            self.event = e
            if self.event.type == pygame.QUIT:
                sys.exit()
            else:
                self.window.render()
                time.sleep(self.deltatime)
                self.clock += 1

