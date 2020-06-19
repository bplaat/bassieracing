# BassieRacing - Stats

# Import modules
import math

# The vehicles data
vehicles = [
    {
        'id': 0,
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

    {
        'id': 1,
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

    {
        'id': 2,
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

    {
        'id': 2,
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
    {
        'id': 0,
        'name': 'Grass',
        'x': 1408,
        'y': 1664
    },

    {
        'id': 1,
        'name': 'Dirt',
        'x': 0,
        'y': 256
    },

    {
        'id': 2,
        'name': 'Sand',
        'x': 1280,
        'y': 2048
    }
]

# The track tiles data
trackTiles = [
    None,

    {
        'id': 1,
        'name': 'Asphalt',
        'x': 512,
        'y': 1280
    },

    {
        'id': 1,
        'name': 'Finish',
        'x': 0,
        'y': 2048
    }
]
