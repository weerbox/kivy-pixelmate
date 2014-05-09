import sys
import os

from kivy.core.window import Window
import pygame
from kivy.utils import platform
from kivy.app import App

APP = App.get_running_app
APP_VERSION = 0.71
KEY_ESCAPE = pygame.K_ESCAPE

USE_KIVY_SETTINGS = 0

DEFAULT_IMAGE_SIZE = (128, 64)

# button column layout size
PALLETECOL_BTNCOUNT = 10

TOOLBAR_LAYOUT_POS_HINT = (0, 0.05)
TOOLBAR_LAYOUT_SIZE_HINT = (0.14, 0.9)
TOOLBAR_LAYOUT_CLMN_SIZE_HINT = (0.5, 1)

BTN_SHOW_TOOLBAR_SIZE_HINT = (0.03, 0.05)

#PAINT_LAYOUT_SIZE = ()
PALLETE_LAYOUT_CLMN_SIZE_HINT = (0.045, 1)
PALLETE_LAYOUT_SIZE_HINT = (0.11, 1.0 - 1.0 / PALLETECOL_BTNCOUNT)

MENU_ENTRY_HEIGHT_HINT = 0.12

WIN_WIDTH = Window.width
WIN_HEIGHT = Window.height
BTN_WIDTH = Window.width * 0.6
BTN_HEIGHT = Window.height * 0.6

LAYER_RIBBON_WIDTH_HINT = 0.20
LAYER_RIBBON_BUTTON_HEIGHT_HINT = 1.0 / 11
LAYERBOX_PADDING = [3, 3, 3, 3]

DRAWAREA_SIZE = (Window.width, Window.height)

if platform() == 'android':
    DEF_PATH = os.path.splitdrive(sys.argv[0])[0] + '/'
else:
    DEF_PATH = os.path.splitdrive(sys.argv[0])[0] + '/'

TOOL_PENCIL = 0
TOOL_ERASE = 1
TOOL_PICKER = 2
TOOL_FILL = 3
TOOL_SELECT = 4
TOOL_MOVE = 5
TOOL_RECT = 6
TOOL_LINE = 7
TOOL_ELLIPSE = 8
TOOL_POLYGON = 9
TOOL_POLYLINE = 10