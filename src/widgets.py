# BassieRacing - Widgets

# Import modules
from constants import *
from objects import *
import pygame
import random
from stats import *

# The widget class
class Widget:
    def __init__(self, x, y, width, height, clickCallback = None, callbackExtra = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.clickCallback = clickCallback
        self.callbackExtra = callbackExtra

    # Handle widget events
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

    # Draw widget
    def draw(self, surface):
        pass

# The label widget class
class Label(Widget):
    # Create label
    def __init__(self, text, x, y, width, height, font, color, align = TextAlign.CENTER, clickCallback = None, callbackExtra = None):
        Widget.__init__(self, x, y, width, height, clickCallback, callbackExtra)
        self.font = font
        self.color = color
        self.align = align
        self.set_text(text)

    # Update label text
    def set_text(self, text):
        self.text = text
        self.textSurface = self.font.render(self.text, True, self.color)

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

# The image widget class
class Image(Widget):
    def __init__(self, image, x, y, width, height, clickCallback = None, callbackExtra = None):
        Widget.__init__(self, x, y, width, height, clickCallback, callbackExtra)
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

    # Draw image
    def draw(self, surface):
        if self.surface != None:
            surface.blit(self.surface, (
                self.x + (self.width - self.surface.get_width()) // 2,
                self.y + (self.height - self.surface.get_height()) // 2
            ))

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
        self.speedLabel = Label('Speed: %3d km/h' % (vehicle.velocity / Config.PIXELS_PER_METER * 3.6), 0, height - 24 - 24, width, 24, game.textFont, Color.BLACK)
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
        self.speedLabel.set_text('Speed: %d km/h' % (self.vehicle.velocity / Config.PIXELS_PER_METER * 3.6))

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

    # Handle page events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw page
    def draw(self, surface):
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
        map.set_tile_size(Config.EDITOR_TILE_SIZE)

    # Center camera
    def center_camera(self):
        self.camera.x = self.map.startX * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2
        self.camera.y = self.map.startY * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2

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
        surface.fill(Color.DARK)

        # Draw the map
        self.map.draw(surface, self.camera)
