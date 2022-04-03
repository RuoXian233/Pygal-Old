from __future__ import annotations

import abc
import inspect
import logging

import os
import sys
import time
import json
import traceback
import tkinter as tk
import xml.dom.minidom

import pygame

# TODO: Unfixed Bug #1: Color of Text cannot be set accurated

class Utils(object):
    @staticmethod
    def fromNameToPath(name: str, elementType: str) -> str | None:
        if elementType == 'image':
            basePath = './assets/Img/'
        elif elementType == 'font':
            basePath = './assets/Font/'
        elif elementType == 'music':
            basePath = './assets/Music/'
        elif elementType == 'sprite':
            basePath = './assets/Sprite/'
        elif elementType == 'scene':
            basePath = './assets/Scene/'
        else:
            raise ValueError(Consts.Errors.UTILS_PARAM_TYPE_ERR.format(elementType))

        if os.path.exists(basePath + name):
            return basePath + name
        else:
            raise FileNotFoundError(Consts.Errors.UTILS_FILE_NOT_FOUND.format(basePath + name + '/'))

class Exceptions(object):
    # Runtime Error may caused by source & code
    class GameError(Exception):
        pass

    # on-Compile Error while loading the script
    class ScriptError(Exception):
        pass

# Class used to store some basic parameters
class Consts(object):
    class Errors:
        ERROR_IN_RES_DICT = 'Cannot identify resources in "{}", unexpected syntax.'
        SCENE_TAG_REDEFINED = '[File "{}"] Tag "[{}]" defined more than once.'
        NULL_VALUE = 'Null value is not support for tag "{}".'
        NO_BODY_NODE = '[Syntax] Missing game body in file "{}". ("<body>" tag)'
        REPEAT_VALUE = 'Tag "{}" can only accept 1 value, but got {}.'
        REPEAT_TAG = 'Tag "{}" appeared more than once.'
        LOG_PARAM_ERR = 'Unknown value for "setLevel(::str)".'
        UTILS_PARAM_TYPE_ERR = 'Unexpected type value got ({}).'
        UTILS_FILE_NOT_FOUND = '"{}" not exists.'
        RENDER_EXCEPTION_FONT_LOAD = 'Font object is not loaded.'
        NO_SCENE_FORWARD = 'No scene forward since scene-{}.'
        CONTENT_TOO_LONG = 'Too long content is not supported. ({} chars > 25 char for title | 90 chars for text).'
        CHOICES_TOO_MANY = 'Too many choices!'
        NO_START_NODE = 'File "{}" cannot be identfied as a Pygal script file, missing start node (<Pygal>).'
        NO_HEAD_NODE = '[Syntax] Missing meta data ("<head>" tag) in file "{}".'
        NO_SCENE_TAG = '[File "{}"] Unable to find tag: "[{}]".'

    class Nums:
        FONT_K = 1.5
        TEXTFIELD_WIDTH_RATIO = 3.5
        TEXTFIELD_CHAR_LIMIT = 30
        FONT_SIZE_MAX = 35
        FONT_SIZE_MIN = 9
        NAME_FONT_SIZE = 27
        TEXTFIELD_LINE_COLOR = (0xCB, 0xEE, 0xBC)
        LOWEST_FPS = 3
        SPRITE_HEIGHT_RAITO = 1.25
        SPRITE_WIDTH_RATIO = 2

    class SceneTypes:
        START_PAGE = -1
        DEFAULT = 0
        END_PAGE = 1
        SAVE_AND_LOAD_PAGE = 114514

    class BgmMode:
        STOP = -1
        KEEP = 0
        CHANGE = 1

    class Literals:
        DEFAULT_CHOICE_BTN_1 = Utils.fromNameToPath('Button/Button_1.png', 'image')
        DEFAULT_CHOICE_BTN_2 = Utils.fromNameToPath('Button/Button_2.png', 'image')

