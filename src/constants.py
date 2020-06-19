# BassieRacing - Constants

# The config constants class
class Config:
    # App constants
    NAME = 'BassieRacing'
    VERSION = '0.4.0'

    # Window constants
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    # Game constants
    TILE_SPRITE_SIZE = 128
    PIXELS_PER_METER = 18

    # Editor constants
    EDITOR_CAMERA_BORDER = 12
    EDITOR_TILE_SIZE = 32
    MAP_SIZES = [ 24, 32, 48, 56 ]
    MAP_SIZE_LABELS = [ 'Small', 'Medium', 'Large', 'Giant' ]

# The colors constants class
class Color:
    BLACK = ( 0, 0, 0 )
    DARK = ( 25, 25, 25 )
    LIGHT_GRAY = ( 225, 225, 225 )
    WHITE = ( 255, 255, 255 )

# The text align constants class
class TextAlign:
    LEFT = 0
    CENTER = 1
    RIGHT = 2
