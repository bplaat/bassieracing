# BassieRacing - Utils

# Import modules
import math

# Format time in seconds to a nice string
def formatTime(time):
    return '%01d:%02d.%03d' % (time // 60, math.floor(time % 60), (time - math.floor(time)) * 1000)
