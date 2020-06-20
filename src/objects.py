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
    def __init__(self, x, y, tilesImage, tileSize, vehiclesImage, vehicleScale = None):
        self.x = x
        self.y = y

        if tileSize == Config.TILE_SPRITE_SIZE:
            self.tilesImage = tilesImage
        else:
            self.tilesImage = pygame.transform.scale(tilesImage, (
                math.floor(tilesImage.get_width() * (tileSize / Config.TILE_SPRITE_SIZE)),
                math.floor(tilesImage.get_height() * (tileSize / Config.TILE_SPRITE_SIZE))
            ))
        self.tileSize = tileSize

        if vehicleScale == None:
            self.vehicleScale = tileSize / Config.TILE_SPRITE_SIZE
        else:
            self.vehicleScale = vehicleScale

        if tileSize == Config.TILE_SPRITE_SIZE:
            self.vehiclesImage = vehiclesImage
        else:
            self.vehiclesImage = pygame.transform.scale(vehiclesImage, (
                math.floor(vehiclesImage.get_width() * self.vehicleScale),
                math.floor(vehiclesImage.get_height() * self.vehicleScale)
            ))
        self.vehicleImageCache = [ None for i in range(2) ]

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

    # Create vehicle
    def __init__(self, id, vehicleType, color, x, y, angle):
        self.id = id
        self.vehicleType = vehicleType
        self.color = color

        self.x = x
        self.y = y
        self.angle = angle

        self.velocity = 0
        self.acceleration = 0

        self.moving = Vehicle.NOT_MOVING
        self.turning = Vehicle.NOT_TURNING

    # Update vehicle
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

    # Crop the right vehicle image and save in camera vehicle image cache
    def crop(self, camera):
        camera.vehicleImageCache[self.id] = pygame.Surface(
            ( self.vehicleType['width'], self.vehicleType['height'] ),
            pygame.SRCALPHA
        )
        camera.vehicleImageCache[self.id].blit(camera.vehiclesImage, ( 0, 0 ),  (
            math.floor(self.vehicleType['colors'][self.color]['x'] * camera.vehicleScale),
            math.floor(self.vehicleType['colors'][self.color]['y'] * camera.vehicleScale),
            math.floor(self.vehicleType['width'] * camera.vehicleScale),
            math.floor(self.vehicleType['height'] * camera.vehicleScale)
        ))

    # Draw vehicle
    def draw(self, surface, camera):
        # Rotate vehicle image and draw
        rotatedVehicleImage = pygame.transform.rotate(camera.vehicleImageCache[self.id], math.degrees(self.angle))
        x = math.floor(self.x - rotatedVehicleImage.get_width() / 2 - (camera.x - surface.get_width() / 2))
        y = math.floor(self.y - rotatedVehicleImage.get_height() / 2 - (camera.y - surface.get_height() / 2))
        if (
            x + rotatedVehicleImage.get_width() >= 0 and y + rotatedVehicleImage.get_height() >= 0 and
            x - rotatedVehicleImage.get_width() < surface.get_width() and y - rotatedVehicleImage.get_height() < surface.get_height()
        ):
            surface.blit(rotatedVehicleImage, ( x, y ))

