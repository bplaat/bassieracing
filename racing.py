# Bassie Racing - A topdown 2D two player racing game
# Made by Bastiaan van der Plaat (https://bastiaan.ml/)
# GitHub repo: https://github.com/bplaat/bassieracing
# Made with PyGame (but only used to plot images and text to the screen and to handle the window events)
# It also uses tkinter for the file open and save dialogs and error messages
# And a noise library for random terrain generation

import json
import noise
import math
import pygame
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import random
import webbrowser

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

# The colors constants class
class Color:
    BLACK = ( 0, 0, 0 )
    DARK = ( 25, 25, 25 )
    LIGHT_GRAY = ( 225, 225, 225 )
    WHITE = ( 255, 255, 255 )

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
        self.tileSize = Game.TILE_SPRITE_SIZE
        self.originalTilesImage = tilesImage
        self.tilesImage = tilesImage

        self.name = name
        self.width = width
        self.height = height

        # Generate terrain
        self.noiseX = random.randint(-1000000, 1000000)
        self.noiseY = random.randint(-1000000, 1000000)

        self.startX = width // 2
        self.startY = height // 2
        self.startAngle = math.radians(270)

        self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
        for y in range(height):
            for x in range(width):
                n = noise.pnoise2((x + self.noiseX) / 20, (y + self.noiseY) / 20, 2)
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

        if  'type' not in data or data['type'] != 'Bassie Racing Map':
            tkinter.messagebox.showinfo('Not a Bassie Racing map!', 'This JSON file is not a Bassie Racing Map')
            return None

        if data['version'] != Game.VERSION:
            tkinter.messagebox.showinfo('Map uses different game version!', 'This map uses a different game version, some incompatibility may occur')

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
    def load_from_file(tilesImage, path):
        with open(path, 'r') as file:
            return Map.load_from_string(tilesImage, file.read())

    # Save map to file
    def save_to_file(self, path):
        with open(path, 'w') as file:
            data = {
                'type': 'Bassie Racing Map',
                'version': Game.VERSION,

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
                n = noise.pnoise2((x + self.noiseX) / 20, (y + self.noiseY) / 20, 2)
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
            math.floor(self.originalTilesImage.get_width() * (tileSize / Game.TILE_SPRITE_SIZE)),
            math.floor(self.originalTilesImage.get_height() * (tileSize / Game.TILE_SPRITE_SIZE))
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
                            math.floor(tileType['x'] * (self.tileSize / Game.TILE_SPRITE_SIZE)),
                            math.floor(tileType['y'] * (self.tileSize / Game.TILE_SPRITE_SIZE)),
                            self.tileSize,
                            self.tileSize
                        )
                    )

        # Draw track tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                trackId = self.track[y][x]
                if trackId != 0:
                    tileType = trackTiles[trackId]
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
                                math.floor(tileType['x'] * (self.tileSize / Game.TILE_SPRITE_SIZE)),
                                math.floor(tileType['y'] * (self.tileSize / Game.TILE_SPRITE_SIZE)),
                                self.tileSize,
                                self.tileSize
                            )
                        )

# The label widget class
class Label:
    # Create label
    def __init__(self, text, x, y, width, height, font, color, clickCallback = None, callbackExtra = None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.textSurface = font.render(text, True, color)
        self.clickCallback = clickCallback
        self.callbackExtra = callbackExtra

    # Update label text
    def set_text(self, text):
        self.text = text
        self.textSurface = self.font.render(self.text, True, self.color)

    # Handle label events
    def handle_event(self, event):
        # Handle mouse events
        if (
            self.clickCallback != None and
            event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP) and
            event.pos[0] >= self.x and event.pos[1] >= self.y and
            event.pos[0] < self.x + self.width and event.pos[1] < self.y + self.height
        ):
            if event.type == pygame.MOUSEBUTTONUP:
                if self.callbackExtra != None:
                    self.clickCallback(self.callbackExtra)
                else:
                    self.clickCallback()
            return True

        return False

    # Draw label
    def draw(self, surface):
        surface.blit(self.textSurface, (
            self.x + (self.width - self.textSurface.get_width()) // 2,
            self.y + (self.height - self.textSurface.get_height()) // 2
        ))

