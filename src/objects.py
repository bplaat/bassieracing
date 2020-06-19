# BassieRacing - Objects

# Import modules
from constants import *
import json
import math
from noise import *
import pygame
import random
from stats import *
import tkinter.messagebox

# The camera class
class Camera:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        self.speed = 400
        self.movingUp = False
        self.movingDown = False
        self.movingLeft = False
        self.movingRight = False

    def update(self, delta):
        if self.movingUp:
            self.y -= self.speed * delta
        if self.movingDown:
            self.y += self.speed * delta
        if self.movingLeft:
            self.x -= self.speed * delta
        if self.movingRight:
            self.x += self.speed * delta

# The vehicle class
class Vehicle:
    NOT_MOVING = 0
    MOVING_FORWARD = 1
    MOVING_BACKWARD = 2

    NOT_TURNING = 0
    TURNING_LEFT = 1
    TURNING_RIGHT = 2

    def __init__(self, vehiclesImage, id, vehicleType, color, x, y, angle):
        self.id = id
        self.vehicleType = vehicleType
        self.color = color

        self.vehicleImage = pygame.Surface(( vehicleType['width'], vehicleType['height'] ), pygame.SRCALPHA)
        self.vehicleImage.blit(vehiclesImage, ( 0, 0 ),  (
            vehicleType['colors'][color]['x'],
            vehicleType['colors'][color]['y'],
            vehicleType['width'],
            vehicleType['height']
        ))

        self.x = x
        self.y = y
        self.angle = angle

        self.velocity = 0
        self.acceleration = 0

        self.moving = Vehicle.NOT_MOVING
        self.turning = Vehicle.NOT_TURNING

    def update(self, delta):
        # Handle turning
        if self.turning == Vehicle.TURNING_LEFT:
            self.angle += self.vehicleType['turningSpeed'] * delta
        if self.turning == Vehicle.TURNING_RIGHT:
            self.angle -= self.vehicleType['turningSpeed'] * delta

        # Handle moving
        if self.moving == Vehicle.MOVING_FORWARD:
            self.acceleration += self.vehicleType['forwardAcceleration']
        elif self.moving == Vehicle.MOVING_BACKWARD:
            self.acceleration += self.vehicleType['backwardAcceleration']
        else:
            # Slow down when not moving
            self.acceleration = 0
            if self.velocity > 0:
                self.velocity -= self.velocity / 20
            if self.velocity < 0:
                self.velocity += -self.velocity / 20

        # Cap velocity by vehicle stats
        self.velocity += self.acceleration
        if self.velocity > self.vehicleType['maxForwardVelocity']:
                self.velocity = self.vehicleType['maxForwardVelocity']
        if self.velocity < self.vehicleType['maxBackwardVelocity']:
            self.velocity = self.vehicleType['maxBackwardVelocity']

        # Calculate new position
        self.x -= self.velocity * math.sin(self.angle) * delta
        self.y -= self.velocity * math.cos(self.angle) * delta

    def draw(self, surface, camera):
        # Rotate vehicle and draw
        rotatedVehicleImage = pygame.transform.rotate(self.vehicleImage, math.degrees(self.angle))
        x = math.floor(self.x - rotatedVehicleImage.get_width() / 2 - (camera.x - surface.get_width() // 2))
        y = math.floor(self.y - rotatedVehicleImage.get_height() / 2 - (camera.y - surface.get_height() // 2))
        if (
            x + rotatedVehicleImage.get_width() >= 0 and y + rotatedVehicleImage.get_height() >= 0 and
            x - rotatedVehicleImage.get_width() < surface.get_width() and y - rotatedVehicleImage.get_height() < surface.get_height()
        ):
            surface.blit(rotatedVehicleImage, ( x, y ))

# The map class
class Map:
    def __init__(self, tilesImage, name, width, height):
        self.tileSize = Config.TILE_SPRITE_SIZE
        self.originalTilesImage = tilesImage
        self.tilesImage = tilesImage

        self.name = name
        self.width = width
        self.height = height

        # Generate terrain
        self.noise = Noise()
        self.noiseX = random.randint(-1000000, 1000000)
        self.noiseY = random.randint(-1000000, 1000000)

        self.startX = width // 2
        self.startY = height // 2
        self.startAngle = math.radians(270)

        self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
        for y in range(height):
            for x in range(width):
                n = self.noise.noise((x + self.noiseX) / 20, (y + self.noiseY) / 20, 2)
                if n > 0.2:
                    self.terrain[y][x] = 2
                elif n > 0.075:
                    self.terrain[y][x] = 1
                else:
                    self.terrain[y][x] = 0

        self.track = [ [ 0 for x in range(width) ] for y in range(height) ]
        self.track[self.startY][self.startX] = 2
        self.track[self.startY + 1][self.startX] = 2

    # Create map by loading a JSON string
    @staticmethod
    def load_from_string(tilesImage, jsonString):
        data = json.loads(jsonString)

        if  'type' not in data or data['type'] != 'BassieRacing Map':
            tkinter.messagebox.showinfo('Not a BassieRacing map!', 'This JSON file is not a BassieRacing Map')
            return None

        if data['version'] != Config.VERSION:
            tkinter.messagebox.showinfo('Map uses different game version!', 'This map uses a different game version, some incompatibility may occur\n\nFile version: ' + data['version'] + '\nGame version: ' + Config.VERSION)

        map = Map(tilesImage, data['name'], data['width'], data['height'])

        map.noiseX = data['noise']['x']
        map.noiseY = data['noise']['y']

        map.startX = data['start']['x']
        map.startY = data['start']['y']
        map.startAngle = math.radians(data['start']['angle'])

        map.terrain = data['terrain']
        map.track = data['track']

        return map

    # Create map by loading a file
    @staticmethod
    def load_from_file(tilesImage, file_path):
        with open(file_path, 'r') as file:
            return Map.load_from_string(tilesImage, file.read())

    # Save map to file
    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            data = {
                'type': 'BassieRacing Map',
                'version': Config.VERSION,

                'name': self.name,
                'width': self.width,
                'height': self.height,

                'noise': {
                    'x': self.noiseX,
                    'y': self.noiseY
                },

                'start': {
                    'x': self.startX,
                    'y': self.startY,
                    'angle': math.degrees(self.startAngle)
                },

                'terrain': self.terrain,
                'track': self.track
            }
            json.dump(data, file, separators=(',', ':'))

    # Resize map
    def resize(self, width, height):
        dw = (width - self.width) / 2
        dh = (height - self.height) / 2

        # TODO

        terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
        for y in range(height):
            for x in range(width):
                n = self.noise.noise((x + self.noiseX) / 20, (y + self.noiseY) / 20, 2)
                if n > 0.2:
                    terrain[y][x] = 2
                elif n > 0.075:
                    terrain[y][x] = 1
                else:
                    terrain[y][x] = 0

        track = [ [ 0 for x in range(width) ] for y in range(height) ]

        self.startX = width // 2
        self.startY = height // 2
        self.startAngle = math.radians(270)

        track[self.startY][self.startX] = 2
        track[self.startY + 1][self.startX] = 2

        self.width = width
        self.height = height
        self.terrain = terrain
        self.track = track

    # Set tile size
    def set_tile_size(self, tileSize):
        self.tileSize = tileSize
        self.tilesImage = pygame.transform.scale(self.originalTilesImage, (
            math.floor(self.originalTilesImage.get_width() * (tileSize / Config.TILE_SPRITE_SIZE)),
            math.floor(self.originalTilesImage.get_height() * (tileSize / Config.TILE_SPRITE_SIZE))
        ))

    # Draw the map
    def draw(self, surface, camera):
        # Draw terrain tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                tileType = terrainTiles[self.terrain[y][x]]
                tx = math.floor(x * self.tileSize - (camera.x - surface.get_width() / 2))
                ty = math.floor(y *  self.tileSize - (camera.y - surface.get_height() / 2))
                if tx + self.tileSize >= 0 and ty + self.tileSize >= 0 and tx < surface.get_width() and ty < surface.get_height():
                    surface.blit(
                        self.tilesImage,
                        ( tx, ty, self.tileSize, self.tileSize ),
                        (
                            math.floor(tileType['x'] * (self.tileSize / Config.TILE_SPRITE_SIZE)),
                            math.floor(tileType['y'] * (self.tileSize / Config.TILE_SPRITE_SIZE)),
                            self.tileSize,
                            self.tileSize
                        )
                    )

        # Draw track tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                trackId = self.track[y][x]
                if trackId != 0:
                    tileType = trackTiles[trackId - 1]
                    tx = math.floor(x * self.tileSize - (camera.x - surface.get_width() / 2))
                    ty = math.floor(y *  self.tileSize - (camera.y - surface.get_height() / 2))
                    if (
                        tx + self.tileSize >= 0 and ty + self.tileSize >= 0 and
                        tx < surface.get_width() and ty < surface.get_height()
                    ):
                        surface.blit(
                            self.tilesImage,
                            ( tx, ty, self.tileSize, self.tileSize ),
                            (
                                math.floor(tileType['x'] * (self.tileSize / Config.TILE_SPRITE_SIZE)),
                                math.floor(tileType['y'] * (self.tileSize / Config.TILE_SPRITE_SIZE)),
                                self.tileSize,
                                self.tileSize
                            )
                        )