class _Logger(object):
    '''Class that with many logging Utils, based on built-in module logging'''

    def __init__(self):
        self.currentTime = time.strftime('%y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)
        if not os.path.exists(os.getcwd() + '/game_logs/'):
            os.mkdir(os.getcwd() + '/game_logs/')
        self.fileLogger = logging.FileHandler(os.getcwd() + '/game_logs/' + self.currentTime + '_log.log', mode='w')
        self.fileLogger.setLevel(logging.NOTSET)
        self.formatter = logging.Formatter(
            '[%(asctime)s] [PyGal-Engine: line %(lineno)d, in \'%(funcName)s()\'] <%(levelname)s:%(levelno)s> %(message)s')
        self.fileLogger.setFormatter(self.formatter)
        self.consoleLogger = logging.StreamHandler()
        self.consoleLogger.setLevel(logging.NOTSET)
        self.consoleLogger.setFormatter(self.formatter)
        self.logger.addHandler(self.consoleLogger)
        self.logger.addHandler(self.fileLogger)

    # A interface which can get current stack-call info and format.
    def formatStackInfo(self) -> str:
        string = '\n' + '*' * 10 + '<Stack Trace>' + '*' * 10 + '\n'
        i = 0
        for stack in inspect.stack():
            i += 1
            string += f'{(i - 1) * " "}At: {stack.filename} => "{stack.function}", with {stack.frame.f_code.co_varnames}({stack.frame.f_code.co_argcount}). [line:{stack.lineno}, size:{stack.frame.f_code.co_stacksize}]\n'
        return string

    # A special function to log error
    def error(self, exc: Exception = None, stackTrace: bool = False):
        if exc:
            sys.stderr.write('*' * 10 + '<Error>' + '*' * 10 + '\n')
            self.logger.error(f'Fatal Error: {exc}.')
            self.logger.error(f'Details: \n {traceback.format_exc()}')
            sys.stderr.write('*' * 27 + '\n')
        else:
            self.logger.error(f'Unhandled Exception Details: \n {traceback.format_exc()}')

        if stackTrace:
            self.logger.info(self.formatStackInfo())

# The class to help load every resource in the game
# Custom textblock style and button style may used this
class ResourcesConfiguration(object):
    def __init__(self, resFile: os.PathLike[str]):
        self.res = self._getResourcePaths(resFile)

    def _getResourcePaths(self, resourceDictionary: os.PathLike[str]) -> dict:
        res = {
            'Button': {},
            'Textfield': None
        }

        with open(resourceDictionary, 'r') as f:
            _res = f.readlines()

        # Parse the syntax like: Button::hover=a.png
        #                          ^       ^    ^
        #                              a[0]=b      a[1]
        #                         b[0]      b[1]
        for r in _res:
            if r.split('::')[0] == 'Button':
                try:
                    _state = r.split('::')[1].strip()
                    _stateName = _state.split('=')[0]
                    _stateValue = _state.split('=')[1].strip()
                    res['Button'][_stateName] = _stateValue
                except IndexError:
                    raise Exceptions.GameError(Consts.Errors.ERROR_IN_RES_DICT.format(resourceDictionary))

        # Textfield:b.png
            elif r.startswith('Textfield'):
                try:
                    _name = r.split('=')[0]
                    _value = r.split('=')[1].strip()
                    res[_name] = _value
                except IndexError:
                    raise Exceptions.GameError(Consts.Errors.ERROR_IN_RES_DICT.format(resourceDictionary))

        # print(res)
        for k, v in res.items():
            if k == 'Button':
                if v['normal'] == 'default':
                    v['normal'] = Consts.Literals.DEFAULT_CHOICE_BTN_1
                if v['hover'] == 'default':
                    v['hover'] = Consts.Literals.DEFAULT_CHOICE_BTN_2

            elif k == 'Textfield':
                if v == 'default':
                    v = None

        return res

    def getValue(self, tag: str) -> str:
        return self.res[tag]

# The base class of every controls on the window except Music & background image
class ControlElements(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    # Set the style like color, fontsize...
    @abc.abstractmethod
    def configureStyle(self, **style): ...

    # Call every time in the main method: renderAll()
    @abc.abstractmethod
    def render(self, event: pygame.event.Event): ...

    # Return the left-top position of an element
    @abc.abstractmethod
    def getPos(self): ...

    # Return the width, height of an element
    @abc.abstractmethod
    def getSize(self): ...

    # Return the rect property which like (lt.x, lt.y, w, h)
    @abc.abstractmethod
    def getRect(self): ...


# The base class of every intractable element
class UIElements(ControlElements, metaclass=abc.ABCMeta):
    def __init__(self, onClick=None):
        super(UIElements, self).__init__()
        self.clickEvent = onClick

    @abc.abstractmethod
    def _onClick(self): ...

    def changeClickTrigger(self, event):
        self.clickEvent = event

    def _click(self):
        if self._onClick():
            self.clickEvent()


# Implements the Button Controls:
class Button(UIElements):
    def __init__(self, parent: pygame.Surface, pos: tuple, size: tuple, text: str, click=None, font: str = None,
                 fontsize: int = None,
                 image: str = None, hoverImage: str = None, fontColor: tuple[int, int, int] = None):
        try:
            super(UIElements).__init__()

            self.parent = parent
            self.size = size
            self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
            self.pos = pos
            self.text = text
            # The on-click trigger function
            self.clickEvent = click
            # when the mouse is on the button, change the appearance of Button
            self.hoverImage = hoverImage

            if not font:
                _font = Utils.fromNameToPath('default.ttf', 'font')
                self.font = _font
            else:
                self.font = font

            if not image:
                _image = Utils.fromNameToPath('Button/default.png', 'image')
                self.image = _image
            else:
                self.image = image

            if not fontsize:
                # Get the fit fontsize by button-size & length of text sequence.
                _fontsize = int(self.size[0] // len(self.text) * Consts.Nums.FONT_K)

                if _fontsize > Consts.Nums.FONT_SIZE_MAX:
                    _fontsize = 35
                elif _fontsize < Consts.Nums.FONT_SIZE_MIN:
                    _fontsize = 9
                self.fontsize = _fontsize
            else:
                self.fontsize = fontsize

            if not fontColor:
                self.fontColor = (0xFF, 0xFF, 0XFF)
            else:
                self.fontColor = fontColor
        except Exception as e:
            raise Exceptions.GameError(e)

    # change the property defined in __init__()
    def configureStyle(self, **style):
        try:
            self.pos = style['pos']
        except KeyError:
            pass

        try:
            self.size = style['size']
        except KeyError:
            pass

        try:
            self.text = style['text']
        except KeyError:
            pass

        try:
            self.image = style['image']
        except KeyError:
            pass

        try:
            self.hoverImage = style['hoverImage']
        except KeyError:
            pass

        try:
            self.font = style['font']
        except KeyError:
            pass

        try:
            self.fontsize = style['fontSize']
        except KeyError:
            pass

        try:
            self.fontColor = style['fontColor']
        except KeyError:
            pass

    def __loadFont(self):
        try:
            self.fontObject = pygame.font.Font(self.font, self.fontsize)
        except pygame.error as e:
            raise Exceptions.GameError(e)

    def __loadImages(self) -> list[pygame.Surface]:
        try:
            # load the current image file to pygame image object
            surfaces = [pygame.transform.scale(pygame.image.load(self.image), self.size)]
            if self.hoverImage:
                surfaces.append(pygame.transform.scale(pygame.image.load(self.hoverImage), self.size))

            return surfaces
        except Exception as e:
            raise Exceptions.GameError(e)

    def __renderText(self) -> pygame.Surface:
        try:
            self.__loadFont()
            # display the text on the button
            if self.fontObject:
                return self.fontObject.render(self.text, True, self.fontColor)
            else:
                raise Exceptions.GameError(Consts.Errors.RENDER_EXCEPTION_FONT_LOAD)
        except Exception as e:
            raise Exceptions.GameError(e)

    def _update(self):
        # Update called in _render() triggered by condition
        try:
            image, hoverImage = self.__loadImages()
            hoverImageExists = True
        except Exception:
            image = self.__loadImages()[0]
            hoverImageExists = False

        labelSurface = self.__renderText()

        # Centre layout
        xPos = (image.get_width() - labelSurface.get_width()) / 2
        yPos = (image.get_height() - labelSurface.get_height()) / 2

        try:
            # The effect of mouse hover
            if self._onHover() and hoverImageExists:
                hoverImage.blit(labelSurface, (xPos, yPos))
                self.surface.blit(hoverImage, (0, 0))
            else:
                image.blit(labelSurface, (xPos, yPos))
                self.surface.blit(image, (0, 0))
        except Exception as e:
            raise Exceptions.GameError(e)

    # Return if a point is on the surface area of Button
    def _isPointOn(self, point: tuple) -> bool:
        x, y = self.pos
        w, h = self.surface.get_size()
        x -= w / 2
        y -= h / 2
        rect = pygame.Rect((x, y), self.size)
        return rect.collidepoint(point)

    # Return if the mouse click the Button
    def _onClick(self, event: pygame.event.Event) -> bool:
        return self._isPointOn(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN

    def _onHover(self) -> bool:
        return self._isPointOn(pygame.mouse.get_pos())

    # All below three method are getters which implements the abstract method in UIElements
    def getPos(self):
        return self.pos

    def getRect(self):
        return self.surface.get_rect()

    def getSize(self):
        return self.size

    def render(self, event: pygame.event.Event):
        try:
            self._update()

            if self._onClick(event):
                self.clickEvent()

            x, y = self.pos
            w, h = self.size
            x -= w / 2
            y -= h / 2

            self.parent.blit(self.surface, (x, y))
        except Exception as e:
            raise Exceptions.GameError(e)

# An area to show text in game
class TextField(ControlElements):
    def __init__(self, parent: pygame.Surface, font: str = None, fontsize: int = None, nameFontColor: tuple = None,
                 textFontColor: tuple = None, ui: os.PathLike[str] = None):
        self.parent = parent
        # Adjust the size by the parent window size, fills the widow and use 1/4 of height
        self.size = self.parent.get_size()[0], self.parent.get_size()[1] / Consts.Nums.TEXTFIELD_WIDTH_RATIO
        # the true alpha value => self.alpha * 255
        self.alpha = 125
        self.text = ''
        self.name = ''
        self.lineLength = len(self.name) * 10
        self.lineColor = (0xFF, 0xFF, 0xFF)
        self.fontsize = fontsize
        self.ui = ui

        if not nameFontColor:
            self.nameFontColor = (0xFF, 0XFF, 0xFF)
        else:
            self.nameFontColor = nameFontColor

        if not textFontColor:
            self.textFontColor = (0xFF, 0xFF, 0xFF)
        else:
            self.textFontColor = (0xFF, 0xFF, 0xFF)

        if not font:
            _font = Utils.fromNameToPath('default.ttf', 'font')
            self.font = _font

        self.rectArea = pygame.Surface(self.size)

    def configureStyle(self, **style):
        try:
            try:
                self.lineLength = style['length']
            except KeyError:
                pass

            try:
                self.lineColor = style['color']
            except KeyError:
                pass

            try:
                self.alpha = style['alpha']
            except KeyError:
                pass

            try:
                self.nameFontColor = style['nameColor']
            except KeyError:
                pass

                self.textFontColor = style['textColor']
            except KeyError:
                pass
        except KeyError:
            pass

    def setText(self, text: str):
        self.text = text

    def setName(self, name: str):
        self.name = name

    def __renderRect(self):
        if self.ui == 'default':
            self.rectArea = pygame.Surface(self.size)
            # Create a pure black rectangle
            self.rectArea.fill([0, 0, 0])
            # Set its transparency key to given value
            self.rectArea.set_alpha(self.alpha)

        else:
            try:
                self.rectArea = pygame.Surface(self.size)
                # Use custome image as the textfield ui
                _uiIMG = pygame.transform.scale(pygame.image.load(self.ui), self.size)
                self.rectArea.blit(_uiIMG, (0, 0))
            except Exception as e:
                raise Exceptions.GameError(f'Runtime-rendering Error: {e}.')

            # Draw the image but no transparency
            self.rectArea.blit(_uiIMG, (0, 0))

    def __renderFont(self):
        # Calculate the fit fontsize
        try:
            if len(self.text) < 30:
                self.fontsize = int(self.size[0] // len(self.text) * Consts.Nums.FONT_K / 5)
            elif 30 < len(self.text) < 60:
                self.fontsize = int(self.size[0] // len(self.text) * Consts.Nums.FONT_K / 5 * 4)
            else:
                self.fontsize = int(self.size[0] // len(self.text) * Consts.Nums.FONT_K / 5 * 6)

            # Load fonts for display text
            self._textFontObject = pygame.font.Font(self.font, self.fontsize)
            self._nameFontObject = pygame.font.Font(self.font, Consts.Nums.NAME_FONT_SIZE)
        except Exception as e:
            raise Exceptions.GameError(e)

    def __renderName(self):
        # Load font before show text
        self.__renderFont()
        print(self.nameFontColor)
        nameTextSurface = self._nameFontObject.render(self.name, True, self.nameFontColor)
        # It's position is (20, 10) => looks better
        self.rectArea.blit(nameTextSurface, (20, 10))

    def __renderLine(self):
        if len(self.name) > 25:
            raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(self.name)))

        _textLineLength = len(self.name) * 10
        # Draw a line to seperate name & text
        _line = pygame.draw.line(self.rectArea, Consts.Nums.TEXTFIELD_LINE_COLOR,
                                 (25, 10 + Consts.Nums.NAME_FONT_SIZE + 10),
                                 (25 + _textLineLength, 20 + Consts.Nums.NAME_FONT_SIZE), width=2)

    # The most important work it does is format multy-line text
    def __renderText(self):
        try:
            if 60 > len(self.text) > 30:
                # Divide the content => two parts to two lines
                _part1 = self.text[0:31]
                _part2 = self.text[31:]

                print(self.textFontColor)
                _textSurface1 = self._textFontObject.render(_part1, True, self.textFontColor)
                _textSurface2 = self._textFontObject.render(_part2, True, self.textFontColor)

                # For the scene have no dialog
                if self.name:
                    self.rectArea.blit(_textSurface1, (35, 30 + Consts.Nums.NAME_FONT_SIZE))
                    self.rectArea.blit(_textSurface2, (35, 30 + Consts.Nums.NAME_FONT_SIZE + self.fontsize))
                else:
                    self.rectArea.blit(_textSurface1, (10, 10))
                    self.rectArea.blit(_textSurface2, (10, 10))

            elif 90 > len(self.text) > 60:
                # Render three lines like that:
                _part1 = self.text[0:31]
                _part2 = self.text[31:61]
                _part3 = self.text[61:]

                _textSurface1 = self._textFontObject.render(_part1, True, self.textFontColor)
                _textSurface2 = self._textFontObject.render(_part2, True, self.textFontColor)
                _textSurface3 = self._textFontObject.render(_part3, True, self.textFontColor)

                if self.name:
                    self.rectArea.blit(_textSurface1, (35, 30 + Consts.Nums.NAME_FONT_SIZE))
                    self.rectArea.blit(_textSurface2, (35, 30 + Consts.Nums.NAME_FONT_SIZE + self.fontsize))
                    self.rectArea.blit(_textSurface3, (35, 30 + Consts.Nums.NAME_FONT_SIZE + 2 * self.fontsize))
                else:
                    self.rectArea.blit(_textSurface1, (10, 10))
                    self.rectArea.blit(_textSurface2, (10, 10))
                    self.rectArea.blit(_textSurface3, (10, 10))

            elif 90 < len(self.text):
                raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(self.text)))

            else:
                # If text is short, pass the format step, render in a single line
                _textSurface = self._textFontObject.render(self.text, True, self.textFontColor)
                if self.name:
                    self.rectArea.blit(_textSurface, (35, 30 + Consts.Nums.NAME_FONT_SIZE))
                else:
                    self.rectArea.blit(_textSurface, (10, 10))

        except Exception as e:
            # raise Exceptions.GameError(e + '\nMaybe window is too small?')
            pass

    def render(self, screenSize: tuple):
        # Redraw textfield if window resized:
        if self.size[0] != screenSize[0]:
            _size = screenSize[0], screenSize[1] / Consts.Nums.TEXTFIELD_WIDTH_RATIO
            self.size = _size

        self.__renderRect()
        self.__renderName()
        self.__renderLine()
        self.__renderText()

        self.parent.blit(self.rectArea, [0, self.parent.get_size()[1] - self.size[1]])

    def getRect(self):
        return self.rectArea.get_rect()

    def getPos(self):
        return self.rectArea.get_rect()[0:2]

    def getSize(self):
        return self.size

# A class which parsed every single scene file
class SceneParser(object):
    def __init__(self):
        pass
        # Judge if the tag is closed
        # For optional choice content, its default value is None

    def _parseTag(self, _content: str):
       # Get the scene info from a json file
        try:
            _scene = json.loads(_content)
        except Exception as e:
            raise Exceptions.ScriptError(f'Json decoding error: {e}.')

        # Check if missing property
        try:
            _tmp = _scene['scene-id']
        except KeyError:
            raise Exceptions.ScriptError(Consts.Errors.NO_SCENE_TAG.format(self.file, 'scene-id'))

        try:
            _tmp = _scene['scene']['text']
        except KeyError:
            raise Exceptions.ScriptError(Consts.Errors.NO_SCENE_TAG.format(self.file, 'text'))

        for k, v in _scene.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if v2:
                        if k2 == 'background-image':
                            if v[k2].startswith('~'):
                                _scene[k][k2] = Utils.fromNameToPath(v[k2].lstrip('~'), 'image')
                        elif k2 == 'bgm':
                            if v[k2].startswith('~'):
                                _scene[k][k2] = Utils.fromNameToPath(v[k2].lstrip('~'), 'music')
                        elif k2 == 'sprite':
                            if v[k2].startswith('~'):
                                _scene[k][k2] = Utils.fromNameToPath(v[k2].lstrip('~'), 'sprite')

        sceneParams = SceneParameters()
        sceneParams.set(
            idNum = _scene['scene-id'],
            name = _scene['scene']['name'],
            text = _scene['scene']['text'],
            background = _scene['scene']['background-image'],
            bgm = _scene['scene']['bgm'],
            sprite = _scene['scene']['sprite'],
            choices = _scene['scene']['choices']
        )

        return sceneParams
        # print(sceneParams.idNum, sceneParams.name, sceneParams.text, sceneParams.background, sceneParams.bgm, sceneParams.sprite, sceneParams.choices)


    def parse(self, path: os.PathLike[str]) -> SceneParameters:
        self.file = path

        with open(path, 'r', encoding = 'utf-8') as f:
            # Read the file by line
            content = f.read()

        # print(self._content)
        return self._parseTag(content)

# The class used to parse script and generate scene
class Parser(object):
    def __init__(self):
        self.script = None
        self.startupParam = {
            'size': '800,600',
            'title': 'Pygal',
            'icon': '',
            'resizable': 'true',
            'dynamicRender': 'true'
        }
        self.author = ''
        self.version = ''
        self.scenes = []

    # Format the param from xml to the python-dict
    def _formatParam(self):
        for i in self._parameters:
            self.startupParam[i[0][1]] = i[1][1]

    def _parseScript(self):
        # Parse the xml format of script file
        # The basic step is:
        # 1. Check if the tag exists
        # 2. Check the amount of the tag
        # 3. Check the amount of the value of the tag
        # 4. Get the value from the tag object

        _scriptTree = xml.dom.minidom.parse(self.script)
        if not _scriptTree.getElementsByTagName('Pygal'):
            raise Exceptions.ScriptError(Consts.Errors.NO_START_NODE.format(self.script))
        
        if len(_scriptTree.getElementsByTagName('Pygal')) != 1:
            raise Exceptions.ScriptError(Consts.Errors.REPEAT_TAG.format('Pygal'))
        
        _collection: xml.dom.minidom.Document = _scriptTree.documentElement
        if len(_collection.getElementsByTagName('head')) != 0:
            _head = _collection.getElementsByTagName('head')
            # Ignore errors: redefine <head>
            if len(_head) != 1:
                raise Exceptions.ScriptError(Consts.Errors.REPEAT_TAG.format('head'))
            _head = _head[0]

            # Get info inside Head tag
            # Get the startup info
            self._parameters = []
            if len(_head.getElementsByTagName('start')) != 0:
                # Get the property inside xml tag
                _startinfo = _head.getElementsByTagName('parameter')
                if len(_startinfo) != 0:
                    _startinfo = _head.getElementsByTagName('parameter')
                    for info in _startinfo:
                        self._parameters.append(info.attributes.items())

            if self._parameters:
                self._formatParam()

            # Get author & version info
            if len(_head.getElementsByTagName('author')) != 0:
                if len(_head.getElementsByTagName('author')) > 1:
                    raise Exceptions.ScriptError(Consts.Errors.REPEAT_TAG.format('author'))

                if len(_head.getElementsByTagName('version')) > 1:
                    raise Exceptions.ScriptError(Consts.Errors.REPEAT_TAG.format('verison'))

                __author = _head.getElementsByTagName('author')[0]
                __version = _head.getElementsByTagName('version')[0]

                if len(__author.childNodes) != 1:
                    raise Exceptions.ScriptError(Consts.Errors.REPEAT_VALUE.format('author', len(__author.childNodes)))

                if len(__version.childNodes) != 1:
                    raise Exceptions.ScriptError(Consts.Errors.REPEAT_VALUE.format('version', len(__version.childNodes)))

                self.author = __author.childNodes[0].data
                self.version = __version.childNodes[0].data

            else:
                pass
        else:
            raise Exceptions.ScriptError(Consts.Errors.NO_HEAD_NODE.format(self.script))

        # Parse body
        if len(_collection.getElementsByTagName('body')) == 0:
            raise Exceptions.ScriptError(Consts.Errors.NO_BODY_NODE.format(self.script))

        _body = _collection.getElementsByTagName('body')[0]
        if not len(_body.getElementsByTagName('scene')):
            raise Exceptions.ScriptError(Consts.Errors.NO_BODY_NODE.format(self.script + ' [No scene index found]'))

        for s in _body.getElementsByTagName('scene'):
            if s.childNodes[0].data.strip() == '':
                raise Exceptions.ScriptError(Consts.Errors.NULL_VALUE.format('body.scene'))

            self.scenes.append(s.childNodes[0].data)

    def setScript(self, scriptPath: os.PathLike[str]):
        self.script = scriptPath

    def _addScene(self, scenePath: os.PathLike[str]) -> SceneParameters:
        pass

    def parse(self) -> list[SceneParameters]:
        self._parseScript()

# The configuration of a scene
class SceneParameters(object):
    def __init__(self, stype: int = Consts.SceneTypes.DEFAULT):
        self.idNum = 1
        self.text = 'Hello Pygal!'
        self.name = ''
        self.bgm = ''
        self.sprite = None
        self.background = ''
        self.choices = {'A': 1, 'B': 0, 'C': 1, 'D': 0}
        self.stype = Consts.SceneTypes.DEFAULT

    # Configure the scene parameters
    def set(self, **kwargs):
        try:
            self.idNum = kwargs['idNum']
        except KeyError:
            pass

        try:
            self.text = kwargs['text']
        except KeyError:
            pass

        try:
            self.name = kwargs['name']
        except KeyError:
            pass

        try:
            self.bgm = kwargs['bgm']
        except KeyError:
            pass

        try:
            self.sprite = kwargs['sprite']
        except KeyError:
            pass

        try:
            self.background = kwargs['background']
        except KeyError:
            pass

        try:
            self.choices = kwargs['choices']
        except KeyError:
            pass

class Scene(object):
    def __init__(self, param: SceneParameters):
        self.bgmPlaying = None
        if param.stype == Consts.SceneTypes.DEFAULT:
            self.text = param.text
            self.name = param.name
            self.bgm = param.bgm
            self.sprite = param.sprite
            self.background = param.background
            self.choices = param.choices
            self.jumpTo = None
            self.choicesLoad = False
            self.spriteLoad = False
            self.spriteFadeIn = False

            self.stype = Consts.SceneTypes.DEFAULT

            # Init sound module
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.musicPlaying = False
            if self.bgm:
                pygame.mixer.music.load(self.bgm)

    def _jump(self, dest: int):
        self.jumpTo = dest

    def render(self, screen: pygame.Surface, screenSize: tuple, textElements: TextField, bgmMode: int = 0,
               event: pygame.event.Event = None, res: dict = None):
        # print('Render process start.')
        if not self.choices:
            textElements.configureStyle(alpha = 140)

        if self.stype == Consts.SceneTypes.DEFAULT:
            # Render background
            background = pygame.transform.scale(pygame.image.load(self.background), screenSize)
            screen.blit(background, (0, 0))

            # Render TextField
            textElements.setText(self.text)
            textElements.setName(self.name)
            textElements.render(screenSize)

            # Play music put to Renderer
            # Conditions: there's music defined in script and other music is not loaded

            if bgmMode == -1:
                pygame.mixer.init()
            elif bgmMode == 0:
                pass
            elif bgmMode == 1:
                if self.bgm:
                    if not self.bgmPlaying:
                        self.bgmPlaying = True
                        try:
                            pygame.mixer.music.load(self.bgm)
                            pygame.time.delay(10)
                            pygame.mixer.music.play()
                        except Exception as e:
                            raise Exceptions.GameError(e)

        # Render the sprite
        if self.sprite:
            if not self.spriteLoad:
                self.spriteLoad = True
                if self.spriteFadeIn:
                    self._fadeEffect(screen,
                                    pygame.transform.scale(pygame.image.load(self.sprite), [screenSize[0] / Consts.Nums.SPRITE_WIDTH_RATIO, screenSize[1]]),
                                     [screenSize[0] - screenSize[0] / Consts.Nums.SPRITE_WIDTH_RATIO, 50],
                                    )

            else:
                spriteObj = pygame.transform.scale(pygame.image.load(self.sprite),
                                                    [screenSize[0] / Consts.Nums.SPRITE_WIDTH_RATIO,
                                                    screenSize[1]])
                screen.blit(spriteObj, [screenSize[0] - screenSize[0] / Consts.Nums.SPRITE_WIDTH_RATIO, 50])

        if self.choices:
            textElements.configureStyle(alpha = 0)

            self._renderInteractive(screen, screenSize, event, res = res)
        # print('Render process end.')

    # A method implements UI fade effect
    def _fadeEffect(self, parent: pygame.Surface, obj: ControlElements | pygame.Surface, position: tuple, speed: int | float = 50, reversed: bool = False, start: int = 0, stop: int = 255, step: float | int = 1):
        if reversed:
            i = start
            while i >= stop:
                obj.set_alpha(i)
                parent.blit(obj, position)
                pygame.display.flip()
                pygame.time.delay(speed)
                i -= step

        else:
            i = start
            while i <= stop:
                obj.set_alpha(i)
                parent.blit(obj, position)
                pygame.display.flip()
                pygame.time.delay(speed)
                i += step

    def _renderInteractive(self, screen: pygame.Surface, screenSize: tuple, event: pygame.event.Event, *, res: dict = None):
        # Render the choice Button
        if self.choices:
            self.choicesBtn = []
            if len(self.choices) > 4:
                raise Exceptions.GameError(Consts.Errors.CHOICES_TOO_MANY)

            # TODO: Fix the fontsize bug: fontsize won't change while button's size change

            # Define the basic configuration of choice button object
            if len(self.choices) == 1:
                # Get the text of Button
                _text = list(self.choices.keys())[0]
                # Get the jump info of the Button
                _scene = list(self.choices.values())[0]

                # Get the size of Button
                if len(_text) < 8:
                    _size = [screenSize[0] / 6, screenSize[1] / 8]
                else:
                    if len(_text) > 25:
                        raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(_text)))
                    _size = [screenSize[0] / 6 + len(_text) * 20, screenSize[1] / 8]

                # try:
                #     raise FutureWarning('May not support single choose button in the future.')
                # except FutureWarning:
                #     sys.stderr.write(traceback.format_exc() + '\n')

                self.choicesBtn.append(
                    Button(
                        screen,
                        # Center alignment
                        pos = [screenSize[0] / 2, screenSize[1] / 2],
                        size = _size,
                        text = _text,
                        click = lambda: self._jump(_scene),
                        image = Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage = Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

            elif len(self.choices) == 2:
                _text1 = list(self.choices.keys())[0]
                _scene1 = list(self.choices.values())[0]
                _text2 = list(self.choices.keys())[1]
                _scene2 = list(self.choices.values())[1]

                # Get the size of Button
                _text = _text1 if _text1 > _text2 else _text2
                if len(_text) < 8:
                    _size = [screenSize[0] / 6, screenSize[1] / 8]
                else:
                    if len(_text) > 25:
                        raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(_text)))
                    _size = [screenSize[0] / 6 + len(_text) * 20, screenSize[1] / 8]

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos = [screenSize[0] / 2, screenSize[1] / 2 - _size[1]],
                        size = _size,
                        text = _text1,
                        click = lambda: self._jump(_scene1),
                        image = Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage = Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos = [screenSize[0] / 2, screenSize[1] / 2 + _size[1]],
                        size = _size,
                        text = _text2,
                        click = lambda: self._jump(_scene2),
                        image = Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage = Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

            elif len(self.choices) == 3:
                _text1 = list(self.choices.keys())[0]
                _scene1 = list(self.choices.values())[0]
                _text2 = list(self.choices.keys())[1]
                _scene2 = list(self.choices.values())[1]
                _text3 = list(self.choices.keys())[2]
                _scene3 = list(self.choices.values())[2]

                _text = max(_text1, _text2, _text3)
                if len(_text) < 8:
                    _size = [screenSize[0] / 6, screenSize[1] / 8]
                else:
                    if len(_text) > 25:
                        raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(_text)))
                    _size = [screenSize[0] / 6 + len(_text) * 20, screenSize[1] / 8]

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos = [screenSize[0] / 2, screenSize[1] / 2 - 1.5 * _size[1]],
                        size = _size,
                        text = _text1,
                        click = lambda: self._jump(_scene1),
                        image = Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage = Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos = [screenSize[0] / 2, screenSize[1] / 2],
                        size = _size,
                        text = _text2,
                        click = lambda: self._jump(_scene2),
                        image = Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage = Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos=[screenSize[0] / 2, screenSize[1] / 2 + 1.5 * _size[1]],
                        size=_size,
                        text=_text3,
                        click=lambda: self._jump(_scene3),
                        image=Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage=Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

            elif len(self.choices) == 4:
                _text1 = list(self.choices.keys())[0]
                _scene1 = list(self.choices.values())[0]
                _text2 = list(self.choices.keys())[1]
                _scene2 = list(self.choices.values())[1]
                _text3 = list(self.choices.keys())[2]
                _scene3 = list(self.choices.values())[2]
                _text4 = list(self.choices.keys())[3]
                _scene4 = list(self.choices.values())[3]

                # Get the size of Button
                _text = max(_text1, _text2, _text3, _text4)
                if len(_text) < 8:
                    _size = [screenSize[0] / 6, screenSize[1] / 8]
                else:
                    if len(_text) > 25:
                        raise Exceptions.GameError(Consts.Errors.CONTENT_TOO_LONG.format(len(_text)))
                    _size = [screenSize[0] / 6 + len(_text) * 20, screenSize[1] / 8]

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos=[screenSize[0] / 2, screenSize[1] / 2 - 3 * _size[1]],
                        size=_size,
                        text=_text1,
                        click=lambda: self._jump(_scene1),
                        image=Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage=Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos=[screenSize[0] / 2, screenSize[1] / 2 - 1 * _size[1]],
                        size=_size,
                        text=_text2,
                        click=lambda: self._jump(_scene2),
                        image=Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage=Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )
                self.choicesBtn.append(
                    Button(
                        screen,
                        pos=[screenSize[0] / 2, screenSize[1] / 2 + 1 * _size[1]],
                        size=_size,
                        text=_text3,
                        click=lambda: self._jump(_scene3),
                        image=Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage=Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

                self.choicesBtn.append(
                    Button(
                        screen,
                        pos=[screenSize[0] / 2, screenSize[1] / 2 + 3 * _size[1]],
                        size=_size,
                        text=_text4,
                        click=lambda: self._jump(_scene4),
                        image=Utils.fromNameToPath('Button/Button_1.png', 'image') if not res else res['Button']['normal'],
                        hoverImage=Utils.fromNameToPath('Button/Button_2.png', 'image') if not res else res['Button']['hover']
                    )
                )

            for btn in self.choicesBtn:
                btn.render(event)

# A class help render the scene
class Renderer(object):
    def __init__(self, scenes: list[Scene], logger: _Logger = None):
        self.s = scenes
        self.id = 0
        self.sceneCount = len(self.s)
        self.s[0].bgmPlaying = False

        if logger:
            for index, content in enumerate(self.s):
                logger.logger.debug(
                    f'[Pygal.renderer] [Scenes] {index + 1}. {content.name}: {content.text} (bgm:{content.bgm}, img:{content.background}, sprite:{content.sprite}).')

    # Render the pointed scene
    def renderAll(self, **args):
        # print(self.s[self.id].bgm, self.s[self.id - 1].bgm)
        if self.id < self.sceneCount:
            if self.id == 0:
                self.s[self.id].render(args['screen'], args['screenSize'], args['textUI'],
                                       bgmMode=Consts.BgmMode.CHANGE, event=args['event'])

            if self.s[self.id].bgm and self.s[self.id].bgm != self.s[self.id - 1].bgm and self.id != 0:
                self.s[self.id].render(args['screen'], args['screenSize'], args['textUI'],
                                       bgmMode=Consts.BgmMode.CHANGE, event=args['event'])

            elif not self.s[self.id].bgm:
                self.s[self.id].bgmPlaying = False
                self.s[self.id].render(args['screen'], args['screenSize'], args['textUI'], bgmMode=Consts.BgmMode.STOP,
                                       event=args['event'])

            elif self.s[self.id].bgm == self.s[self.id - 1].bgm:
                self.s[self.id].bgmPlaying = True
                self.s[self.id].render(args['screen'], args['screenSize'], args['textUI'], bgmMode=Consts.BgmMode.KEEP,
                                       event=args['event'])

        self._onjump()

    def _onjump(self):
        # Detect the jump event:
        if self.s[self.id].jumpTo is not None and self.s[self.id].jumpTo != self.id:
            self.jump(self.s[self.id].jumpTo)

    # Will called if not force dynamicRender
    # This will only enable interaction in scenes
    def renderInteraction(self, **kw):
        if self.s[self.id].choices:
            # The try statement is for this method called before the button in scene constructed
            try:
                for btn in self.s[self.id].choicesBtn:
                    # Call sub render for every interactive object
                    btn.render(kw['event'])
            except AttributeError:
                pass

            self._onjump()
        else:
            return

    def hasNext(self) -> bool:
        return self.id + 1 < self.sceneCount

    def next(self):
        if self.id >= self.sceneCount:
            return

        self.id += 1
        self.s[self.id].bgmPlaying = False

    def getCurrentScene(self) -> Scene:
        try:
            return self.s[self.id]
        except IndexError:
            return self.s[self.id - 1]

    # Implements the jumping function
    def jump(self, index: int):
        if index > self.sceneCount:
            raise IndexError(Consts.Errors.NO_SCENE_FORWARD.format(index))

        self.id = index - 1
        # Stop the music played in last scene
        self.s[self.id].musicPlaying = False
        pygame.mixer.init()


# The main class to launch the engine
class Pygal(object):
    def __init__(self, scriptPath: str):
        # This property sets the mode of engine
        # When it's true, the render() will be called once per frame
        # It will be more lag, while you're resizing the window or exit the game, it will delay
        # When it is false
        # The render() will only be called when window resized or Mouse Event triggered

        self.dynamicRenderMode = False
        # Configure logger settings
        self.logger = _Logger()
        self.logger.logger.info('Hello Pygal Engine!')

        # Create a renderer to help show the scene
        self.sceneList = []

        # Script parser
        self.parser = Parser()
        self.logger.logger.info('Scene parser loaded!')

        self.sceneParser = SceneParser()
        self.parser.setScript(scriptPath)
        self.parser.parse()

        for s in self.parser.scenes:
            self.sceneList.append(Scene(self.sceneParser.parse(s.split('=')[1].rstrip(']'))))

        self.renderer = Renderer(self.sceneList, logger=self.logger)
        self.logger.logger.info('Renderer ready!')
        self.logger.logger.debug(f'Total scenes: {self.renderer.sceneCount}')

        # Create a runtime-variabel dictionary
        self.vars = {}

        # Resources
        try:
            print(self.parser.startupParam)
            _res = self.parser.startupParam['resource']
            if _res != 'null':
                self.resourceDict = ResourcesConfiguration(self.parser.startupParam['resource'])
        except KeyError:
            self.resourceDict = None

        except Exception as e:
            self.logger.logger.error(e)

        try:
            self.setup(
                size = (int(self.parser.startupParam['size'].split(',')[0]), int(self.parser.startupParam['size'].split(',')[1])),
                title = self.parser.startupParam['title'],
                icon = self.parser.startupParam['icon'],
                resizeable = self.parser.startupParam['resizable'],
                dynamicRender = True if self.parser.startupParam['dynamicRender'] == 'true' else False
            )
        except Exception as e:
            self.logger.error(e)

    def setup(self, size: tuple = None, title: str = None, icon: str = None, resizeable: bool = True, dynamicRender: bool = False):
        try:
            self.dynamicRenderMode = dynamicRender
            if self.dynamicRenderMode:
                try:
                    raise RuntimeWarning('Force dynamic rendering will caused fps decrease!')
                except RuntimeWarning:
                    sys.stderr.write(traceback.format_exc())

            pygame.init()
            # The window size
            self.wsize = size
            self.logger.logger.info('Pygame Engine loaded!')

            # Configure Window
            self.window = pygame.display.set_mode(self.wsize, pygame.RESIZABLE if resizeable else 0)
            self.logger.logger.info(f'Window successfully init! (size={size}, resize={resizeable})')
            if title:
                pygame.display.set_caption(title)
                self.logger.logger.info(f'Window title redirecting to {title}.')
            else:
                pygame.display.set_caption('Pygal')

            if icon:
                pygame.display.set_icon(pygame.image.load(icon))
                self.logger.logger.info(f'Successfully load icon: {icon} => {pygame.image.load(icon)}.')
        except Exception as e:
            self.logger.error(e)

        # Scene control elements
        self.textField = TextField(self.window, ui=self.resourceDict.res['Textfield'])
        self.logger.logger.info(f'Text control init! {self.textField}.')

        # Clock to control fps
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            # if self.dynamicRenderMode:
            #     self.clock.tick(Consts.Nums.LOWEST_FPS)

            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.logger.logger.info('Engine exits!')
                        sys.exit()

                    # If the window resize, update the window size so that renderer can redraw controls
                    if event.type == pygame.WINDOWRESIZED:
                        self.wsize = self.window.get_size()
                        if not self.dynamicRenderMode:
                            self.renderer.renderAll(screen=self.window, screenSize=self.window.get_size(),
                                                    textUI=self.textField, event=event)
                        self.logger.logger.info(f'Window resized to {self.wsize}.')

                    # Only triggered in scene with no choice button
                    # Use to go forward
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.renderer.getCurrentScene().choices:
                        # Ignore
                        if self.renderer.hasNext():
                            self.renderer.next()
                            if not self.dynamicRenderMode:
                                self.renderer.renderAll(screen=self.window, screenSize=self.window.get_size(),
                                                        textUI=self.textField, event=event)
                            self.logger.logger.info(f'Scene forward to "scene-{self.renderer.id + 1}!"')

                    # An special render channel
                    if self.renderer.getCurrentScene().choices and not self.dynamicRenderMode:
                        self.renderer.renderInteraction(event=event)
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.logger.logger.info('Button pushed!')
                            self.renderer.renderAll(screen=self.window, screenSize=self.window.get_size(),
                                                        textUI=self.textField, event=event)

                    # Write your last render code after
                    if self.dynamicRenderMode:
                        self.renderer.renderAll(screen=self.window, screenSize=self.window.get_size(),
                                            textUI=self.textField, event=event)
                    # pygame.display.flip()
                    pygame.display.update()
            except Exception as e:
                self.logger.error(e)

class PygalTk(tk.Tk, object):
    pass
