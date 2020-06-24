# BassieRacing - Utils

# Import modules
from constants import *
import math

# Format time in seconds to a nice string
def formatTime(time):
    return '%01d:%02d.%03d' % (time // 60, math.floor(time % 60), (time - math.floor(time)) * 1000)

# Check if other version is newer
def checkVersion(version):
    otherVersionParts = [ int(part) for part in version.split('.') ]
    gameVersionParts = [ int(part) for part in Config.VERSION.split('.') ]
    return otherVersionParts[0] > gameVersionParts[0] or otherVersionParts[1] > gameVersionParts[1] or otherVersionParts[2] > gameVersionParts[2]
