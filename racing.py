# Bassie Racing - A cool 2D topdown racing game
# Made by Bastiaan van der Plaat (https://bastiaan.ml/)
# GitHub repo: https://github.com/bplaat/bassieracing
# Made with PyGame (but only used to plot images and text to the screen and to handle the window events)
# It also uses tkinter for the file open and save dialogs
# And a noise library for random terrain generation

import noise
import math
import pygame
import time
import tkinter
import tkinter.filedialog
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
    }
]

# The colors constants class
class Color:
    BLACK = ( 0, 0, 0 )
    WHITE = ( 255, 255, 255 )

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
        x = math.floor(self.x - rotatedVehicleImage.get_width() / 2 - (camera['x'] - surface.get_width() // 2))
        y = math.floor(self.y - rotatedVehicleImage.get_height() / 2 - (camera['y'] - surface.get_height() // 2))
        if (
            x + rotatedVehicleImage.get_width() >= 0 and y + rotatedVehicleImage.get_height() >= 0 and
            x - rotatedVehicleImage.get_width() < surface.get_width() and y - rotatedVehicleImage.get_height() < surface.get_height()
        ):
            surface.blit(rotatedVehicleImage, ( x, y ))

# The map class
class Map:
    def __init__(self, tilesImage, width, height):
        self.tilesImage = tilesImage

        self.width = width
        self.height = height

        # Generate terrain
        self.terrain = [ [ 0 for x in range(width) ] for y in range(height) ]
        tx = random.randint(-10000, 10000)
        ty = random.randint(-10000, 10000)
        for y in range(height):
            for x in range(width):
                n = noise.pnoise2(x / 20 + tx, y / 20 + ty, 2)
                if n > 0.2:
                    self.terrain[y][x] = 2
                elif n > 0.075:
                    self.terrain[y][x] = 1
                else:
                    self.terrain[y][x] = 0

        self.track = [ [ 0 for x in range(width) ] for y in range(height) ]

        self.startX = width // 2
        self.startY = height // 2
        self.startAngle = math.radians(270)

        self.track[self.startY][self.startX] = 1
        self.track[self.startY + 1][self.startX] = 1

    # Draw the map
    def draw(self, surface, camera):
        # Draw terrain tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                tileType = terrainTiles[self.terrain[y][x]]
                tx = math.floor(x * Game.TILE_SPRITE_SIZE - (camera['x'] - surface.get_width() / 2))
                ty = math.floor(y *  Game.TILE_SPRITE_SIZE - (camera['y'] - surface.get_height() / 2))
                if tx + Game.TILE_SPRITE_SIZE >= 0 and ty + Game.TILE_SPRITE_SIZE >= 0 and tx < surface.get_width() and ty < surface.get_height():
                    surface.blit(
                        self.tilesImage,
                        ( tx, ty, Game.TILE_SPRITE_SIZE, Game.TILE_SPRITE_SIZE ),
                        ( tileType['x'], tileType['y'], Game.TILE_SPRITE_SIZE, Game.TILE_SPRITE_SIZE )
                    )

        # Draw track tiles to surface
        for y in range(self.height):
            for x in range(self.width):
                trackId = self.track[y][x]
                if trackId != 0:
                    tileType = trackTiles[trackId]
                    tx = math.floor(x * Game.TILE_SPRITE_SIZE - (camera['x'] - surface.get_width() / 2))
                    ty = math.floor(y *  Game.TILE_SPRITE_SIZE - (camera['y'] - surface.get_height() / 2))
                    if (
                        tx + Game.TILE_SPRITE_SIZE >= 0 and ty + Game.TILE_SPRITE_SIZE >= 0 and
                        tx < surface.get_width() and ty < surface.get_height()
                    ):
                        surface.blit(
                            self.tilesImage,
                            ( tx, ty, Game.TILE_SPRITE_SIZE, Game.TILE_SPRITE_SIZE ),
                            ( tileType['x'], tileType['y'], Game.TILE_SPRITE_SIZE, Game.TILE_SPRITE_SIZE )
                        )

# The label widget class
class Label:
    def __init__(self, text, x, y, width, height, font, color, clickCallback = None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.textSurface = font.render(text, True, color)
        self.clickCallback = clickCallback

    def set_text(self, text):
        self.text = text
        self.textSurface = self.font.render(self.text, True, self.color)

    def handleEvent(self, event):
        # Handle mouse click events
        if (
            self.clickCallback != None and
            event.type == pygame.MOUSEBUTTONUP and
            event.pos[0] >= self.x and event.pos[1] >= self.y and
            event.pos[0] < self.x + self.width and event.pos[1] < self.y + self.height
        ):
            self.clickCallback()

    def draw(self, surface):
        surface.blit(self.textSurface, (
            self.x + (self.width - self.textSurface.get_width()) // 2,
            self.y + (self.height - self.textSurface.get_height()) // 2
        ))

# The button widget class
class Button(Label):
    def __init__(self, text, x, y, width, height, font, color, backgroundColor, clickCallback = None):
        Label.__init__(self, text, x, y, width, height, font, color, clickCallback)
        self.backgroundColor = backgroundColor

    def handleEvent(self, event):
        Label.handleEvent(self, event)

    def draw(self, surface):
        pygame.draw.rect(surface, self.backgroundColor, ( self.x, self.y, self.width, self.height ))
        Label.draw(self, surface)

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
        self.speedLabel = Label('Speed: %3d km/h' % (vehicle.velocity / Game.PIXELS_PER_METER * 3.6), 0, height - 24 - 24, width, 24, game.textFont, Color.BLACK)

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface(( width, height ))

    def handleEvent(self, event):
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

    def draw(self, surface):
        # Clear the surface
        self.surface.fill(( 25, 25, 25 ))

        # Create camera object
        camera = {
            'x': self.vehicle.x,
            'y': self.vehicle.y
        }

        # Draw the map to left surfface
        self.map.draw(self.surface, camera)

        # Draw all the vehicles to left surfface
        for vehicle in self.vehicles:
            vehicle.draw(self.surface, camera)

        # Draw speed text
        self.speedLabel.set_text('Speed: %d km/h' % (self.vehicle.velocity / Game.PIXELS_PER_METER * 3.6))
        self.speedLabel.draw(self.surface)

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
        self.widgets.append(Button('<', x, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button('>', x + width - 48, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

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
    def handleEvent(self, event):
        # Send all events to the widgets
        for widget in self.widgets:
            widget.handleEvent(event)

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

# The page class
class Page:
    # Create empty page
    def __init__(self, game):
        self.game = game

        # Pick random background
        self.backgroundColor = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))

        # Create empty widgets list
        self.widgets = []

    # Handle page events
    def handleEvent(self, event):
        # Send all events to the widgets
        for widget in self.widgets:
            widget.handleEvent(event)

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
        self.widgets.append(Label('v' + Game.VERSION, Game.WIDTH - 16 - 96, 16, 96, 32, game.textFont, Color.WHITE, self.version_label_clicked))
        y = 32
        self.widgets.append(Label('Bassie Racing', 0, y, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Button('Create map to play', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.create_map_to_play_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Load map to play', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.load_map_to_play_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Create a map to edit', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.create_map_to_edit_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Load a map to edit', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.load_map_to_edit_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Help', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.help_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Exit', Game.WIDTH // 4, y, Game.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.exit_button_clicked))
        y += 64 + 16
        self.widgets.append(Label('Made by Bastiaan van der Plaat', 0, y, Game.WIDTH, 96, game.textFont, Color.WHITE, self.footer_label_clicked))

    # Version label clicked
    def version_label_clicked(self):
        webbrowser.open_new('https://github.com/bplaat/bassieracing')

    # Create map to play button
    def create_map_to_play_button_clicked(self):
        self.game.page = SelectPage(self.game)

    # Load map to play button clicked
    def load_map_to_play_button_clicked(self):
        filename = tkinter.filedialog.askopenfilename(filetypes=[ ( 'JSON files', '*.json' ) ])
        if filename != '':
            print('Open file: ' + filename)
            self.game.page = SelectPage(self.game)

    # Create map to edit button
    def create_map_to_edit_button_clicked(self):
        self.game.page = EditPage(self.game)

    # Load map to edit button clicked
    def load_map_to_edit_button_clicked(self):
        filename = tkinter.filedialog.askopenfilename(filetypes=[ ( 'JSON files', '*.json' ) ])
        if filename != '':
            print('Open file: ' + filename)
            self.game.page = EditPage(self.game)

     # Help button clicked
    def help_button_clicked(self):
        self.game.page = HelpPage(self.game)

    # Exit button clicked
    def exit_button_clicked(self):
        self.game.running = False

    # Footer label clicked
    def footer_label_clicked(self):
        webbrowser.open_new('https://bastiaan.ml/')

# The select page class
class SelectPage(Page):
    # Create select page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create select page widgets
        self.widgets.append(Label('Select both your vehicle', 0, 24, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        self.leftVehicleSelector = VehicleSelector(game, 16, 32 + 96 + 16, Game.WIDTH // 2 - (16 + 16), Game.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 0)
        self.widgets.append(self.leftVehicleSelector)
        self.rightVehicleSelector = VehicleSelector(game, 16 + Game.WIDTH // 2, 32 + 96 + 16, Game.WIDTH // 2 - (16 + 16), Game.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 1)
        self.widgets.append(self.rightVehicleSelector)
        self.widgets.append(Button('Back', 16, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button('Race!', Game.WIDTH - 16 - 240, Game.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.race_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Race button clicked
    def race_button_clicked(self):
        self.game.page = GamePage(self.game, self.leftVehicleSelector.selectedVehicle, self.rightVehicleSelector.selectedVehicle)

# The game page class
class GamePage(Page):
    # Create game page
    def __init__(self, game, leftVehicleType, rightVehicleType):
        Page.__init__(self, game)

        # Init the map
        self.map = Map(game.tilesImage, 40, 40)

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
class EditPage(Page):
    # Create edit page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create edit page widgets
        self.widgets.append(Button('Save', Game.WIDTH - (16 + 128) * 2, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.save_button_clicked))
        self.widgets.append(Button('Back', Game.WIDTH - 16 - 128, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Save button clicked
    def save_button_clicked(self):
        filename = tkinter.filedialog.asksaveasfilename(filetypes=[ ( 'JSON files', '*.json' ) ], defaultextension='.json')
        if filename != '':
            print('Save file to: ' + filename)

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

# The help page class
class HelpPage(Page):
    # Create help page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create help page widgets
        y = 64
        self.widgets.append(Label('Help', 0, y, Game.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Label('Bassie Racing is a simple two player race game', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the left car by using WASD keys', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the right car by using the arrow keys', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can also create or edit custom maps', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('And try to get better times when playing maps', 0, y, Game.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
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
    PIXELS_PER_METER = 18

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

        # Hidden Tkinter window for file dialogs
        self.tkinter_window = tkinter.Tk()
        self.tkinter_window.withdraw()

    # Handle user events
    def handleEvent(self, event):
        # Send event to current page
        self.page.handleEvent(event)

        # Handle window close events
        if event.type == pygame.QUIT:
            self.running = False

    # Update all the game objects
    def update(self, delta):
        # When on game page update objects
        if isinstance(self.page, GamePage):
            self.page.update(delta)

    # Draw all the game objects
    def draw(self):
        # Draw the current page
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
                self.handleEvent(event)

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