# The button widget class
class Button(Label):
    # Create button
    def __init__(self, text, x, y, width, height, font, color, backgroundColor, clickCallback = None, callbackExtra = None):
        Label.__init__(self, text, x, y, width, height, font, color, clickCallback, callbackExtra)
        self.backgroundColor = backgroundColor

    # Draw button
    def draw(self, surface):
        pygame.draw.rect(surface, self.backgroundColor, ( self.x, self.y, self.width, self.height ))
        Label.draw(self, surface)

# The combobox widget class
class ComboBox(Button):
    # Create combobox
    def __init__(self, options, selectedItem, x, y, width, height, font, color, backgroundColor, activeBackgroundColor, changedCallback = None, callbackExtra = None):
        self.options = options
        self.selectedItem = selectedItem
        Button.__init__(self, options[self.selectedItem] + ' \u25BC', x, y, width, height, font, color, backgroundColor, self.root_button_clicked)
        self.blurBackgroundColor = backgroundColor
        self.activeBackgroundColor = activeBackgroundColor
        self.changedCallback = changedCallback
        self.callbackExtra = callbackExtra
        self.active = False

        # Create combobox widgets
        ry = y + height
        if len(options) * height > Game.HEIGHT - (y + height):
            ry = y - len(options) * height

        self.widgets = []
        for i in range(len(options)):
            self.widgets.append(Button(options[i], x, ry, width, height, font, color, backgroundColor, self.option_button_clicked, i))
            ry += height

    # Set selected item
    def set_selected(self, selectedItem):
        self.selectedItem = selectedItem
        self.set_text(self.options[self.selectedItem] + ' \u25BC')

    # Root button clicked
    def root_button_clicked(self):
        # Toggle active
        self.active = not self.active
        if self.active:
            self.backgroundColor = self.activeBackgroundColor
        else:
            self.backgroundColor = self.blurBackgroundColor

    # Option button clicked
    def option_button_clicked(self, optionIndex):
        # Update root button
        self.active = False
        self.backgroundColor = self.blurBackgroundColor
        self.set_selected(optionIndex)

        # Call callback
        if self.changedCallback != None:
            if self.callbackExtra != None:
                self.changedCallback(self.selectedItem, self.callbackExtra)
            else:
                self.changedCallback(self.selectedItem)

    # Handle combobox events
    def handle_event(self, event):
        # If active handle widget events
        if self.active:
            for widget in reversed(self.widgets):
                if widget.handle_event(event):
                    return True

        # Handle root button events
        return Button.handle_event(self, event)

    # Draw combobox
    def draw(self, surface):
        # Draw root button
        Button.draw(self, surface)

        # If active draw widgets
        if self.active:
            for widget in self.widgets:
                widget.draw(surface)

