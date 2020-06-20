# BassieRacing - Stats

# Import modules
import math

# The vehicles data
vehicles = [
    # Speedy Car
    {
        'name': 'Speedy Car',
        'colors': [
            # Blue
            {
                'x': 0,
                'y': 116
            },
            # Red
            {
                'x': 71,
                'y': 232
            }
        ],
        'width': 70,
        'height': 131,
        'forwardAcceleration': 1,
        'maxForwardVelocity': 700,
        'backwardAcceleration': -0.5,
        'maxBackwardVelocity': -200,
        'turningSpeed': math.radians(90)
    },

    # CyberTruck
    {
        'name': 'CyberTruck',
        'colors': [
            # Blue
            {
                'x': 282,
                'y': 383
            },
            # Red
            {
                'x': 352,
                'y': 363
            }
        ],
        'width': 70,
        'height': 131,
        'forwardAcceleration': 0.5,
        'maxForwardVelocity': 800,
        'backwardAcceleration': -0.25,
        'maxBackwardVelocity': -300,
        'turningSpeed': math.radians(65)
    },

    # Torchcycle
    {
        'name': 'Torchcycle',
        'colors': [
            # Blue
            {
                'x': 466,
                'y': 393
            },
            # Red
            {
                'x': 422,
                'y': 393
            }
        ],
        'width': 44,
        'height': 100,
        'forwardAcceleration': 1.5,
        'maxForwardVelocity': 650,
        'backwardAcceleration': -1,
        'maxBackwardVelocity': -200,
        'turningSpeed': math.radians(180)
    },

    # MemeRacer
    {
        'name': 'MemeRacer',
        'colors': [
            # Blue
            {
                'x': 0,
                'y': 247
            },
            # Red
            {
                'x': 71,
                'y': 363
            }
        ],
        'width': 71,
        'height': 116,
        'forwardAcceleration': 2,
        'maxForwardVelocity': 400,
        'backwardAcceleration': -0.75,
        'maxBackwardVelocity': -1000,
        'turningSpeed': math.radians(80)
    }
]

# The terrain tiles data
terrainTiles = [
    # Grass tiles
    { 'x': 1408, 'y': 1664 }, # 0 = Grass

    { 'x': 1408, 'y': 1408 }, #  1 = Grass Dirt Top
    { 'x': 1408, 'y': 1920 }, #  2 = Grass Dirt Bottom
    { 'x': 1536, 'y': 384 },  #  3 = Grass Dirt Left
    { 'x': 1536, 'y': 128 },  #  4 = Grass Dirt Right

    { 'x': 1408, 'y': 2176 }, #  5 = Grass 3/4 Dirt Corner Top Left
    { 'x': 1536, 'y': 0 },    #  6 = Grass 3/4 Dirt Corner Top Right
    { 'x': 1536, 'y': 512 },  #  7 = Grass 3/4 Dirt Corner Bottom Left
    { 'x': 1536, 'y': 640 },  #  8 = Grass 3/4 Dirt Corner Bottom Right

    { 'x': 1408, 'y': 1536 }, #  9 = Grass 1/4 Dirt Corner Top Left
    { 'x': 1408, 'y': 1280 }, # 10 = Grass 1/4 Dirt Corner Top Right
    { 'x': 1408, 'y': 2048 }, # 11 = Grass 1/4 Dirt Corner Bottom Left
    { 'x': 1408, 'y': 1792 }, # 12 = Grass 1/4 Dirt Corner Bottom Right

    # Dirt tiles
    { 'x': 0, 'y': 256 },     # 13 = Dirt

    { 'x': 0, 'y': 0 },       # 14 = Dirt Sand Top
    { 'x': 0, 'y': 512 },     # 15 = Dirt Sand Bottom
    { 'x': 0, 'y': 1280 },    # 16 = Dirt Sand Left
    { 'x': 0, 'y': 1024 },    # 17 = Dirt Sand Right

    { 'x': 0, 'y': 768 },     # 18 = Dirt 3/4 Sand Corner Top Left
    { 'x': 0, 'y': 896 },     # 19 = Dirt 3/4 Sand Corner Top Right
    { 'x': 0, 'y': 1408 },    # 20 = Dirt 3/4 Sand Corner Bottom Left
    { 'x': 0, 'y': 1536 },    # 21 = Dirt 3/4 Sand Corner Bottom Right

    { 'x': 0, 'y': 128 },     # 22 = Dirt 1/4 Sand Corner Top Left
    { 'x': 0, 'y': 1664 },    # 23 = Dirt 1/4 Sand Corner Top Right
    { 'x': 0, 'y': 640 },     # 24 = Dirt 1/4 Sand Corner Bottom Left
    { 'x': 0, 'y': 384 },     # 25 = Dirt 1/4 Sand Corner Bottom Right

    # Sand tiles
    { 'x': 1280, 'y': 2048 }  # 26 = Sand
]

# The track tiles data
trackTiles = [
    None,

    # Asphalt tiles
    { 'x': 512, 'y': 1280 }, #  1 = Asphalt Open

    { 'x': 640, 'y': 1280 }, #  2 = Asphalt Top Closed
    { 'x': 384, 'y': 1280 }, #  3 = Asphalt Bottom Closed
    { 'x': 512, 'y': 1408 }, #  4 = Asphalt Left Closed
    { 'x': 512, 'y': 1152 }, #  5 = Asphalt Right Closed

    { 'x': 640, 'y': 1024 }, #  6 = Asphalt Corner Top Left
    { 'x': 640, 'y': 896 },  #  7 = Asphalt Corner Top Right
    { 'x': 512, 'y': 1024 }, #  8 = Asphalt Corner Bottom Left
    { 'x': 512, 'y': 896 },  #  9 = Asphalt Corner Bottom Right

    { 'x': 640, 'y': 1536 }, # 10 = Asphalt Vertical Closed
    { 'x': 640, 'y': 1664 }, # 11 = Asphalt Horizontal Closed

    # Finish tiles
    { 'x': 0, 'y': 2048 },   # 12 = Finish Vertical Open
    { 'x': 128, 'y': 2048 }, # 13 = Finish Horizontal Open

    { 'x': 0, 'y': 2176 },   # 14 = Finish Top Closed
    { 'x': 0, 'y': 1920 },   # 15 = Finish Bottom Closed
    { 'x': 128, 'y': 2176 }, # 16 = Finish Left Closed
    { 'x': 128, 'y': 1920 }, # 17 = Finish Right Closed

    { 'x': 384, 'y': 1024 }, # 18 = Finish Vertical Closed
    { 'x': 384, 'y': 896 }   # 19 = Finish Horizontal Closed
]