# The map class
class Map:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

        # Generate terrain
        self.noise = PerlinNoise()
        self.noiseX = random.randint(-1000000, 1000000)
        self.noiseY = random.randint(-1000000, 1000000)

        self.startX = width // 2
        self.startY = height // 2
        self.startAngle = math.radians(270)

        self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
        for y in range(height):
            for x in range(width):
                self.terrain[y][x] = self.generate_terrain_tile(x, y)
        self.blendTerrain()

        self.track = [ [ 0 for x in range(width) ] for y in range(height) ]
        self.blendTrack()

    # Create map by loading a JSON string
    @staticmethod
    def load_from_string(jsonString):
        try:
            data = json.loads(jsonString)
        except:
            tkinter.messagebox.showinfo('Corrupt JSON file!', 'This JSON file is corrupt\nYou can try to fix it with JSONLint (https://jsonlint.com/)')
            return

        if  'type' not in data or data['type'] != 'BassieRacing Map':
            tkinter.messagebox.showinfo('Not a BassieRacing map!', 'This JSON file is not a BassieRacing Map')
            return

        if data['version'] != Config.VERSION:
            tkinter.messagebox.showinfo('Map uses different game version!', 'This map uses a different game version, some incompatibility may occur\n\nFile version: ' + data['version'] + '\nGame version: ' + Config.VERSION)

        map = Map(data['name'], data['width'], data['height'])

        map.noiseX = data['noise']['x']
        map.noiseY = data['noise']['y']

        map.startX = data['start']['x']
        map.startY = data['start']['y']
        map.startAngle = math.radians(data['start']['angle'])

        map.terrain = data['terrain']
        map.blendTerrain()
        map.track = data['track']
        map.blendTrack()

        return map

    # Create map by loading a file
    @staticmethod
    def load_from_file(file_path):
        with open(file_path, 'r') as file:
            return Map.load_from_string(file.read())

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
            file.write(json.dumps(data, separators=(',', ':')) + '\n')

    # Generate terrain tile
    def generate_terrain_tile(self, x, y):
        n = self.noise.noise((x + (self.noiseX - self.width // 2)) / 20, (y + (self.noiseY - self.height // 2)) / 20, 2)
        if n > 0.2:
            return 2
        if n > 0.075:
            return 1
        return 0

    # Blend terrain
    def blendTerrain(self):
        self.blendedTerrain = [ [ 0 for x in range(self.width) ] for y in range(self.height) ]
        for y in range(self.height):
            for x in range(self.width):
                # Grass terrain tile
                if self.terrain[y][x] == 0:
                    # Dirt 1/4 corner
                    if (x != 0 and self.terrain[y][x - 1] == 1) and (y != 0 and self.terrain[y - 1][x] == 1):
                        self.blendedTerrain[y][x] = 9
                    elif (x != self.width - 1 and self.terrain[y][x + 1] == 1) and (y != 0 and self.terrain[y - 1][x] == 1):
                        self.blendedTerrain[y][x] = 10
                    elif (x != 0 and self.terrain[y][x - 1] == 1) and (y != self.height - 1 and self.terrain[y + 1][x] == 1):
                        self.blendedTerrain[y][x] = 11
                    elif (x != self.width - 1 and self.terrain[y][x + 1] == 1) and (y != self.height - 1 and self.terrain[y + 1][x] == 1):
                        self.blendedTerrain[y][x] = 12

                    # Dirt border
                    elif y != 0 and self.terrain[y - 1][x] == 1:
                        self.blendedTerrain[y][x] = 1
                    elif y != self.height - 1 and self.terrain[y + 1][x] == 1:
                        self.blendedTerrain[y][x] = 2
                    elif x != 0 and self.terrain[y][x - 1] == 1:
                        self.blendedTerrain[y][x] = 3
                    elif x != self.width - 1 and self.terrain[y][x + 1] == 1:
                        self.blendedTerrain[y][x] = 4

                    # Dirt 3/4 corner
                    elif x != 0 and y != 0 and self.terrain[y - 1][x - 1] == 1:
                        self.blendedTerrain[y][x] = 5
                    elif x != self.width - 1 and y != 0 and self.terrain[y - 1][x + 1] == 1:
                        self.blendedTerrain[y][x] = 6
                    elif x != 0 and y != self.height - 1 and self.terrain[y + 1][x - 1] == 1:
                        self.blendedTerrain[y][x] = 7
                    elif x != self.width - 1 and y != self.height - 1 and self.terrain[y + 1][x + 1] == 1:
                        self.blendedTerrain[y][x] = 8

                    else:
                        self.blendedTerrain[y][x] = 0

                # Dirt terrain tile
                if self.terrain[y][x] == 1:
                    # Sand 1/4 corner
                    if (x != 0 and self.terrain[y][x - 1] == 2) and (y != 0 and self.terrain[y - 1][x] == 2):
                        self.blendedTerrain[y][x] = 22
                    elif (x != self.width - 1 and self.terrain[y][x + 1] == 2) and (y != 0 and self.terrain[y - 1][x] == 2):
                        self.blendedTerrain[y][x] = 23
                    elif (x != 0 and self.terrain[y][x - 1] == 2) and (y != self.height - 1 and self.terrain[y + 1][x] == 2):
                        self.blendedTerrain[y][x] = 24
                    elif (x != self.width - 1 and self.terrain[y][x + 1] == 2) and (y != self.height - 1 and self.terrain[y + 1][x] == 2):
                        self.blendedTerrain[y][x] = 25

                    # Sand border
                    elif y != 0 and self.terrain[y - 1][x] == 2:
                        self.blendedTerrain[y][x] = 14
                    elif y != self.height - 1 and self.terrain[y + 1][x] == 2:
                        self.blendedTerrain[y][x] = 15
                    elif x != 0 and self.terrain[y][x - 1] == 2:
                        self.blendedTerrain[y][x] = 16
                    elif x != self.width - 1 and self.terrain[y][x + 1] == 2:
                        self.blendedTerrain[y][x] = 17

                    # Sand 3/4 corner
                    elif x != 0 and y != 0 and self.terrain[y - 1][x - 1] == 2:
                        self.blendedTerrain[y][x] = 18
                    elif x != self.width - 1 and y != 0 and self.terrain[y - 1][x + 1] == 2:
                        self.blendedTerrain[y][x] = 19
                    elif x != 0 and y != self.height - 1 and self.terrain[y + 1][x - 1] == 2:
                        self.blendedTerrain[y][x] = 20
                    elif x != self.width - 1 and y != self.height - 1 and self.terrain[y + 1][x + 1] == 2:
                        self.blendedTerrain[y][x] = 21

                    else:
                        self.blendedTerrain[y][x] = 13

                # Sand terrain tile
                if self.terrain[y][x] == 2:
                    self.blendedTerrain[y][x] = 26

    # Blend track
    def blendTrack(self):
        self.blendedTrack = [ [ 0 for x in range(self.width) ] for y in range(self.height) ]
        for y in range(self.height):
            for x in range(self.width):
                # Asphalt track tile
                if self.track[y][x] == 1:
                    # Closed
                    if (y == 0 or self.track[y - 1][x] == 0) and (y == self.height - 1 or self.track[y + 1][x] == 0):
                        self.blendedTrack[y][x] = 10
                    elif (x == 0 or self.track[y][x - 1] == 0) and (x == self.width - 1 or self.track[y][x + 1] == 0):
                        self.blendedTrack[y][x] = 11

                    # Corners
                    elif (y == 0 or self.track[y - 1][x] == 0) and (x == 0 or self.track[y][x - 1] == 0):
                        self.blendedTrack[y][x] = 6
                    elif (y == 0 or self.track[y - 1][x] == 0) and (x == self.width - 1 or self.track[y][x + 1] == 0):
                        self.blendedTrack[y][x] = 7
                    elif (y == self.height - 1 or self.track[y + 1][x] == 0) and (x == 0 or self.track[y][x - 1] == 0):
                        self.blendedTrack[y][x] = 8
                    elif (y == self.height - 1 or self.track[y + 1][x] == 0) and (x == self.width - 1 or self.track[y][x + 1] == 0):
                        self.blendedTrack[y][x] = 9

                    # Straight border
                    elif y == 0 or self.track[y - 1][x] == 0:
                        self.blendedTrack[y][x] = 2
                    elif y == self.height - 1 or self.track[y + 1][x] == 0:
                        self.blendedTrack[y][x] = 3
                    elif x == 0 or self.track[y][x - 1] == 0:
                        self.blendedTrack[y][x] = 4
                    elif x == self.width - 1 or self.track[y][x + 1] == 0:
                        self.blendedTrack[y][x] = 5

                    else:
                        self.blendedTrack[y][x] = 1

                # Finish track tile
                if self.track[y][x] == 2:
                    # Open
                    if (y != 0 and self.track[y - 1][x] == 2) and (y != self.height - 1 and self.track[y + 1][x] == 2):
                        self.blendedTrack[y][x] = 12
                    elif (x != 0 and self.track[y][x - 1] == 2) and (x != self.width - 1 and self.track[y][x + 1] == 2):
                        self.blendedTrack[y][x] = 13

                    # Straight border
                    elif (y == 0 or self.track[y - 1][x] == 0) and (y != self.height - 1 and self.track[y + 1][x] == 2):
                        self.blendedTrack[y][x] = 14
                    elif (y == self.height - 1 or self.track[y + 1][x] == 0) and (y != 0 and self.track[y - 1][x] == 2):
                        self.blendedTrack[y][x] = 15
                    elif (x == 0 or self.track[y][x - 1] == 0) and (x != self.width - 1 and self.track[y][x + 1] == 2):
                        self.blendedTrack[y][x] = 16
                    elif (x == self.width - 1 or self.track[y][x + 1] == 0) and (x != 0 and self.track[y][x - 1] == 2):
                        self.blendedTrack[y][x] = 17

                    # Closed
                    elif (y == 0 or self.track[y - 1][x] == 0) and (y == self.height - 1 or self.track[y + 1][x] == 0):
                        self.blendedTrack[y][x] = 18
                    elif (x == 0 or self.track[y][x - 1] == 0) and (x == self.width - 1 or self.track[y][x + 1] == 0):
                        self.blendedTrack[y][x] = 19

                    else:
                        self.blendedTrack[y][x] = 13
    # Resize map
    def resize(self, width, height):
        old_width = self.width
        old_height = self.height
        old_terrain = self.terrain
        old_track = self.track

        self.width = width
        self.height = height
        dw = (width - old_width) // 2
        dh = (height - old_height) // 2

        # Extend map
        if dw > 0:
            self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
            for y in range(height):
                for x in range(width):
                    if x - dw >= 0 and y - dh >= 0 and x - dw < old_width and y - dh < old_height:
                        self.terrain[y][x] = old_terrain[y - dh][x - dw]
                    else:
                        self.terrain[y][x] = self.generate_terrain_tile(x, y)
            self.blendTerrain()

            self.track = [ [ 0 for x in range(width) ] for y in range(height) ]
            for y in range(height):
                for x in range(width):
                    if x - dw >= 0 and y - dh >= 0 and x - dw < old_width and y - dh < old_height:
                        self.track[y][x] = old_track[y - dh][x - dw]
            self.blendTrack()

            self.startX += dw
            self.startY += dh

        # Crop map
        else:
            dw = abs(dw)
            dh = abs(dh)

            self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
            for y in range(height):
                for x in range(width):
                    self.terrain[y][x] = old_terrain[dh + y][dw + x]
            self.blendTerrain()

            self.track = [ [ 0 for x in range(width) ] for y in range(height) ]
            for y in range(height):
                for x in range(width):
                    self.track[y][x] = old_track[dh + y][dw + x]
            self.blendTrack()

            self.startX -= dw
            self.startY -= dh

    # Draw the map
    def draw(self, surface, camera):
        # Draw terrain tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                tileType = terrainTiles[self.blendedTerrain[y][x]]
                tx = math.floor(x * camera.tileSize - (camera.x - surface.get_width() / 2))
                ty = math.floor(y *  camera.tileSize - (camera.y - surface.get_height() / 2))
                if tx + camera.tileSize >= 0 and ty + camera.tileSize >= 0 and tx < surface.get_width() and ty < surface.get_height():
                    surface.blit(
                        camera.tilesImage,
                        ( tx, ty, camera.tileSize, camera.tileSize ),
                        (
                            math.floor(tileType['x'] * (camera.tileSize / Config.TILE_SPRITE_SIZE)),
                            math.floor(tileType['y'] * (camera.tileSize / Config.TILE_SPRITE_SIZE)),
                            camera.tileSize,
                            camera.tileSize
                        )
                    )

        # Draw track tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                trackId = self.blendedTrack[y][x]
                if trackId != 0:
                    tileType = trackTiles[trackId]
                    tx = math.floor(x * camera.tileSize - (camera.x - surface.get_width() / 2))
                    ty = math.floor(y *  camera.tileSize - (camera.y - surface.get_height() / 2))
                    if (
                        tx + camera.tileSize >= 0 and ty + camera.tileSize >= 0 and
                        tx < surface.get_width() and ty < surface.get_height()
                    ):
                        surface.blit(
                            camera.tilesImage,
                            ( tx, ty, camera.tileSize, camera.tileSize ),
                            (
                                math.floor(tileType['x'] * (camera.tileSize / Config.TILE_SPRITE_SIZE)),
                                math.floor(tileType['y'] * (camera.tileSize / Config.TILE_SPRITE_SIZE)),
                                camera.tileSize,
                                camera.tileSize
                            )
                        )