# The vehicle viewport widget class
class VehicleViewport:
    def __init__(self, game, vehicle, x, y, width, height, map, vehicles):
        self.game = game
        self.vehicle = vehicle
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.map = map
        self.vehicles = vehicles
        self.surface = pygame.Surface(( width, height ))

        # Create vehicle viewport widgets
        self.widgets = []
        self.speedLabel = Label('Speed: %3d km/h' % (vehicle.velocity / Game.PIXELS_PER_METER * 3.6), 0, height - 24 - 24, width, 24, game.textFont, Color.BLACK)
        self.widgets.append(self.speedLabel)

    def handle_event(self, event):
        # Handle keydown events
        if event.type == pygame.KEYDOWN:
            # Handle left player movement
            if self.vehicle.id == 0:
                if event.key == pygame.K_w:
                    self.vehicle.moving = Vehicle.MOVING_FORWARD
                if event.key == pygame.K_s:
                    self.vehicle.moving = Vehicle.MOVING_BACKWARD
                if event.key == pygame.K_a:
                    self.vehicle.turning = Vehicle.TURNING_LEFT
                if event.key == pygame.K_d:
                    self.vehicle.turning = Vehicle.TURNING_RIGHT

            # Handle right player movement
            if self.vehicle.id == 1:
                if event.key == pygame.K_UP:
                    self.vehicle.moving = Vehicle.MOVING_FORWARD
                if event.key == pygame.K_DOWN:
                    self.vehicle.moving = Vehicle.MOVING_BACKWARD
                if event.key == pygame.K_LEFT:
                    self.vehicle.turning = Vehicle.TURNING_LEFT
                if event.key == pygame.K_RIGHT:
                    self.vehicle.turning = Vehicle.TURNING_RIGHT

         # Handle keyup events
        if event.type == pygame.KEYUP:
            # Handle left player movement
            if self.vehicle.id == 0:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.vehicle.moving = Vehicle.NOT_MOVING
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    self.vehicle.turning = Vehicle.NOT_TURNING

            # Handle right player movement
            if self.vehicle.id == 1:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.vehicle.moving = Vehicle.NOT_MOVING
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.vehicle.turning = Vehicle.NOT_TURNING

        return False

    def draw(self, surface):
        # Clear the surface
        self.surface.fill(Color.DARK)

        # Create camera
        camera = Camera(self.vehicle.x, self.vehicle.y)

        # Draw the map to surface
        self.map.draw(self.surface, camera)

        # Draw all the vehicles to surface
        for vehicle in self.vehicles:
            vehicle.draw(self.surface, camera)

        # Update speed label
        self.speedLabel.set_text('Speed: %d km/h' % (self.vehicle.velocity / Game.PIXELS_PER_METER * 3.6))

        # Draw widgets
        for widget in self.widgets:
            widget.draw(self.surface)

        # Draw own surface to the screen
        surface.blit(self.surface, ( self.x, self.y ))

