# BassieRacing - Widgets

# Import modules
from constants import *
from objects import *
import os
import pygame
import random
from stats import *

# The rect widget class
class Rect:
    # Create rect
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    # Handle rect events
    def handle_event(self, event):
        return False

    # Draw rect
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, ( self.x, self.y, self.width, self.height ))

# The label widget class
class Label:
    # Create label
    def __init__(self, text, x, y, width, height, font, color, align = TextAlign.CENTER, clickCallback = None, callbackExtra = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.align = align
        self.set_text(text)
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
        if self.align == TextAlign.LEFT:
            surface.blit(self.textSurface, (
                self.x,
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

        if self.align == TextAlign.CENTER:
            surface.blit(self.textSurface, (
                self.x + (self.width - self.textSurface.get_width()) // 2,
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

        if self.align == TextAlign.RIGHT:
            surface.blit(self.textSurface, (
                self.x + (self.width - self.textSurface.get_width()),
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

# The button widget class
class Button(Label):
    # Create button
    def __init__(self, text, x, y, width, height, font, color, backgroundColor, clickCallback = None, callbackExtra = None):
        Label.__init__(self, text, x, y, width, height, font, color, TextAlign.CENTER, clickCallback, callbackExtra)
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
        if len(options) * height > Config.HEIGHT - (y + height):
            ry = y - len(options) * height

        self.widgets = []
        for i, option in enumerate(options):
            self.widgets.append(Button(option, x, ry, width, height, font, color, backgroundColor, self.option_button_clicked, i))
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

# The image widget class
class Image:
    # Create image
    def __init__(self, image, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.set_image(image)

    # Set image image
    def set_image(self, image):
        if isinstance(image, str):
            self.surface = pygame.image.load(image).convert_alpha()
        elif isinstance(image, pygame.Surface):
            self.surface = image
        elif image == None:
            self.surface = None
        else:
            raise ValueError('Image is not a file path, a surface or None!')

    # Handle image events
    def handle_event(self, event):
        return False

    # Draw image
    def draw(self, surface):
        if self.surface != None:
            surface.blit(self.surface, (
                self.x + (self.width - self.surface.get_width()) // 2,
                self.y + (self.height - self.surface.get_height()) // 2
            ))

# The mini map widget class
class MiniMap:
    # Create mini map
    def __init__(self, game, map, vehicles, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.game = game
        self.vehicles = vehicles
        self.set_map(map)
        self.surface = pygame.Surface(( width, height ))

    # Set map
    def set_map(self, map):
        self.map = map
        self.tileSize = self.width // self.map.width
        self.vehicleScale = 0.2
        self.camera = Camera(
            (self.map.width * self.tileSize) / 2,
            (self.map.height * self.tileSize) / 2,
            self.game.tilesImage, self.tileSize,
            self.game.vehiclesImage, self.vehicleScale
        )
        if self.vehicles != None:
            for vehicle in self.vehicles:
                vehicle.crop(self.camera)

    # Handle mini map events
    def handle_event(self, event):
        return False

    # Draw mini map
    def draw(self, surface):
        # Draw background
        self.surface.fill(Color.DARK)

        # Draw the map
        self.map.draw(self.surface, self.camera)

        # Draw the vehicles if given
        if self.vehicles != None:
            # TODO
            for vehicle in self.vehicles:
                rotatedVehicleImage = pygame.transform.rotate(self.camera.vehicleImageCache[vehicle.id], math.degrees(vehicle.angle))
                x = math.floor((vehicle.x / (Config.TILE_SPRITE_SIZE / self.tileSize)) - rotatedVehicleImage.get_width() / 2 - (self.camera.x - self.width / 2))
                y = math.floor((vehicle.y / (Config.TILE_SPRITE_SIZE / self.tileSize)) - rotatedVehicleImage.get_height() / 2 - (self.camera.y - self.height / 2))
                if (
                    x + rotatedVehicleImage.get_width() >= 0 and y + rotatedVehicleImage.get_height() >= 0 and
                    x - rotatedVehicleImage.get_width() < self.width and y - rotatedVehicleImage.get_height() < self.height
                ):
                    self.surface.blit(rotatedVehicleImage, ( x, y ))

        # Draw surface
        surface.blit(self.surface, ( self.x, self.y ))

# The map selector widget
class MapSelector:
    def __init__(self, game, x, y, width, height):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.mapPaths = [ os.path.abspath('assets/maps/' + filename) for filename in os.listdir('assets/maps/') if os.path.isfile('assets/maps/' + filename) ]
        self.maps = [ Map.load_from_file(mapPath) for mapPath in self.mapPaths ]

        self.selectedMapIndex = random.randint(0, len(self.maps) - 1)
        self.update_widgets()

    # Update map selector widgets
    def update_widgets(self):
        self.selectedMap = self.maps[self.selectedMapIndex]

        self.widgets = []

        item_width = (self.width - 48 - 48) // 3
        rx = self.x + 48
        for i in range(3):
            position = (self.selectedMapIndex - 1) + i
            if position == -1:
                map = self.maps[len(self.maps) - 1]
            elif position == len(self.maps):
                map = self.maps[0]
            else:
                map = self.maps[position]

            if i == 1:
                self.widgets.append(Rect(rx, self.y, item_width, self.height, Color.WHITE))

            color = Color.BLACK if i == 1 else Color.WHITE
            self.widgets.append(MiniMap(self.game, map, None, rx + (item_width - 240) / 2, self.y + 64, 240, 240))
            self.widgets.append(Label(map.name, rx, self.y + 64 + 240 + 24, item_width, 32, self.game.textFont, color))
            self.widgets.append(Label('Size: %dx%d' % (map.width, map.height), rx, self.y + 64 + 240 + 24 + 32 + 8, item_width, 32, self.game.smallFont, color))
            rx += item_width

        self.widgets.append(Button('<', self.x, self.y, 48, self.height, self.game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button('>', self.x + self.width - 48, self.y, 48, self.height, self.game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

    # Load and add map file
    def load_map(self, file_path):
        file_path = os.path.abspath(file_path)
        # Check if map is not already pressent
        if file_path not in self.mapPaths:
            # Add and select it
            self.maps.append(Map.load_from_file(file_path))
            self.selectedMapIndex = len(self.maps) - 1
            self.update_widgets()

        # Just selected the map
        else:
            self.selectedMapIndex = self.mapPaths.index(file_path)
            self.update_widgets()

    # Handle rotate left button click
    def rotate_left_button_clicked(self):
        if self.selectedMapIndex == 0:
            self.selectedMapIndex = len(self.maps) - 1
        else:
            self.selectedMapIndex -= 1
        self.update_widgets()

    # Handle rotate right button click
    def rotate_right_button_clicked(self):
        if self.selectedMapIndex == len(self.maps) - 1:
            self.selectedMapIndex = 0
        else:
            self.selectedMapIndex += 1
        self.update_widgets()

    # Handle map selector events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw map selector
    def draw(self, surface):
        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

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

        ry = y + 32
        self.vehicleImage = Image(None, x, ry, width, 128)
        self.widgets.append(self.vehicleImage)
        ry += 128 + 32
        self.nameLabel = Label('', x, ry, width, 48, game.textFont, Color.WHITE)
        self.widgets.append(self.nameLabel)
        ry += 48 + 16
        self.maxForwardSpeed = Label('', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxForwardSpeed)
        ry += 32 + 16
        self.maxBackwardSpeed = Label('', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxBackwardSpeed)
        ry += 32 + 16
        self.turningSpeed = Label('', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.turningSpeed)

        self.widgets.append(Button('<', x, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button('>', x + width - 48, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

        self.selectedVehicleIndex = random.randint(0, len(vehicles) - 1)
        self.update_vehicle()

    # Update selected vehicle
    def update_vehicle(self):
        self.selectedVehicle = vehicles[self.selectedVehicleIndex]
        vehicleImageSurface = pygame.Surface(( self.selectedVehicle['width'], self.selectedVehicle['height'] ), pygame.SRCALPHA)
        vehicleImageSurface.blit(self.game.vehiclesImage, ( 0, 0 ),  (
            self.selectedVehicle['colors'][self.color]['x'],
            self.selectedVehicle['colors'][self.color]['y'],
            self.selectedVehicle['width'],
            self.selectedVehicle['height']
        ))
        self.vehicleImage.set_image(vehicleImageSurface)

        self.nameLabel.set_text(self.selectedVehicle['name'])
        self.maxForwardSpeed.set_text('Max Forward Speed: %d km/h' % (self.selectedVehicle['maxForwardVelocity'] / Config.PIXELS_PER_METER * 3.6))
        self.maxBackwardSpeed.set_text('Max Backward Speed: %d km/h' % (self.selectedVehicle['maxBackwardVelocity'] / Config.PIXELS_PER_METER * 3.6))
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

    # Handle vehicle selector events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw vehicle selector
    def draw(self, surface):
        # Draw widgets
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
        self.camera = Camera(self.vehicle.x, self.vehicle.y, self.game.tilesImage, Config.TILE_SPRITE_SIZE, self.game.vehiclesImage)
        for vehicle in self.vehicles:
            vehicle.crop(self.camera)

        # Create vehicle viewport widgets
        self.widgets = []
        self.speedLabel = Label('Speed: %3d km/h' % (vehicle.velocity / Config.PIXELS_PER_METER * 3.6), 24, height - 24 - 24, width - 24 - 24, 24, game.textFont, Color.BLACK, TextAlign.LEFT)
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

        # Update camera
        self.camera.x = self.vehicle.x
        self.camera.y = self.vehicle.y

        # Draw the map to surface
        self.map.draw(self.surface, self.camera)

        # Draw all the vehicles to surface
        for vehicle in self.vehicles:
            vehicle.draw(self.surface, self.camera)

        # Update speed label
        self.speedLabel.set_text('Speed: %d km/h' % (self.vehicle.velocity / Config.PIXELS_PER_METER * 3.6))

        # Draw widgets
        for widget in self.widgets:
            widget.draw(self.surface)

        # Draw own surface to the screen
        surface.blit(self.surface, ( self.x, self.y ))

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
        self.map = map
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_camera()
        self.tool = tool
        self.mouseDown = False
        self.surface = pygame.Surface(( width, height ))

    # Center camera
    def center_camera(self):
        self.camera = Camera(
            self.map.startX * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2,
            self.map.startY * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2,
            self.game.tilesImage,
            Config.EDITOR_TILE_SIZE,
            self.game.vehiclesImage
        )

    # Use tool
    def use_tool(self, mouseX, mouseY):
        tileX = math.floor((mouseX + self.camera.x - Config.WIDTH / 2) / Config.EDITOR_TILE_SIZE)
        tileY = math.floor((mouseY + self.camera.y - Config.HEIGHT / 2) / Config.EDITOR_TILE_SIZE)

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
                self.camera.movingUp = mouseY >= 2 and mouseY < Config.EDITOR_CAMERA_BORDER
                self.camera.movingDown = mouseY >= Config.HEIGHT - Config.EDITOR_CAMERA_BORDER and mouseY < Config.HEIGHT - 2
                self.camera.movingLeft = mouseX >= 2 and mouseX < Config.EDITOR_CAMERA_BORDER
                self.camera.movingRight = mouseX >= Config.WIDTH - Config.EDITOR_CAMERA_BORDER and mouseX < Config.WIDTH - 2

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
        self.surface.fill(Color.DARK)

        # Draw the map
        self.map.draw(self.surface, self.camera)

        # Draw surface
        surface.blit(self.surface, ( self.x, self.y ))
