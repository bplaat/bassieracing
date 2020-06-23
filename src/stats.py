# BassieRacing - Stats

# Import modules
import math

# The vehicles data
vehicles = [
    # Speedy Car (Car 1)
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
            },
            # Green
            {
                'x': 0,
                'y': 363
            },
            # Yellow
            {
                'x': 142,
                'y': 0
            },
            # Black
            {
                'x': 142,
                'y': 131
            }
        ],
        'width': 71,
        'height': 131,
        'forwardAcceleration': 200,
        'maxForwardVelocity': 700,
        'backwardAcceleration': -60,
        'maxBackwardVelocity': -200,
        'turningSpeed': math.radians(90)
    },

    # CyberTruck (Car 4)
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
            },
            # Green
            {
                'x': 422,
                'y': 131
            },
            # Yellow
            {
                'x': 142,
                'y': 383
            },
            # Black
            {
                'x': 213,
                'y': 0
            }
        ],
        'width': 70,
        'height': 131,
        'forwardAcceleration': 150,
        'maxForwardVelocity': 800,
        'backwardAcceleration': -100,
        'maxBackwardVelocity': -300,
        'turningSpeed': math.radians(75)
    },

    # Fire Car (Car 3)
    {
        'name': 'Fire Car',
        'colors': [
            # Blue
            {
                'x': 282,
                'y': 252
            },
            # Red
            {
                'x': 353,
                'y': 0
            },
            # Green
            {
                'x': 422,
                'y': 262
            },
            # Yellow
            {
                'x': 212,
                'y': 262
            },
            # Black
            {
                'x': 212,
                'y': 393
            }
        ],
        'width': 70,
        'height': 131,
        'forwardAcceleration': 150,
        'maxForwardVelocity': 600,
        'backwardAcceleration': -50,
        'maxBackwardVelocity': -200,
        'turningSpeed': math.radians(145)
    },

    # Torchcycle (Motorcycle)
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
            },
            # Green
            {
                'x': 423,
                'y': 0
            },
            # Yellow
            {
                'x': 353,
                'y': 131
            },
            # Black
            {
                'x': 71,
                'y': 479
            }
        ],
        'width': 44,
        'height': 100,
        'forwardAcceleration': 300,
        'maxForwardVelocity': 650,
        'backwardAcceleration': -75,
        'maxBackwardVelocity': -200,
        'turningSpeed': math.radians(180)
    },

    # MemeRacer (Car 2)
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
            },
            # Green
            {
                'x': 71,
                'y': 0
            },
            # Yellow
            {
                'x': 71,
                'y': 116
            },
            # Black
            {
                'x': 0,
                'y': 0
            }
        ],
        'width': 71,
        'height': 116,
        'forwardAcceleration': 150,
        'maxForwardVelocity': 400,
        'backwardAcceleration': -250,
        'maxBackwardVelocity': -1000,
        'turningSpeed': math.radians(90)
    },

    # Deluxe 3000 (Car 5)
    {
        'name': 'Deluxe 3000',
        'colors': [
            # Blue
            {
                'x': 283,
                'y': 0
            },
            # Red
            {
                'x': 352,
                'y': 242
            },
            # Green
            {
                'x': 283,
                'y': 121
            },
            # Yellow
            {
                'x': 142,
                'y': 262
            },
            # Black
            {
                'x': 213,
                'y': 131
            }
        ],
        'width': 70,
        'height': 121,
        'forwardAcceleration': 175,
        'maxForwardVelocity': 650,
        'backwardAcceleration': -100,
        'maxBackwardVelocity': -150,
        'turningSpeed': math.radians(120)
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
    { 'x': 512, 'y': 1280 },  #  1 = Asphalt Open

    { 'x': 640, 'y': 1280 },  #  2 = Asphalt Top Closed
    { 'x': 384, 'y': 1280 },  #  3 = Asphalt Bottom Closed
    { 'x': 512, 'y': 1408 },  #  4 = Asphalt Left Closed
    { 'x': 512, 'y': 1152 },  #  5 = Asphalt Right Closed

    { 'x': 640, 'y': 1024 },  #  6 = Asphalt Corner Top Left
    { 'x': 640, 'y': 896 },   #  7 = Asphalt Corner Top Right
    { 'x': 512, 'y': 1024 },  #  8 = Asphalt Corner Bottom Left
    { 'x': 512, 'y': 896 },   #  9 = Asphalt Corner Bottom Right

    { 'x': 640, 'y': 1536 },  # 10 = Asphalt Vertical Closed
    { 'x': 640, 'y': 1664 },  # 11 = Asphalt Horizontal Closed

    # Finish tiles
    { 'x': 0, 'y': 2048 },    # 12 = Finish Vertical Open
    { 'x': 128, 'y': 2048 },  # 13 = Finish Horizontal Open

    { 'x': 0, 'y': 2176 },    # 14 = Finish Top Closed
    { 'x': 0, 'y': 1920 },    # 15 = Finish Bottom Closed
    { 'x': 128, 'y': 2176 },  # 16 = Finish Left Closed
    { 'x': 128, 'y': 1920 },  # 17 = Finish Right Closed

    { 'x': 384, 'y': 896 },   # 18 = Finish Vertical Closed
    { 'x': 384, 'y': 1024 },  # 19 = Finish Horizontal Closed

    # Checkpoint tiles
    { 'x': 128, 'y': 256 },   # 20 = Checkpoint Vertical Open
    { 'x': 128, 'y': 384 },   # 21 = Checkpoint Horizontal Open

    { 'x': 2176, 'y': 768 },  # 22 = Checkpoint Top Closed
    { 'x': 2176, 'y': 896 },  # 23 = Checkpoint Bottom Closed
    { 'x': 2176, 'y': 1024 }, # 24 = Checkpoint Left Closed
    { 'x': 2176, 'y': 1152 }, # 25 = Checkpoint Right Closed

    { 'x': 128, 'y': 768 },   # 26 = Checkpoint Vertical Closed
    { 'x': 128, 'y': 896 }    # 27 = Checkpoint Horizontal Closed
]