# The vehicle selector widget class
class VehicleSelector:
    def __init__(self, game, x, y, width, height, color):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        # Create vehicle selector widget widgets
        self.widgets = []
        ry = 196
        self.nameLabel = Label('', x, y + ry, self.width, 48, game.textFont, Color.WHITE)
        self.widgets.append(self.nameLabel)
        ry += 48 + 16
        self.maxForwardSpeed = Label('', x, y + ry, self.width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxForwardSpeed)
        ry += 32 + 16
        self.maxBackwardSpeed = Label('', x, y + ry, self.width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxBackwardSpeed)
        ry += 32 + 16
        self.turningSpeed = Label('', x, y + ry, self.width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.turningSpeed)

        self.widgets.append(Button('<', x, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button('>', x + width - 48, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

        self.selectedVehicleIndex = random.randint(0, len(vehicles) - 1)
        self.update_vehicle()

    # Update selected vehicle
    def update_vehicle(self):
        self.selectedVehicle = vehicles[self.selectedVehicleIndex]
        self.vehicleImage = pygame.Surface(( self.selectedVehicle['width'], self.selectedVehicle['height'] ), pygame.SRCALPHA)
        self.vehicleImage.blit(game.vehiclesImage, ( 0, 0 ),  (
            self.selectedVehicle['colors'][self.color]['x'],
            self.selectedVehicle['colors'][self.color]['y'],
            self.selectedVehicle['width'],
            self.selectedVehicle['height']
        ))

        self.nameLabel.set_text(self.selectedVehicle['name'])
        self.maxForwardSpeed.set_text('Max Forward Speed: %d km/h' % (self.selectedVehicle['maxForwardVelocity'] / Game.PIXELS_PER_METER * 3.6))
        self.maxBackwardSpeed.set_text('Max Backward Speed: %d km/h' % (self.selectedVehicle['maxBackwardVelocity'] / Game.PIXELS_PER_METER * 3.6))
        self.turningSpeed.set_text('Turing Speed: %d \u00B0/s' % math.degrees(self.selectedVehicle['turningSpeed']))

    # Handle rotate left button click
    def rotate_left_button_clicked(self):
        if self.selectedVehicleIndex == 0:
            self.selectedVehicleIndex = len(vehicles) - 1
        else:
            self.selectedVehicleIndex -= 1
        self.selectedVehicle = vehicles[self.selectedVehicleIndex]
        self.update_vehicle()

    # Handle rotate right button click
    def rotate_right_button_clicked(self):
        if self.selectedVehicleIndex == len(vehicles) - 1:
            self.selectedVehicleIndex = 0
        else:
            self.selectedVehicleIndex += 1
        self.selectedVehicle = vehicles[self.selectedVehicleIndex]
        self.update_vehicle()

    # Handle page events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw page
    def draw(self, surface):
        # Draw vehicle image
        surface.blit(self.vehicleImage, (
            self.x + ((self.width - self.selectedVehicle['width']) // 2),
            self.y + (((self.height - 256) - self.selectedVehicle['height']) // 2)
        ))

        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

# The map editor widget class
class MapEditor:
    GRASS_BRUSH = 0
    DIRT_BRUSH = 1
    SAND_BRUSH = 2
    ASPHALT_BRUSH = 3
    FINISH_BRUSH = 4
    TRACK_ERASER = 5
    TOOL_LABELS =  [ 'Grass Brush', 'Dirt Brush', 'Sand Brush', 'Asphalt Brush', 'Finish Brush', 'Track Eraser' ]

    # Create map editor
    def __init__(self, game, map, x, y, width, height, tool):
        self.game = game
        self.set_map(map)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.camera = Camera()
        self.center_camera()

        self.tool = tool
        self.mouseDown = False

    # Set map
    def set_map(self, map):
        self.map = map
        map.set_tile_size(Game.EDITOR_TILE_SIZE)

    # Center camera
    def center_camera(self):
        self.camera.x = self.map.startX * Game.EDITOR_TILE_SIZE + Game.EDITOR_TILE_SIZE / 2
        self.camera.y = self.map.startY * Game.EDITOR_TILE_SIZE + Game.EDITOR_TILE_SIZE / 2

    # Use tool
    def use_tool(self, mouseX, mouseY):
        tileX = math.floor((mouseX + self.camera.x - Game.WIDTH / 2) / Game.EDITOR_TILE_SIZE)
        tileY = math.floor((mouseY + self.camera.y - Game.HEIGHT / 2) / Game.EDITOR_TILE_SIZE)

        if tileX >= 0 and tileY >= 0 and tileX < self.map.width and tileY < self.map.height:
            if self.tool == MapEditor.GRASS_BRUSH:
                self.map.terrain[tileY][tileX] = 0

            if self.tool == MapEditor.DIRT_BRUSH:
                self.map.terrain[tileY][tileX] = 1

            if self.tool == MapEditor.SAND_BRUSH:
                self.map.terrain[tileY][tileX] = 2

            if self.tool == MapEditor.ASPHALT_BRUSH:
                self.map.track[tileY][tileX] = 1

            if self.tool == MapEditor.FINISH_BRUSH:
                self.map.track[tileY][tileX] = 2

            if self.tool == MapEditor.TRACK_ERASER:
                self.map.track[tileY][tileX] = 0

    # Handle page events
    def handle_event(self, event):
        # Handle mousedown events
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouseDown = True
            self.use_tool(event.pos[0], event.pos[1])
            return True

        # Handle mousemove events
        if event.type == pygame.MOUSEMOTION:
            mouseX = event.pos[0]
            mouseY = event.pos[1]

            if self.mouseDown:
                self.use_tool(mouseX, mouseY)
            else:
                self.camera.movingUp = mouseY >= 2 and mouseY < Game.EDITOR_CAMERA_BORDER
                self.camera.movingDown = mouseY >= Game.HEIGHT - Game.EDITOR_CAMERA_BORDER and mouseY < Game.HEIGHT - 2
                self.camera.movingLeft = mouseX >= 2 and mouseX < Game.EDITOR_CAMERA_BORDER
                self.camera.movingRight = mouseX >= Game.WIDTH - Game.EDITOR_CAMERA_BORDER and mouseX < Game.WIDTH - 2

            return True

        # Handle mouseup events
        if event.type == pygame.MOUSEBUTTONUP:
            self.mouseDown = False
            return True

        # Handle keydown events
        if event.type == pygame.KEYDOWN:
            # Handle camera movement
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.camera.movingUp = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.camera.movingDown = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.camera.movingLeft = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.camera.movingRight = True

        # Handle keyup events
        if event.type == pygame.KEYUP:
            # Handle camera movement
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.camera.movingUp = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.camera.movingDown = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.camera.movingLeft = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.camera.movingRight = False

        return False

    # Update map editor
    def update(self, delta):
        # Update camera
        self.camera.update(delta)

    # Draw map editor
    def draw(self, surface):
        # Draw background
        surface.fill(Color.DARK)

        # Draw the map
        self.map.draw(surface, self.camera)

# The page class
class Page:
    # Create empty page
    def __init__(self, game):
        self.game = game

        # Pick random background
        self.backgroundColor = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))

        # Create empty widgets list
        self.widgets = []

    # Handle page events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Update page
    def update(self, delta):
        pass

    # Draw page
    def draw(self, surface):
        # Draw background
        surface.fill(self.backgroundColor)

        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

# The menu page class
class MenuPage(Page):
    # Create menu page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create menu page widgets
        y = 128
        self.widgets.append(Label('Bassie Racing', 0, y, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Button('Play', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.play_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Map Editor', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.edit_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Help', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.help_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Exit', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.exit_button_clicked))
        self.widgets.append(Label('v' + Game.VERSION, Game.WIDTH - 16 - 96, 16, 96, 32, game.textFont, Color.WHITE, self.version_label_clicked))
        self.widgets.append(Label('Made by Bastiaan van der Plaat', 0, Game.HEIGHT - 64 - 16, Game.WIDTH, 64, game.textFont, Color.WHITE, self.footer_label_clicked))

    # Version label clicked
    def version_label_clicked(self):
        webbrowser.open_new('https://github.com/bplaat/bassieracing')

    # Play button clicked
    def play_button_clicked(self):
        self.game.page = SelectMapPage(self.game)

    # Edit button clicked
    def edit_button_clicked(self):
        self.game.page = EditorPage(self.game)

     # Help button clicked
    def help_button_clicked(self):
        self.game.page = HelpPage(self.game)

    # Exit button clicked
    def exit_button_clicked(self):
        self.game.running = False

    # Footer label clicked
    def footer_label_clicked(self):
        webbrowser.open_new('https://bastiaan.ml/')

# The select map page class
class SelectMapPage(Page):
    # Create select map page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create select map page widgets
        self.widgets.append(Label('Select a map to race', 0, 24, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        self.widgets.append(Label('Comming soon...', 0, 0, Game.WIDTH, Game.HEIGHT, game.textFont, Color.WHITE))
        self.widgets.append(Button('Back', 16, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button('Continue', Game.WIDTH - 16 - 240, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.continue_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Continue button clicked
    def continue_button_clicked(self):
        self.game.page = SelectVehiclePage(self.game)

# The select vehicle page class
class SelectVehiclePage(Page):
    # Create select vehicle page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create select vehicle page widgets
        self.widgets.append(Label('Select both your vehicle', 0, 24, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        self.leftVehicleSelector = VehicleSelector(game, 16, 32 + 96 + 16, Game.WIDTH // 2 - (16 + 16), Game.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 0)
        self.widgets.append(self.leftVehicleSelector)
        self.rightVehicleSelector = VehicleSelector(game, 16 + Game.WIDTH // 2, 32 + 96 + 16, Game.WIDTH // 2 - (16 + 16), Game.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 1)
        self.widgets.append(self.rightVehicleSelector)
        self.widgets.append(Button('Back', 16, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button('Race!', Game.WIDTH - 16 - 240, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.race_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = SelectMapPage(self.game)

    # Race button clicked
    def race_button_clicked(self):
        self.game.page = GamePage(self.game, self.leftVehicleSelector.selectedVehicle, self.rightVehicleSelector.selectedVehicle)

# The game page class
class GamePage(Page):
    # Create game page
    def __init__(self, game, leftVehicleType, rightVehicleType):
        Page.__init__(self, game)

        # Init the map
        self.map = Map.load_from_file(game.tilesImage, 'map.json') # Map(game.tilesImage, 'Random Map', 40, 40)

        # Init the vehicles
        self.vehicles = []

        leftVehicle = Vehicle(game.vehiclesImage, 0, leftVehicleType, 0,
            self.map.startX * Game.TILE_SPRITE_SIZE + Game.TILE_SPRITE_SIZE / 2,
            self.map.startY * Game.TILE_SPRITE_SIZE + Game.TILE_SPRITE_SIZE / 2,
            self.map.startAngle
        )
        self.vehicles.append(leftVehicle)

        rightVehicle = Vehicle(game.vehiclesImage, 1, rightVehicleType, 1,
            self.map.startX * Game.TILE_SPRITE_SIZE + Game.TILE_SPRITE_SIZE / 2,
            self.map.startY * Game.TILE_SPRITE_SIZE + Game.TILE_SPRITE_SIZE * 1.5,
            self.map.startAngle
        )
        self.vehicles.append(rightVehicle)

        # Create game page widgets
        self.widgets.append(VehicleViewport(game, leftVehicle, 0, 0, Game.WIDTH // 2, Game.HEIGHT, self.map, self.vehicles))
        self.widgets.append(VehicleViewport(game, rightVehicle, Game.WIDTH // 2, 0, Game.WIDTH // 2, Game.HEIGHT, self.map, self.vehicles))
        self.widgets.append(Button('Back', Game.WIDTH - 16 - 128, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Update game page
    def update(self, delta):
        # Update all the vehicles
        for vehicle in self.vehicles:
            vehicle.update(delta)

# The edit page class
class EditorPage(Page):
    # Create edit page
    def __init__(self, game):
        Page.__init__(self, game)

        self.map = Map(game.tilesImage, 'Custom Map', 32, 32)

        # Create edit page widgets
        self.mapEditor = MapEditor(game, self.map, 0, 0, Game.WIDTH, Game.HEIGHT, MapEditor.ASPHALT_BRUSH)
        self.widgets.append(self.mapEditor)

        self.widgets.append(Button('New', 16, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.new_button_clicked))
        self.widgets.append(Button('Load', 16 + (128 + 16), 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.load_button_clicked))
        self.widgets.append(Button('Save', 16 + (128 + 16) * 2, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.save_button_clicked))

        self.widgets.append(Button('Back', Game.WIDTH - (16 + 128), 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

        self.sizeComboBox = ComboBox([ '%s (%dx%d)' % (Game.MAP_SIZE_LABELS[i], Game.MAP_SIZES[i], Game.MAP_SIZES[i]) for i in range(len(Game.MAP_SIZES)) ], 1, 16, Game.HEIGHT - 64 - 16, (Game.WIDTH - 16 * 3) // 2, 64, game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.size_combobox_changed)
        self.widgets.append(self.sizeComboBox)
        self.brushComboBox = ComboBox(MapEditor.TOOL_LABELS, 3, Game.WIDTH // 2 + 8, Game.HEIGHT - 64 - 16, (Game.WIDTH - 16 * 3) // 2, 64, game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.brush_combobox_changed)
        self.widgets.append(self.brushComboBox)

    # Update map editor
    def update(self, delta):
        self.mapEditor.update(delta)

    # New button clicked
    def new_button_clicked(self):
        for i in range(len(Game.MAP_SIZES)):
            if i == self.sizeComboBox.selectedItem:
                self.map = Map(self.game.tilesImage, 'Custom Map', Game.MAP_SIZES[i], Game.MAP_SIZES[i])
                self.mapEditor.set_map(self.map)
                self.mapEditor.center_camera()
                return

        # When custom size
        self.map = Map(self.game.tilesImage, 'Custom Map', 32, 32)
        self.mapEditor.set_map(self.map)
        self.mapEditor.center_camera()
        self.sizeComboBox.set_selected(1)

    # Load button clicked
    def load_button_clicked(self):
        path = tkinter.filedialog.askopenfilename(filetypes=[ ( 'JSON files', '*.json' ) ])
        if path != '':
            self.map = Map.load_from_file(self.game.tilesImage, path)
            self.mapEditor.set_map(self.map)
            self.mapEditor.center_camera()

            for i in range(len(Game.MAP_SIZES)):
                if Game.MAP_SIZES[i] == self.map.width:
                    self.sizeComboBox.set_selected(i)
                    return

            self.sizeComboBox.selectedItem = len(self.sizeComboBox.options)
            self.sizeComboBox.set_text('Custom (%dx%d) \u25BC' % (self.map.width, self.map.height))

    # Save button clicked
    def save_button_clicked(self):
        path = tkinter.filedialog.asksaveasfilename(filetypes=[ ( 'JSON files', '*.json' ) ], defaultextension='.json')
        if path != '':
            self.map.save_to_file(path)

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Size combobox changed
    def size_combobox_changed(self, selectedItem):
        for i in range(len(Game.MAP_SIZES)):
            if selectedItem == i:
                self.map.resize(Game.MAP_SIZES[i], Game.MAP_SIZES[i])
                self.mapEditor.center_camera()
                break

    # Brush combobox changed
    def brush_combobox_changed(self, selectedItem):
        for i in range(len(MapEditor.TOOL_LABELS)):
            if selectedItem == i:
                self.mapEditor.tool = i
                break

# The help page class
class HelpPage(Page):
    # Create help page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create help page widgets
        y = 64
        self.widgets.append(Label('Help', 0, y, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Label('Bassie Racing is a topdown 2D two player racing game', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the left car by using WASD keys', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the right car by using the arrow keys', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('There are multiple maps and vehicles that you can try', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can also create or edit custom maps', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 32
        self.widgets.append(Button('Back', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

# The game class
class Game:
    # Window constants
    VERSION = '0.3'
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    # Game constants
    TILE_SPRITE_SIZE = 128
    EDITOR_CAMERA_BORDER = 12
    EDITOR_TILE_SIZE = 32
    PIXELS_PER_METER = 18
    MAP_SIZES = [ 24, 32, 48, 56 ]
    MAP_SIZE_LABELS = [ 'Small', 'Medium', 'Large', 'Giant' ]

    def __init__(self):
        # Init pygame
        pygame.init()

        # Create the window
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pygame.display.set_caption('Bassie Racing')

        # Set running
        self.running = True

        # Load fonts
        self.titleFont = pygame.font.Font('PressStart2P-Regular.ttf', 48)
        self.textFont = pygame.font.Font('PressStart2P-Regular.ttf', 24)
        self.smallFont = pygame.font.Font('PressStart2P-Regular.ttf', 16)

        # Load textures
        self.tilesImage = pygame.image.load('tiles.png').convert_alpha()
        self.vehiclesImage = pygame.image.load('vehicles.png').convert_alpha()

        # Create pages
        self.page = MenuPage(self)

        # Hidden Tkinter window for file dialogs and error messages
        self.tkinter_window = tkinter.Tk()
        self.tkinter_window.withdraw()

    # Handle user events
    def handle_event(self, event):
        # Send event to current page
        self.page.handle_event(event)

        # Handle window close events
        if event.type == pygame.QUIT:
            self.running = False

    # Update the current page
    def update(self, delta):
        self.page.update(delta)

    # Draw the current page
    def draw(self):
        self.page.draw(self.screen)

    # The game loop
    def start(self):
        lastTime = time.time()
        while self.running:
            # Calculate delta time
            currentTime = time.time()
            delta = currentTime - lastTime
            lastTime = currentTime

            # Handle window events
            for event in pygame.event.get():
                self.handle_event(event)

            # Update game
            self.update(delta)

            # Draw game and flip pygame back buffer
            self.draw()
            pygame.display.flip()

            # Sleep for a short while
            time.sleep(1 / Game.FPS)

# Create a game instance and start the game
game = Game()
game.start()
